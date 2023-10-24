import sqlite3

from date_converter import parse_time_ago


class Database:
    """"""

    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def initialize(self):
        self.cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS channels (
                channel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_name VARCHAR,
                channel_amount_followers VARCHAR,
                channel_link VARCHAR
            );

            CREATE TABLE IF NOT EXISTS videos (
                video_id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_name VARCHAR,
                video_link VARCHAR,
                video_views VARCHAR,
                video_likes VARCHAR,
                video_date VARCHAR,
                video_duration VARCHAR,
                channel_id INT REFERENCES channels(channel_id)
            );

            CREATE TABLE IF NOT EXISTS comments (
                comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                comment_text VARCHAR,
                comment_date VARCHAR,
                comment_likes VARCHAR,
                user_id INT REFERENCES users(id),
                video_id INT REFERENCES videos(video_id)
            );

            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name VARCHAR,
                user_link VARCHAR
            );

            CREATE TABLE IF NOT EXISTS user_files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_type VARCHAR,
                file_path VARCHAR,
                user_id VARCHAR REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS video_files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_type VARCHAR,
                file_path VARCHAR,
                video_id VARCHAR REFERENCES videos(video_id)
            );

            CREATE TABLE IF NOT EXISTS channel_files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_type VARCHAR,
                file_path VARCHAR,
                channel_id VARCHAR REFERENCES channels(channel_id)
            );
            """
        )
        self.conn.commit()

    def add_channel(
        self,
        name: str,
        amount_followers: str,
        link: str,
    ):
        self.cursor.execute(
            """
            INSERT INTO channels (channel_name, channel_amount_followers, channel_link)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1
                FROM channels
                WHERE channel_name = ?
            );
            """,
            (name, amount_followers, link, name),
        )
        self.conn.commit()

        self.cursor.execute("SELECT MAX(channel_id) FROM channels")
        last_id = self.cursor.fetchone()[0]

        return last_id

    def add_video(
        self,
        name: str,
        link: str,
        views: str,
        likes: str,
        date: str,
        duration: str,
        channel_id: int,
    ):
        self.cursor.execute(
            """
            INSERT INTO videos (video_name, video_link, video_views, video_likes, video_date, video_duration, channel_id)
            SELECT ?, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1
                FROM videos
                WHERE video_link = ?
            );
            """,
            (name, link, views, likes, date, duration, channel_id, link),
        )
        self.conn.commit()

        self.cursor.execute("SELECT MAX(video_id) FROM videos")
        last_id = self.cursor.fetchone()[0]

        return last_id

    def add_comment(
        self,
        text: str,
        date: str,
        likes: str,
        user_id: str,
        video_id: int,
    ):
        self.cursor.execute(
            """
            INSERT INTO comments (comment_text, comment_date, comment_likes, user_id, video_id) VALUES(?, ?, ?, ?, ?);
            """,
            (text, parse_time_ago(date), likes, user_id, video_id),
        )
        self.conn.commit()

    def add_user(
        self,
        name: str,
        link: str,
    ):
        self.cursor.execute(
            """
            INSERT INTO users (user_name, user_link)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1
                FROM users
                WHERE user_name = ?
            )
            """,
            (name, link, name),
        )
        self.conn.commit()

        self.cursor.execute("SELECT MAX(user_id) FROM users")
        last_id = self.cursor.fetchone()[0]

        return last_id

    def add_user_files(
        self,
        type: str,
        path: str,
        user_id: int,
    ):
        self.cursor.execute(
            """
            INSERT INTO user_files (file_type, file_path, user_id)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1
                FROM user_files
                WHERE user_id = ?
            )
            """,
            (type, path, user_id, user_id),
        )
        self.conn.commit()

    def add_video_files(
        self,
        type: str,
        path: str,
        video_id: int,
    ):
        self.cursor.execute(
            """
            INSERT INTO video_files (file_type, file_path, video_id)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1
                FROM video_files
                WHERE video_id = ?
            )
            """,
            (type, path, video_id, video_id),
        )
        self.conn.commit()

    def add_channel_files(
        self,
        type: str,
        path: str,
        channel_id: int,
    ):
        self.cursor.execute(
            """
            INSERT INTO channel_files (file_type, file_path, channel_id)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1
                FROM channel_files
                WHERE channel_id = ?
            )
            """,
            (type, path, channel_id, channel_id),
        )
        self.conn.commit()

    def conn_close(self):
        self.conn.close()
