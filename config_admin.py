from pathlib import Path
import json
import shutil
import tkinter as tk
from tkinter import messagebox, ttk


CONFIG_PATH = Path(__file__).resolve().with_name("areas.json")


class ListEditor:

    def __init__(self, parent, title, on_change=None):

        self.frame = ttk.LabelFrame(parent, text=title)
        self.on_change = on_change
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(
            self.frame,
            height=10,
            exportselection=False
        )
        self.listbox.grid(
            row=0,
            column=0,
            rowspan=6,
            sticky="nsew",
            padx=(8, 6),
            pady=8
        )

        scrollbar = ttk.Scrollbar(
            self.frame,
            orient="vertical",
            command=self.listbox.yview
        )
        scrollbar.grid(
            row=0,
            column=1,
            rowspan=6,
            sticky="ns",
            pady=8
        )
        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.entry = ttk.Entry(self.frame)
        self.entry.grid(
            row=0,
            column=2,
            sticky="ew",
            padx=(8, 8),
            pady=(8, 4)
        )

        self.frame.columnconfigure(2, weight=1)

        ttk.Button(
            self.frame,
            text="Add",
            command=self.add_item
        ).grid(
            row=1,
            column=2,
            sticky="ew",
            padx=(8, 8),
            pady=3
        )

        ttk.Button(
            self.frame,
            text="Remove Selected",
            command=self.remove_selected
        ).grid(
            row=2,
            column=2,
            sticky="ew",
            padx=(8, 8),
            pady=3
        )

        ttk.Button(
            self.frame,
            text="Move Up",
            command=lambda: self.move_selected(-1)
        ).grid(
            row=3,
            column=2,
            sticky="ew",
            padx=(8, 8),
            pady=3
        )

        ttk.Button(
            self.frame,
            text="Move Down",
            command=lambda: self.move_selected(1)
        ).grid(
            row=4,
            column=2,
            sticky="ew",
            padx=(8, 8),
            pady=3
        )

        ttk.Button(
            self.frame,
            text="Clear",
            command=self.clear_items
        ).grid(
            row=5,
            column=2,
            sticky="ew",
            padx=(8, 8),
            pady=(3, 8)
        )

    def set_items(self, values):

        self.listbox.delete(0, tk.END)

        for value in values:

            self.listbox.insert(tk.END, str(value))

    def get_items(self):

        return [
            self.listbox.get(index)
            for index in range(self.listbox.size())
            if self.listbox.get(index).strip()
        ]

    def add_item(self):

        value = self.entry.get().strip()

        if not value:

            return

        if value not in self.get_items():

            self.listbox.insert(tk.END, value)

        self.entry.delete(0, tk.END)
        if self.on_change:
            self.on_change()

    def remove_selected(self):

        selection = list(self.listbox.curselection())

        for index in reversed(selection):

            self.listbox.delete(index)
        if self.on_change:
            self.on_change()

    def clear_items(self):

        self.listbox.delete(0, tk.END)
        if self.on_change:
            self.on_change()

    def move_selected(self, direction):

        selection = list(self.listbox.curselection())

        if len(selection) != 1:

            return

        index = selection[0]
        new_index = index + direction

        if new_index < 0 or new_index >= self.listbox.size():

            return

        value = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(new_index, value)
        self.listbox.selection_set(new_index)
        if self.on_change:
            self.on_change()


class ConfigAdminApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Signal Garden Config Admin")
        self.root.geometry("1100x760")
        self.root.minsize(980, 700)

        self.status_var = tk.StringVar(value="Loading...")

        container = ttk.Frame(root, padding=12)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header,
            text="Signal Garden Config Admin",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header,
            text=f"Editing {CONFIG_PATH}"
        ).pack(anchor="w", pady=(2, 0))

        button_bar = ttk.Frame(container)
        button_bar.pack(fill="x", pady=(0, 10))

        ttk.Button(
            button_bar,
            text="Reload",
            command=self.reload
        ).pack(side="left")

        ttk.Button(
            button_bar,
            text="Save",
            command=self.save
        ).pack(side="left", padx=(8, 0))

        ttk.Button(
            button_bar,
            text="Open Folder",
            command=self.open_folder
        ).pack(side="left", padx=(8, 0))

        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)

        editors_frame = ttk.Frame(self.notebook, padding=8)
        editors_frame.columnconfigure(0, weight=1)
        editors_frame.rowconfigure(0, weight=1)
        editors_frame.rowconfigure(1, weight=1)
        editors_frame.rowconfigure(2, weight=1)

        self.folders_editor = ListEditor(
            editors_frame,
            "Folders",
            on_change=self.refresh_raw_preview
        )
        self.topics_editor = ListEditor(
            editors_frame,
            "Research Topics",
            on_change=self.refresh_raw_preview
        )
        self.sources_editor = ListEditor(
            editors_frame,
            "Preferred Sources",
            on_change=self.refresh_raw_preview
        )

        self.folders_editor.frame.grid(
            row=0,
            column=0,
            sticky="nsew",
            pady=(0, 10)
        )
        self.topics_editor.frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            pady=(0, 10)
        )
        self.sources_editor.frame.grid(
            row=2,
            column=0,
            sticky="nsew"
        )

        self.notebook.add(editors_frame, text="Lists")

        categories_frame = ttk.Frame(self.notebook, padding=8)
        categories_frame.columnconfigure(0, weight=1)
        categories_frame.rowconfigure(1, weight=1)

        ttk.Label(
            categories_frame,
            text="MOC Categories JSON"
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, 6)
        )

        self.moc_text = tk.Text(
            categories_frame,
            wrap="none",
            height=20,
            undo=True
        )
        self.moc_text.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        moc_scroll_y = ttk.Scrollbar(
            categories_frame,
            orient="vertical",
            command=self.moc_text.yview
        )
        moc_scroll_y.grid(
            row=1,
            column=1,
            sticky="ns"
        )
        self.moc_text.configure(yscrollcommand=moc_scroll_y.set)

        moc_scroll_x = ttk.Scrollbar(
            categories_frame,
            orient="horizontal",
            command=self.moc_text.xview
        )
        moc_scroll_x.grid(
            row=2,
            column=0,
            sticky="ew"
        )
        self.moc_text.configure(xscrollcommand=moc_scroll_x.set)

        ttk.Label(
            categories_frame,
            text=(
                "Edit the category map as JSON. "
                "Save validates the structure before writing."
            )
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(8, 0)
        )

        self.notebook.add(categories_frame, text="MOC Categories")

        raw_frame = ttk.Frame(self.notebook, padding=8)
        raw_frame.columnconfigure(0, weight=1)
        raw_frame.rowconfigure(1, weight=1)

        ttk.Label(
            raw_frame,
            text="Raw JSON Preview"
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.raw_text = tk.Text(
            raw_frame,
            wrap="none",
            height=20
        )
        self.raw_text.grid(row=1, column=0, sticky="nsew")

        self.notebook.add(raw_frame, text="Raw JSON")

        status_bar = ttk.Label(
            container,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            padding=(8, 4)
        )
        status_bar.pack(fill="x", pady=(10, 0))

        self.config = {}
        self.reload()

    def open_folder(self):

        try:

            import os

            os.startfile(CONFIG_PATH.parent)

        except Exception as exc:

            messagebox.showerror("Open Folder Failed", str(exc))

    def load_config(self):

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:

            return json.load(f)

    def populate(self, config):

        self.config = config

        self.folders_editor.set_items(config.get("folders", []))
        self.topics_editor.set_items(config.get("research_topics", []))
        self.sources_editor.set_items(config.get("preferred_sources", []))

        moc_categories = config.get("moc_categories", {})

        self.moc_text.delete("1.0", tk.END)
        self.moc_text.insert(
            tk.END,
            json.dumps(
                moc_categories,
                indent=4,
                ensure_ascii=False
            )
        )

        self.refresh_raw_preview()

    def refresh_raw_preview(self):

        preview = {
            "folders": self.folders_editor.get_items(),
            "research_topics": self.topics_editor.get_items(),
            "preferred_sources": self.sources_editor.get_items(),
            "moc_categories": self.safe_parse_moc_categories()
        }

        self.raw_text.delete("1.0", tk.END)
        self.raw_text.insert(
            tk.END,
            json.dumps(preview, indent=2, ensure_ascii=False)
        )

    def safe_parse_moc_categories(self):

        raw = self.moc_text.get("1.0", tk.END).strip()

        if not raw:

            return {}

        parsed = json.loads(raw)

        if not isinstance(parsed, dict):

            raise ValueError("moc_categories must be a JSON object")

        return parsed

    def reload(self):

        try:

            config = self.load_config()
            self.populate(config)
            self.status_var.set(f"Loaded {CONFIG_PATH}")

        except Exception as exc:

            messagebox.showerror("Load Failed", str(exc))
            self.status_var.set("Load failed")

    def validate_config(self):

        config = {
            "folders": self.folders_editor.get_items(),
            "research_topics": self.topics_editor.get_items(),
            "preferred_sources": self.sources_editor.get_items(),
            "moc_categories": self.safe_parse_moc_categories()
        }

        required_keys = {
            "folders",
            "research_topics",
            "preferred_sources",
            "moc_categories"
        }

        missing = required_keys - set(config.keys())

        if missing:

            raise ValueError(f"Missing keys: {', '.join(sorted(missing))}")

        return config

    def save(self):

        try:

            config = self.validate_config()

            backup_path = CONFIG_PATH.with_suffix(".bak")

            if CONFIG_PATH.exists():

                shutil.copy2(CONFIG_PATH, backup_path)

            with open(CONFIG_PATH, "w", encoding="utf-8") as f:

                json.dump(
                    config,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            self.populate(config)
            self.status_var.set(f"Saved {CONFIG_PATH}")
            messagebox.showinfo("Saved", f"Configuration saved to {CONFIG_PATH}")

        except Exception as exc:

            messagebox.showerror("Save Failed", str(exc))
            self.status_var.set("Save failed")


def main():

    root = tk.Tk()
    app = ConfigAdminApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
