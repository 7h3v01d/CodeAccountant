# gui.py

import tkinter as tk
from tkinter import ttk, messagebox
from codebuilder.cli import main as codebuilder_main
from dependency_checker_pkg.dependency_core import scan_dependencies_logic
from snapshot import create_snapshot

class CodeAccountantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CodeAccountant")
        self.project_folder = tk.StringVar(value=os.getcwd())
        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True)

        # Editor Tab
        self.editor_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.editor_frame, text="Editor")
        ttk.Button(self.editor_frame, text="Build", command=self.build).pack()
        ttk.Button(self.editor_frame, text="Run", command=self.run).pack()
        self.output_text = tk.Text(self.editor_frame, height=10)
        self.output_text.pack()

        # Dependencies Tab
        self.deps_frame = ttk.Frame(self.tabs)
        self.tabs.add(self.deps_frame, text="Dependencies")
        ttk.Button(self.deps_frame, text="Check Dependencies", command=self.check_deps).pack()

    def build(self):
        sys.argv = ["codebuilder", "build", "main.py"]  # Placeholder file
        codebuilder_main()
        self.output_text.insert(tk.END, "Build complete\n")  # Update with actual output

    def run(self):
        sys.argv = ["codebuilder", "run", "main.py"]  # Placeholder file
        codebuilder_main()
        self.output_text.insert(tk.END, "Run complete\n")  # Update with actual output

    def check_deps(self):
        missing, messages = scan_dependencies_logic(self.project_folder.get())
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "\n".join(messages))

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeAccountantGUI(root)
    root.mainloop()