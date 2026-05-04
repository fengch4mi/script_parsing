from pathlib import Path
from tkinter import Tk, StringVar
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

from scrap import find_quotes, _default_output_filename, _unique_path

class UI:
    def __init__(self):
        self.root = Tk()
        self.root.title("Character Quote Finder")
        self.root.geometry("900x600")

        self.file_var = StringVar()
        self.character_var = StringVar()
        self.mode_var = StringVar(value="line")
        self.status_var = StringVar(value="Ready.")
        self.results = []

        self._build_layout()

    def _build_layout(self):
        container = ttk.Frame(self.root, padding=12)
        container.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(4, weight=1)

        ttk.Label(container, text="Script file:").grid(row=0, column=0, sticky="w")
        file_entry = ttk.Entry(container, textvariable=self.file_var)
        file_entry.grid(row=0, column=1, sticky="ew", padx=(8, 8))
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
        self.results_text.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(6, 6))
        self.results_text.configure(state="disabled")

        status = ttk.Label(container, textvariable=self.status_var)
        status.grid(row=5, column=0, columnspan=3, sticky="w")

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

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = UI()
    app.run()