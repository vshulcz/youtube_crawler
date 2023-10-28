from tkinter import ttk
from tkinter import Tk
from gui.crawler_tab import CrawlerTab
from gui.database_executor_tab import DataBaseExecutorTab
from gui.database_search_tab import DataBaseSearch
from gui.database_view_tab import DataBaseView


class MyApplication:
    """Сlass for YouTube Crawler application"""

    def __init__(
        self,
        root: Tk,
    ) -> None:
        self.root = root
        self.root.title("YouTube Crawler")
        self.root.geometry("625x300")
        self.root.resizable(width=False, height=False)

        self.tab_control = ttk.Notebook(root)

        CrawlerTab(tab_control=self.tab_control).tab_render()
        DataBaseView(tab_control=self.tab_control).tab_render()
        DataBaseExecutorTab(tab_control=self.tab_control).tab_render()
        DataBaseSearch(tab_control=self.tab_control).tab_render()

        self.tab_control.pack()
