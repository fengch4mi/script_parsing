import subprocess
import sys
from pathlib import Path
from tkinter import Tk, StringVar
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

from scrap import find_quotes, _default_output_filename, _unique_path

DEFAULT_MODEL = "gemini-2.5-flash"

class QuoteFinderTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=12)
        self.file_var = StringVar()
        self.character_var = StringVar()
        self.mode_var = StringVar(value="line")
        self.status_var = StringVar(value="Ready.")
        self.results = []

        self._build_layout()

    def _build_layout(self):
        container = self.frame
        container.columnconfigure(1, weight=1)
        container.rowconfigure(4, weight=1)

        ttk.Label(container, text="Script file:").grid(row=0, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.file_var).grid(
            row=0, column=1, sticky="ew", padx=(8, 8)
        )
        ttk.Button(container, text="Browse...", command=self.browse_file).grid(
            row=0, column=2, sticky="ew"
        )

        ttk.Label(container, text="Character name:").grid(row=1, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.character_var).grid(
            row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(8, 0)
        )

        mode_frame = ttk.LabelFrame(container, text="Search mode")
        mode_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 6))
        ttk.Radiobutton(
            mode_frame, text="Line", value="line", variable=self.mode_var
        ).grid(row=0, column=0, padx=8, pady=6, sticky="w")
        ttk.Radiobutton(
            mode_frame, text="Paragraph", value="paragraph", variable=self.mode_var
        ).grid(row=0, column=1, padx=8, pady=6, sticky="w")
        ttk.Radiobutton(
            mode_frame, text="Dialogue", value="dialogue", variable=self.mode_var
        ).grid(row=0, column=2, padx=8, pady=6, sticky="w")

        actions = ttk.Frame(container)
        actions.grid(row=3, column=0, columnspan=3, sticky="w", pady=(6, 6))
        ttk.Button(actions, text="Run", command=self.run_search).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(actions, text="Save Results", command=self.save_results).grid(
            row=0, column=1, padx=(0, 8)
        )
        ttk.Button(actions, text="Clear", command=self.clear_results).grid(
            row=0, column=2
        )

        self.results_text = ScrolledText(container, wrap="word", height=18)
        self.results_text.grid(
            row=4, column=0, columnspan=3, sticky="nsew", pady=(6, 6)
        )
        self.results_text.configure(state="disabled")

        ttk.Label(container, textvariable=self.status_var).grid(
            row=5, column=0, columnspan=3, sticky="w"
        )

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select script file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self.file_var.set(path)

    def run_search(self):
        file_path = self.file_var.get().strip().strip('"')
        character_name = self.character_var.get().strip()
        mode = self.mode_var.get()

        if not file_path:
            messagebox.showwarning("Missing file", "Please choose a script file.")
            return
        if not Path(file_path).is_file():
            messagebox.showwarning("File not found", "The selected file does not exist.")
            return
        if not character_name:
            messagebox.showwarning("Missing name", "Please enter a character name.")
            return

        try:
            self.results = find_quotes(file_path, character_name, mode)
        except Exception as exc:
            messagebox.showerror("Search error", f"Failed to parse file:\n{exc}")
            return

        self._render_results()

    def _render_results(self):
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")

        if not self.results:
            self.results_text.insert("end", "No results found.")
            self.status_var.set("No results.")
        else:
            for result in self.results:
                self.results_text.insert("end", result["text"] + "\n")
                self.results_text.insert("end", "-" * 60 + "\n")
            self.status_var.set(f"Found {len(self.results)} results.")

        self.results_text.configure(state="disabled")

    def save_results(self):
        if not self.results:
            messagebox.showinfo("No results", "Run a search before saving results.")
            return

        file_path = self.file_var.get().strip().strip('"')
        character_name = self.character_var.get().strip() or "character"
        default_output = _default_output_filename(file_path, character_name)
        default_path = _unique_path(Path(default_output))

        initial_dir = Path(file_path).parent if file_path else Path.cwd()
        save_path = filedialog.asksaveasfilename(
            title="Save results",
            defaultextension=".txt",
            initialdir=str(initial_dir),
            initialfile=default_path.name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not save_path:
            return

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                for result in self.results:
                    f.write(result["text"] + "\n\n")
                    f.write("-" * 60 + "\n\n")
        except Exception as exc:
            messagebox.showerror("Save error", f"Failed to save file:\n{exc}")
            return

        self.status_var.set(f"Saved to {Path(save_path).name}.")

    def clear_results(self):
        self.results = []
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.configure(state="disabled")
        self.status_var.set("Ready.")

class AnalysisTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, padding=12)
        self.api_key_var = StringVar()
        self.model_var = StringVar(value=DEFAULT_MODEL)
        self.character_var = StringVar()
        self.file_var = StringVar()
        self.status_var = StringVar(value="Ready.")
        self.result_text = ""

        self._build_layout()

    def _build_layout(self):
        container = self.frame
        container.columnconfigure(1, weight=1)
        container.rowconfigure(6, weight=1)

        ttk.Label(container, text="API key:").grid(row=0, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.api_key_var, show="*").grid(
            row=0, column=1, columnspan=2, sticky="ew", padx=(8, 0)
        )

        ttk.Label(container, text="Model:").grid(row=1, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.model_var).grid(
            row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(8, 0)
        )

        ttk.Label(container, text="Character name:").grid(row=2, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.character_var).grid(
            row=2, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(8, 0)
        )

        ttk.Label(container, text="Quotes file:").grid(row=3, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.file_var).grid(
            row=3, column=1, sticky="ew", padx=(8, 8), pady=(8, 0)
        )
        ttk.Button(container, text="Browse...", command=self.browse_file).grid(
            row=3, column=2, sticky="ew", pady=(8, 0)
        )

        actions = ttk.Frame(container)
        actions.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 6))
        ttk.Button(actions, text="Analyze", command=self.run_analysis).grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(actions, text="Save Output", command=self.save_output).grid(
            row=0, column=1, padx=(0, 8)
        )
        ttk.Button(actions, text="Clear", command=self.clear_output).grid(
            row=0, column=2
        )

        self.output_box = ScrolledText(container, wrap="word", height=20)
        self.output_box.grid(
            row=6, column=0, columnspan=3, sticky="nsew", pady=(6, 6)
        )
        self.output_box.configure(state="disabled")

        ttk.Label(container, textvariable=self.status_var).grid(
            row=7, column=0, columnspan=3, sticky="w"
        )

    def browse_file(self):
        path = filedialog.askopenfilename(
            title="Select quotes file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            self.file_var.set(path)

    def _ensure_dependency(self):
        try:
            import google.generativeai  # noqa: F401
            return True
        except Exception:
            install = messagebox.askyesno(
                "Install dependency",
                "google-generativeai is not installed. Install it now?",
            )
            if not install:
                return False

            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "google-generativeai"]
                )
                return True
            except Exception as exc:
                messagebox.showerror(
                    "Install failed",
                    f"Failed to install google-generativeai:\n{exc}",
                )
                return False

    def _load_analyzer(self):
        if not self._ensure_dependency():
            return None

        try:
            from chara_analysis import GeminiAnalyzer
        except Exception as exc:
            messagebox.showerror("Import error", f"Failed to load analyzer:\n{exc}")
            return None

        return GeminiAnalyzer

    def run_analysis(self):
        api_key = self.api_key_var.get().strip()
        model = self.model_var.get().strip() or DEFAULT_MODEL
        character = self.character_var.get().strip()
        quotes_file = self.file_var.get().strip().strip('"')

        if not api_key:
            messagebox.showwarning("Missing API key", "Please enter your API key.")
            return
        if not model:
            messagebox.showwarning("Missing model", "Please enter a model name.")
            return
        if not character:
            messagebox.showwarning("Missing name", "Please enter a character name.")
            return
        if not quotes_file:
            messagebox.showwarning("Missing file", "Please choose a quotes file.")
            return

        path = Path(quotes_file)
        if path.suffix.lower() != ".txt":
            messagebox.showwarning("Invalid file", "Quotes file must be a .txt file.")
            return
        if not path.is_file():
            messagebox.showwarning("File not found", "The selected file does not exist.")
            return

        analyzer_class = self._load_analyzer()
        if not analyzer_class:
            return

        try:
            analyzer = analyzer_class(api_key, model)
            result = analyzer.analyze_character(character, path)
        except Exception as exc:
            messagebox.showerror("Analysis error", f"Failed to analyze:\n{exc}")
            return

        self.result_text = result
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("end", result)
        self.output_box.configure(state="disabled")
        self.status_var.set("Analysis complete.")

    def save_output(self):
        if not self.result_text:
            messagebox.showinfo("No output", "Run an analysis before saving.")
            return

        character = self.character_var.get().strip() or "character"
        quotes_file = self.file_var.get().strip().strip('"')
        initial_dir = Path(quotes_file).parent if quotes_file else Path.cwd()
        default_name = f"{character}_gemini_analysis.txt"

        save_path = filedialog.asksaveasfilename(
            title="Save analysis",
            defaultextension=".txt",
            initialdir=str(initial_dir),
            initialfile=default_name,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not save_path:
            return

        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(self.result_text)
        except Exception as exc:
            messagebox.showerror("Save error", f"Failed to save file:\n{exc}")
            return

        self.status_var.set(f"Saved to {Path(save_path).name}.")

    def clear_output(self):
        self.result_text = ""
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.configure(state="disabled")
        self.status_var.set("Ready.")

class App:
    def __init__(self):
        self.root = Tk()
        self.root.title("Script Tools")
        self.root.geometry("1000x700")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        self.quote_tab = QuoteFinderTab(notebook)
        notebook.add(self.quote_tab.frame, text="Quote Finder")

        self.analysis_tab = AnalysisTab(notebook)
        notebook.add(self.analysis_tab.frame, text="Character Analysis")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()