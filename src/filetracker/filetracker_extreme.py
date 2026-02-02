import os
import re
import threading
import time
import hashlib
import mimetypes
import traceback
from concurrent.futures import ThreadPoolExecutor
from rapidfuzz import fuzz
from typing import List, Dict, Any, Optional, Callable, Tuple, Set, Union

from collections import namedtuple
FileMatchResult = namedtuple("FileMatchResult", ["name", "raw_path", "size_bytes", "mtime", "mime_type", "content_type"])

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    Image = None

try:
    import mutagen
except ImportError:
    mutagen = None

class FileTracker:
    DEFAULT_FUZZY_MATCH_THRESHOLD = 80
    DEFAULT_BATCH_SIZE = 100

    def __init__(self, max_workers: Optional[int] = None):
        self.files_data: List[Dict[str, Any]] = []
        self.stop_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=max_workers or os.cpu_count() or 4)
        self.cache: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
        self.excluded_extensions = {'.log', '.tmp'}

    def _calculate_hash(self, path: str, algo: str) -> str:
        h = hashlib.new(algo)
        try:
            with open(path, 'rb') as f:
                while chunk := f.read(4096):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return 'error'

    def _extract_exif(self, path: str) -> Dict[str, Any]:
        if not Image:
            return {}
        try:
            img = Image.open(path)
            info = img._getexif() or {}
            return {TAGS.get(k, str(k)): str(v) for k, v in info.items()}
        except Exception:
            return {}

    def _extract_media_metadata(self, path: str) -> Dict[str, Any]:
        if not mutagen:
            return {}
        try:
            audio = mutagen.File(path)
            return dict(audio.info.pprint().split(": ", 1)) if audio and hasattr(audio, 'info') else {}
        except Exception:
            return {}

    def _extract_filesystem_metadata(self, path: str) -> Dict[str, Any]:
        try:
            stat = os.stat(path)
            return {
                "owner": stat.st_uid if hasattr(stat, 'st_uid') else None,
                "permissions": oct(stat.st_mode)[-3:]
            }
        except Exception:
            return {}

    def _get_metadata(self, path: str, mime_type: str) -> Dict[str, Any]:
        metadata = {}
        if mime_type.startswith("image/"):
            metadata.update(self._extract_exif(path))
        if mime_type.startswith(("video/", "audio/")):
            metadata.update(self._extract_media_metadata(path))
        metadata.update(self._extract_filesystem_metadata(path))
        return metadata

    def scan_files(self, search_location: str, fields: List[str], hash_algo: Optional[str] = None,
                   extract_metadata: bool = False) -> List[Dict[str, Any]]:
        results = []
        for root, _, files in os.walk(search_location):
            for name in files:
                if self.stop_event.is_set():
                    return results
                if os.path.splitext(name)[1].lower() in self.excluded_extensions:
                    continue
                path = os.path.join(root, name)
                try:
                    stat = os.stat(path)
                    mime = mimetypes.guess_type(path)[0] or 'unknown'
                    item = {
                        "name": name,
                        "raw_path": path,
                        "size_bytes": stat.st_size,
                        "mtime": stat.st_mtime,
                        "mime_type": mime,
                        "content_type": self._classify_file(name)
                    }
                    if hash_algo:
                        item["hash"] = self._calculate_hash(path, hash_algo)
                    if extract_metadata:
                        item.update(self._get_metadata(path, mime))
                    results.append(item)
                except Exception:
                    continue
        return results

    def search_files(self, search_term: str, search_location: str, selected_type: str = "All",
                     exact_match_mode: bool = False, use_regex: bool = False,
                     size_range: Optional[Tuple[int, int]] = None,
                     date_range: Optional[Tuple[float, float]] = None,
                     sort_by: str = "name", sort_order: str = "asc",
                     max_files: Optional[int] = None, max_time: Optional[int] = None,
                     hash_algo: Optional[str] = None, extract_metadata: bool = False) -> List[Dict[str, Any]]:

        files = self.scan_files(search_location, fields=[], hash_algo=hash_algo, extract_metadata=extract_metadata)

        results = []
        regex = None
        if use_regex:
            try:
                regex = re.compile(search_term, re.IGNORECASE)
            except re.error:
                return []

        for f in files:
            if self.stop_event.is_set():
                break

            name = f['name']
            if selected_type != "All" and f["content_type"] != selected_type:
                continue
            if size_range and not (size_range[0] <= f["size_bytes"] <= size_range[1]):
                continue
            if date_range and not (date_range[0] <= f["mtime"] <= date_range[1]):
                continue
            if use_regex and not regex.search(name):
                continue
            if exact_match_mode:
                if search_term.lower() not in [name.lower(), os.path.splitext(name)[0].lower()]:
                    continue
            else:
                score = fuzz.partial_ratio(search_term.lower(), name.lower())
                if score < 80:
                    continue
            results.append(f)

        results.sort(key=lambda x: x.get(sort_by, ''), reverse=(sort_order == 'desc'))
        return results

    def _classify_file(self, name: str) -> str:
        name = name.lower()
        if re.search(r'\.(mp4|mkv|avi)$', name):
            if re.search(r'(s\d{1,2}e\d{1,2}|season\s*\d+)', name):
                return "TV Show"
            return "Movie"
        return "Other"