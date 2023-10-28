import sqlite3
import tkinter as tk

from tkinter import ttk


class DataBaseView:
    """Сlass that creates a tab for viewing a database in the form of a table"""

    def __init__(
        self,
        tab_control: ttk.Notebook,
    ) -> None:
        self.db_tab = self.add_tab(tab_control=tab_control)
        self.treeview = None

    def tab_render(
        self,
    ) -> None:
        conn = sqlite3.connect("youtube.db")
        cursor = conn.cursor()

        def show_table() -> None:
            conn = sqlite3.connect("youtube.db")
            selected_table = table_var.get()

            cursor.execute(f"PRAGMA table_info({selected_table})")
            columns = [column[1] for column in cursor.fetchall()]

            if self.treeview is None:
                self.treeview = ttk.Treeview(self.db_tab, columns=(), show="headings")
                self.treeview.pack(fill="both")

            self.treeview["columns"] = columns
            for column in columns:
                self.treeview.heading(
                    column,
                    text=column,
                    command=lambda c=column: sort_treeview(c, False),
                )
                self.treeview.column(column, width=100)

            cursor.execute(f"SELECT * FROM {selected_table}")
            rows = cursor.fetchall()

            for row in self.treeview.get_children():
                self.treeview.delete(row)

            for row in rows:
                self.treeview.insert("", "end", values=row)

        def sort_treeview(
            col: str,
            reverse: bool,
        ) -> None:
            data = [
                (self.treeview.set(child, col), child)
                for child in self.treeview.get_children("")
            ]
            data.sort(reverse=reverse)
            for i, item in enumerate(data):
                self.treeview.move(item[1], "", i)
            self.treeview.heading(col, command=lambda: sort_treeview(col, not reverse))

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]

        table_var = tk.StringVar()
        table_var.set(tables[0])
        table_option_menu = tk.OptionMenu(self.db_tab, table_var, *tables)
        table_option_menu.pack()

        show_button = tk.Button(
            self.db_tab,
            text="Show the table",
            command=show_table,
        )
        show_button.pack()

    def add_tab(
        self,
        tab_control: ttk.Notebook,
    ) -> None:
        db_tab = ttk.Frame(tab_control)
        tab_control.add(
            db_tab,
            text="SQLViewer",
        )
        tab_control.pack()

        return db_tab
