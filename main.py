import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from data_module import DataModule
from create_module import create_session
from update_module import update_session
from delete_module import delete_session
from readandsearch_module import fetch_all_sessions, search_sessions_by_name


class FairAirActivity5:
    """Fully wired Activity 5 UI that drives SQLite CRUD operations."""
    def __init__(self, root):
        """Initialize window, shared state, and seed the table contents."""
        self.root = root
        self.root.title("Fair Air – AC Sharing Log (Activity 5)")
        self.root.geometry("1920x1080")
        try:
            self.root.state('zoomed')
        except tk.TclError:
            self.root.attributes('-fullscreen', True)
            self.root.bind('<Escape>', lambda e: self.root.attributes('-fullscreen', False))

        self.colors = {
            'bg': '#B2ECE1',
            'secondary': '#8CDEDC',
            'accent1': '#BA274A',
            'accent2': '#2191FB',
            'accent3': '#841C26'
        }

        self.data_module = DataModule()
        self.data_module.connect()  # Open SQLite connection once so all CRUD helpers share it.

        self.name_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.duration_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.selected_session_id = None
        self.current_rows = []

        self._set_default_date()

        self.root.configure(bg=self.colors['bg'])
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)  # Ensure DB closes when the X button is used.

        self.build_layout()
        self._load_sessions()

    def build_layout(self):
        """Assemble the full GUI: inputs, actions, filters, table, summary."""
        title_frame = tk.Frame(self.root, bg=self.colors['accent2'], height=100)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)

        # Main heading label keeps the window branded per the wireframe.
        tk.Label(
            title_frame,
            text="Fair Air – AC Sharing Log",
            font=('Arial', 24, 'bold'),
            bg=self.colors['accent2'],
            fg='white'
        ).place(relx=0.5, rely=0.35, anchor='center')

        # Subtitle label explains the SDG context directly under the title.
        tk.Label(
            title_frame,
            text="Track fan/AC usage for fair energy consumption • Supporting SDG 7",
            font=('Arial', 10),
            bg=self.colors['accent2'],
            fg='white'
        ).place(relx=0.5, rely=0.7, anchor='center')

        main_container = tk.Frame(self.root, bg=self.colors['bg'])  # Holds left form + right data panels side-by-side.
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Left column mirrors the wireframe: inputs + action buttons.
        left_panel = tk.Frame(main_container, bg=self.colors['secondary'], relief='groove', borderwidth=2)
        left_panel.pack(side='left', fill='both', padx=(0, 10), pady=5)

        # Section header label clarifies the purpose of the form panel.
        tk.Label(
            left_panel,
            text="Log Usage Session",
            font=('Arial', 14, 'bold'),
            bg=self.colors['secondary']
        ).pack(pady=15)

        self.name_entry = self._add_labeled_entry(left_panel, "Name:", self.name_var)
        self.date_entry = self._add_labeled_entry(left_panel, "Date (YYYY-MM-DD):", self.date_var)
        self.duration_entry = self._add_labeled_entry(left_panel, "Duration (minutes):", self.duration_var)

        button_frame = tk.Frame(left_panel, bg=self.colors['secondary'])
        button_frame.pack(pady=10)

        # Create button fires an INSERT into SQLite.
        tk.Button(
            button_frame,
            text="Create",
            font=('Arial', 11, 'bold'),
            bg=self.colors['accent2'],
            fg='white',
            width=12,
            command=self._handle_create
        ).grid(row=0, column=0, padx=5, pady=5)  # Top-left button handles inserts.

        # Update button writes changes back to the selected record.
        tk.Button(
            button_frame,
            text="Update",
            font=('Arial', 11, 'bold'),
            bg=self.colors['accent1'],
            fg='white',
            width=12,
            command=self._handle_update
        ).grid(row=0, column=1, padx=5, pady=5)

        # Delete button removes the highlighted session once confirmed.
        tk.Button(
            button_frame,
            text="Delete",
            font=('Arial', 11, 'bold'),
            bg=self.colors['accent3'],
            fg='white',
            width=12,
            command=self._handle_delete
        ).grid(row=1, column=0, padx=5, pady=5)

        # Clear Form button resets the inputs for the next entry.
        tk.Button(
            button_frame,
            text="Clear Form",
            font=('Arial', 11, 'bold'),
            bg=self.colors['accent2'],
            fg='white',
            width=12,
            command=self._clear_form
        ).grid(row=1, column=1, padx=5, pady=5)

        right_panel = tk.Frame(main_container, bg=self.colors['bg'])  # Hosts search, table, and summary widgets.
        right_panel.pack(side='right', fill='both', expand=True)

        filter_frame = tk.Frame(right_panel, bg=self.colors['bg'], relief='ridge', borderwidth=1)
        filter_frame.pack(fill='x', pady=(0, 10))

        # Label for the search box so users know the filter key.
        tk.Label(
            filter_frame,
            text="Search Name:",
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg']
        ).grid(row=0, column=0, padx=5, pady=5, sticky='w')

        # Entry where the user types a name keyword.
        search_entry = tk.Entry(filter_frame, font=('Arial', 10), width=25, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, padx=5, pady=5)
        search_entry.bind('<Return>', lambda _event: self._handle_search())  # Allow Enter key to run search.

        # Search button executes the LIKE query.
        tk.Button(
            filter_frame,
            text="Search",
            font=('Arial', 10, 'bold'),
            bg=self.colors['accent2'],
            fg='white',
            command=self._handle_search
        ).grid(row=0, column=2, padx=5, pady=5)

        # Reset button quickly restores the full dataset view.
        tk.Button(
            filter_frame,
            text="Reset",
            font=('Arial', 10, 'bold'),
            bg=self.colors['accent1'],
            fg='white',
            command=lambda: (self.search_var.set(''), self._load_sessions())
        ).grid(row=0, column=3, padx=5, pady=5)  # Quick way to clear search filter and reload DB rows.

        sort_frame = tk.Frame(right_panel, bg=self.colors['bg'])
        sort_frame.pack(fill='x', pady=(0, 10))

        # Sort label anchors the buttons that change ordering.
        tk.Label(
            sort_frame,
            text="Sort Sessions:",
            font=('Arial', 10, 'bold'),
            bg=self.colors['bg']
        ).pack(side='left', padx=(0, 10))

        # Sorting by recent re-fetches rows using the default ORDER BY id DESC.
        tk.Button(
            sort_frame,
            text="Sort by Recent",
            font=('Arial', 10, 'bold'),
            bg=self.colors['accent2'],
            fg='white',
            command=self._load_sessions
        ).pack(side='left', padx=5)

        # Sorting by name reuses cached rows and sorts client-side.
        tk.Button(
            sort_frame,
            text="Sort by Name",
            font=('Arial', 10, 'bold'),
            bg=self.colors['accent2'],
            fg='white',
            command=self._sort_by_name
        ).pack(side='left', padx=5)

        table_frame = tk.Frame(right_panel, bg=self.colors['bg'])
        table_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Label above the table clarifies what the grid represents.
        tk.Label(
            table_frame,
            text="Usage Sessions",
            font=('Arial', 12, 'bold'),
            bg=self.colors['bg']
        ).pack(anchor='w', pady=(0, 5))

        columns = ('ID', 'Name', 'Date', 'Duration (min)')  # Define all grid columns in display order.
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)  # Treeview shows data rows.
        for col in columns:  # Apply consistent heading/column config per column name.
            self.tree.heading(col, text=col)  # Human-readable heading text.
            if col == 'ID':  # Narrow column for the identifier and center it.
                self.tree.column(col, width=50, anchor='center')
            elif col == 'Duration (min)':  # Wider numeric column for duration values.
                self.tree.column(col, width=120, anchor='center')
            else:  # Name and Date stay wider and left-aligned.
                self.tree.column(col, width=160, anchor='w')
        self.tree.pack(fill='both', expand=True)  # Let the table stretch with the parent frame.
        self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)  # Keep form fields synced with the selected row.

        summary_frame = tk.Frame(right_panel, bg=self.colors['accent1'], relief='raised', borderwidth=2)
        summary_frame.pack(fill='x', pady=10)

        # Summary title label sets the context for the totals card.
        tk.Label(
            summary_frame,
            text="Usage Summary by Person",
            font=('Arial', 12, 'bold'),
            bg=self.colors['accent1'],
            fg='white'
        ).pack(pady=10)

        self.summary_text = tk.Text(
            summary_frame,
            height=6,
            font=('Courier', 10),
            bg='white',
            relief='solid',
            borderwidth=1,
            state='disabled'
        )
        self.summary_text.pack(padx=10, pady=(0, 10), fill='x')  # Always display even if no data is present yet.

    def _add_labeled_entry(self, parent, label, text_variable):
        """Render a labeled entry field bound to a StringVar."""
        tk.Label(parent, text=label, font=('Arial', 11), bg=self.colors['secondary']).pack(anchor='w', padx=20)
        entry = tk.Entry(parent, font=('Arial', 11), width=25, bg='white', textvariable=text_variable)
        entry.pack(padx=20, pady=(0, 15))
        return entry

    def _handle_create(self):
        """Persist a new session after validating the form."""
        name, date, duration = self._gather_form_values()
        if not self._validate_inputs(name, date, duration):
            return
        create_session(self.data_module, name, date, int(duration))  # Persist only after passing validation.
        messagebox.showinfo("Created", "Session saved successfully.")
        self._clear_form(reset_search=False)
        self._load_sessions()

    def _handle_update(self):
        """Apply edits to the selected row when inputs check out."""
        if self.selected_session_id is None:
            messagebox.showwarning("Select Row", "Choose a session to update.")
            return
        name, date, duration = self._gather_form_values()
        if not self._validate_inputs(name, date, duration):
            return
        update_session(self.data_module, self.selected_session_id, name, date, int(duration))
        messagebox.showinfo("Updated", "Session updated successfully.")
        self._clear_form(reset_search=False)
        self._load_sessions()

    def _handle_delete(self):
        """Remove the highlighted record after confirmation."""
        if self.selected_session_id is None:
            messagebox.showwarning("Select Row", "Choose a session to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Delete the selected session?"):
            delete_session(self.data_module, self.selected_session_id)
            messagebox.showinfo("Deleted", "Session removed.")
            self._clear_form(reset_search=False)
            self._load_sessions()

    def _handle_search(self):
        """Filter rows by name keyword using the search helper."""
        keyword = self.search_var.get().strip()
        if not keyword:
            self._load_sessions()  # Empty search box just reloads all rows.
            return
        rows = search_sessions_by_name(self.data_module, keyword)
        self._populate_tree(rows)
        self._update_summary(rows)

    def _sort_by_name(self):
        """Sort cached data alphabetically without extra SQL hits."""
        rows = fetch_all_sessions(self.data_module)
        rows.sort(key=lambda row: (row[1].lower(), -row[0]))
        self._populate_tree(rows)
        self._update_summary(rows)

    def _load_sessions(self):
        """Refresh the Treeview with the latest database contents."""
        rows = fetch_all_sessions(self.data_module)
        self._populate_tree(rows)
        self._update_summary(rows)

    def _populate_tree(self, rows):
        """Replace the Treeview rows with the provided dataset."""
        self.current_rows = rows  # cache rows so future sorts/filters can reuse them.
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def _update_summary(self, rows):
        """Summarize duration totals per name and show them in the card."""
        totals = {}
        for _id, name, _date, duration in rows:
            totals.setdefault(name, 0)
            totals[name] += duration
        summary_lines = ["No data available." if not totals else ""]
        if totals:
            summary_lines = [
                f"{name:<15} {minutes:>5} min"
                for name, minutes in sorted(totals.items(), key=lambda item: (-item[1], item[0].lower()))
            ]
        self.summary_text.configure(state='normal')
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', "\n".join(summary_lines))
        self.summary_text.configure(state='disabled')

    def _gather_form_values(self):
        """Return trimmed strings from the form inputs."""
        name_normalized = self._normalize_name(self.name_var.get())  # keep consistent casing for comparisons.
        self.name_var.set(name_normalized)
        return (
            name_normalized,
            self.date_var.get().strip(),
            self.duration_var.get().strip()
        )

    def _validate_inputs(self, name, date, duration):
        """Guard against empty fields or invalid duration data."""
        if not name or not date or not duration:
            messagebox.showerror("Missing Data", "All fields are required.")
            return False
        if not duration.isdigit() or int(duration) <= 0:
            messagebox.showerror("Invalid Duration", "Duration must be a positive integer.")
            return False
        return True

    def _clear_form(self, reset_search=True):
        """Reset form fields and optionally wipe any active search filter."""
        self.name_var.set('')
        self._set_default_date()
        self.duration_var.set('')
        self.selected_session_id = None
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        if reset_search:
            self.search_var.set('')  # Optional flag used to keep search terms after CRUD actions.

    def _set_default_date(self):
        """Populate the date field with today's ISO stamp."""
        self.date_var.set(date.today().isoformat())

    def _normalize_name(self, value):
        """Normalize name entry for case-insensitive handling."""
        return value.strip().title()

    def _on_tree_select(self, _event):
        """Sync the selected table row back to the form fields."""
        selected = self.tree.selection()  # Returns tuple of selected item IDs.
        if not selected:
            return
        values = self.tree.item(selected[0], 'values')
        session_id, name, date, duration = values
        self.selected_session_id = int(session_id)
        self.name_var.set(name)
        self.date_var.set(date)
        self.duration_var.set(duration)

    def _on_close(self):
        """Tear down the DB connection before quitting Tkinter."""
        self.data_module.close()
        self.root.destroy()


def main():
    """Bootstrap the Activity 5 window."""
    root = tk.Tk()
    FairAirActivity5(root)
    root.mainloop()


if __name__ == '__main__':
    main()
