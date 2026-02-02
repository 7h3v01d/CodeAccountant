# codebuilder/utils/detector.py
import os

def detect_language(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    language_map = {
        '.py': 'python',
        '.c': 'c',
        '.cpp': 'cpp',
        '.cs': 'csharp',
        '.java': 'java',
        '.rs': 'rust',
        '.go': 'go'
    }
    return language_map.get(ext, None)