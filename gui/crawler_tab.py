import threading
import tkinter as tk

from tkinter import ttk
from crawler.crawler import YouTubeCrawler
from crawler.db import Database


class CrawlerTab:
    """Сlass that creates a tab with a YouTube crawler"""

    def __init__(
        self,
        tab_control: ttk.Notebook,
    ):
        self.db_tab = self.add_tab(tab_control=tab_control)

    def tab_render(
        self,
    ):
        channel_label = ttk.Label(self.db_tab, text="Channel name:")
        channel_label.grid(row=0, column=0, padx=10, pady=5)
        num_videos_label = ttk.Label(self.db_tab, text="Number of videos:")
        num_videos_label.grid(row=1, column=0, padx=10, pady=5)
        num_comments_label = ttk.Label(self.db_tab, text="Number of comments:")
        num_comments_label.grid(row=2, column=0, padx=10, pady=5)

        self.channel_name_entry = tk.Entry(self.db_tab, width=40, fg="gray")
        self.channel_name_entry.grid(row=0, column=1, padx=10, pady=5)
        self.channel_name_entry.insert(0, "Enter name of channel needs to be crawled")
        self.channel_name_entry.bind("<FocusIn>", self.on_entry_click)
        self.channel_name_entry.bind("<FocusOut>", self.on_entry_leave)

        self.num_videos_entry = tk.Entry(self.db_tab, width=40, fg="gray")
        self.num_videos_entry.grid(row=1, column=1, padx=10, pady=5)
        self.num_videos_entry.insert(0, "Enter number of videos needs to be crawled")
        self.num_videos_entry.bind("<FocusIn>", self.on_num_videos_click)
        self.num_videos_entry.bind("<FocusOut>", self.on_num_videos_leave)

        self.num_comments_entry = tk.Entry(self.db_tab, width=40, fg="gray")
        self.num_comments_entry.grid(row=2, column=1, padx=10, pady=5)
        self.num_comments_entry.insert(
            0, "Enter number of comments needs to be crawled from every video"
        )
        self.num_comments_entry.bind("<FocusIn>", self.on_num_comments_click)
        self.num_comments_entry.bind("<FocusOut>", self.on_num_comments_leave)

        parser_button = tk.Button(
            self.db_tab,
            text="Run crawling",
            command=lambda: self.run_crawler(
                self.channel_name_entry.get(),
                int(self.num_videos_entry.get()),
                int(self.num_comments_entry.get()),
            ),
        )
        parser_button.grid(row=3, column=0, padx=10, pady=10, columnspan=2)

    def run_crawler(
        self,
        name: str,
        video_amount: int = 10,
        comment_amount: int = 1000,
    ):
        crawler = YouTubeCrawler(name)

        progress_var = tk.DoubleVar()
        progress_var.set(0.0)

        progress_bar = ttk.Progressbar(
            self.db_tab,
            length=200,
            mode="determinate",
            variable=progress_var,
        )
        progress_bar.grid(row=4, column=0, columnspan=2, pady=10)

        progress_label = ttk.Label(self.db_tab, text="Crawler process")
        progress_label.grid(row=5, column=0, columnspan=2)

        def update_progress(progress):
            progress_var.set(progress)

            if progress >= 100.0:
                progress_bar.grid_forget()
                progress_label.config(text="Well Done!")

        def start_crawling():
            crawler.load_channel(
                video_amount=video_amount,
                comment_amount=comment_amount,
                progress_callback=update_progress,
            )

        parser_thread = threading.Thread(target=start_crawling)
        parser_thread.start()

    def add_tab(
        self,
        tab_control: ttk.Notebook,
    ):
        db_tab = ttk.Frame(tab_control)
        tab_control.add(
            db_tab,
            text="YouTube Crawler",
        )
        tab_control.pack()

        return db_tab

    def on_entry_click(
        self,
        event,
    ):
        if self.channel_name_entry.get() == "Enter name of channel needs to be crawled":
            self.channel_name_entry.delete(0, "end")
            self.channel_name_entry.config(fg="black")

    def on_num_videos_click(
        self,
        event,
    ):
        if self.num_videos_entry.get() == "Enter number of videos needs to be crawled":
            self.num_videos_entry.delete(0, "end")
            self.num_videos_entry.config(fg="black")

    def on_num_comments_click(
        self,
        event,
    ):
        if (
            self.num_comments_entry.get()
            == "Enter number of comments needs to be crawled from every video"
        ):
            self.num_comments_entry.delete(0, "end")
            self.num_comments_entry.config(fg="black")

    def on_entry_leave(
        self,
        event,
    ):
        if self.channel_name_entry.get() == "":
            self.channel_name_entry.insert(
                0, "Enter name of channel needs to be crawled"
            )
            self.channel_name_entry.config(fg="gray")

    def on_num_videos_leave(
        self,
        event,
    ):
        if self.num_videos_entry.get() == "":
            self.num_videos_entry.insert(
                0, "Enter number of videos needs to be crawled"
            )
            self.num_videos_entry.config(fg="gray")

    def on_num_comments_leave(
        self,
        event,
    ):
        if self.num_comments_entry.get() == "":
            self.num_comments_entry.insert(
                0, "Enter number of comments needs to be crawled from every video"
            )
            self.num_comments_entry.config(fg="gray")
