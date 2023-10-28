import sqlite3
import tkinter as tk

from tkinter import ttk, scrolledtext


class DataBaseExecutorTab:
    """Class that creates a tab for the ability to send queries to the database"""

    def __init__(
        self,
        tab_control: ttk.Notebook,
    ) -> None:
        self.db_tab = self.add_tab(tab_control=tab_control)

    def tab_render(
        self,
    ) -> None:
        self.query_entry = tk.Entry(self.db_tab, width=40, fg="gray")
        self.query_entry.grid(row=0, column=0, padx=10, pady=3)
        self.query_entry.insert(0, "Enter your query")
        self.query_entry.bind("<FocusIn>", self.on_entry_click)
        self.query_entry.bind("<FocusOut>", self.on_entry_leave)

        result_label = ttk.Label(self.db_tab, text="Your result:")
        result_label.grid(row=1, padx=10, pady=3, columnspan=2)

        result_text = scrolledtext.ScrolledText(self.db_tab, width=72, height=10)
        result_text.grid(row=2, padx=10, pady=3, columnspan=2)

        execute_button = tk.Button(
            self.db_tab,
            text="Execute a request",
            command=lambda: self.execute_query(result_text),
        )
        execute_button.grid(
            row=0,
            column=1,
            padx=10,
            pady=3,
        )

    def execute_query(
        self,
        result_text: scrolledtext.ScrolledText,
    ) -> None:
        query = self.query_entry.get()

        connection = sqlite3.connect("youtube.db")
        results = connection.cursor().execute(query).fetchall()
        connection.close()

        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "\n".join(map(str, results)))

    def add_tab(
        self,
        tab_control: ttk.Notebook,
    ) -> ttk.Frame:
        db_tab = ttk.Frame(tab_control)
        tab_control.add(
            db_tab,
            text="DataBaseExecutor",
        )
        tab_control.pack()

        return db_tab

    def on_entry_leave(
        self,
        event,
    ) -> None:
        if self.query_entry.get() == "":
            self.query_entry.insert(0, "Enter your query")
            self.query_entry.config(fg="gray")

    def on_entry_click(
        self,
        event,
    ) -> None:
        if self.query_entry.get() == "Enter your query":
            self.query_entry.delete(0, "end")
            self.query_entry.config(fg="black")
