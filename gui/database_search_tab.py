import sqlite3
import tkinter as tk

from tkinter import ttk, scrolledtext


class DataBaseSearch:
    def __init__(
        self,
        tab_control: ttk.Notebook,
    ):
        self.db_tab = self.add_tab(tab_control=tab_control)

    def tab_render(
        self,
    ):
        search_label = ttk.Label(self.db_tab, text="Search by:")
        search_label.grid(row=0, column=0, pady=5)

        search_options = ["User", "Date", "Channel", "Word", "Min messages"]

        search_var = tk.StringVar(self.db_tab)
        search_var.set(search_options[0])

        search_dropdown = tk.OptionMenu(
            self.db_tab,
            search_var,
            *search_options,
        )
        search_dropdown.grid(row=0, column=1, pady=5)

        self.entry = tk.Entry(self.db_tab, width=40, fg="black")
        self.entry.grid(row=0, column=2, pady=5)
        self.entry.insert(0, "Enter text needs to be searched")
        self.entry.bind("<FocusIn>", self.on_entry_click)
        self.entry.bind("<FocusOut>", self.on_entry_leave)

        result_text = scrolledtext.ScrolledText(self.db_tab, width=72, height=10)
        result_text.grid(row=1, columnspan=3, pady=5)

        search_button = tk.Button(
            self.db_tab,
            text="Search",
            command=lambda: self.perform_search(
                search_var.get(), self.entry.get(), result_text
            ),
        )
        search_button.grid(row=2, columnspan=3, pady=5)

    def perform_search(self, search_option, search_text, result_text):
        connection = sqlite3.connect("youtube.db")
        cursor = connection.cursor()

        if search_option == "User":
            query = f"SELECT * FROM users WHERE user_name = '{search_text}'"
            results = cursor.execute(query).fetchall()

        elif search_option == "Date":
            query = f"SELECT * FROM comments WHERE comment_date >= '{search_text}'"
            results = cursor.execute(query).fetchall()

        elif search_option == "Channel":
            query = f"SELECT * FROM channels WHERE channel_name = '{search_text}'"
            results = cursor.execute(query).fetchall()

        elif search_option == "Word":
            query = f"SELECT * FROM comments WHERE comment_text LIKE '%{search_text}%'"
            results = cursor.execute(query).fetchall()

        elif search_option == "Min messages":
            query = f"""
            SELECT users.user_name, COUNT(comments.comment_id)
            FROM users
            LEFT JOIN comments ON users.user_id = comments.user_id
            GROUP BY users.user_name
            HAVING COUNT(comments.comment_id) >= {search_text};
            """
            results = cursor.execute(query).fetchall()

        connection.close()

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "\n".join(map(str, results)))

    def add_tab(
        self,
        tab_control: ttk.Notebook,
    ):
        db_tab = ttk.Frame(tab_control)
        tab_control.add(
            db_tab,
            text="DataBaseaSearcher",
        )
        tab_control.pack()

        return db_tab

    def on_entry_leave(
        self,
        event,
    ):
        if self.entry.get() == "":
            self.entry.insert(0, "Enter text needs to be searched")
            self.entry.config(fg="gray")

    def on_entry_click(
        self,
        event,
    ):
        if self.entry.get() == "Enter text needs to be searched":
            self.entry.delete(0, "end")
            self.entry.config(fg="black")
