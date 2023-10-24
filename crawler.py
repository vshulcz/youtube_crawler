import requests
import logging
import re
import json

from fake_useragent import UserAgent
from progress.bar import Bar
from extractors import VideoExtractor, ChannelExtractor, CommentExtractor
from db import Database
from math import ceil

logger = logging.getLogger(__name__)


class YouTubeCrawler:
    """
    Class for extracting important data from a channel.
    You need to pass the YouTube channel id to the class.
    For example: YouTubeCrawler("@MrBeast")
    """

    def __init__(self, name: str):
        self.session = requests.session()
        self.session.headers["User-Agent"] = UserAgent().random
        self.name = name

    def load_channel(
        self,
        video_amount: int = 10,
        comment_amount: int = 1000,
        path: str = "youtube.db",
    ):
        """
        Function for collecting data about the channel and its videos.
        It should transmit the number of videos that need to be parsed and the number of
        comments that need to be collected under each video.
        """
        db = Database(path)
        db.initialize()
        bar = Bar(
            "Parsing", max=video_amount * comment_amount, suffix="%(percent).2f%%"
        )

        response = self.session.get(f"https://www.youtube.com/{self.name}/videos").text

        data = []
        data.append(
            json.loads(
                re.search(
                    "(?<=ytcfg\.set\()(.+?)(?=\); window\.ytcfg)", response
                ).group()
            )
        )
        data.append(
            json.loads(
                re.search(
                    '(?<=var ytInitialData \= )(.+?)(?=;\<\/script\>\<script nonce\=")',
                    response,
                ).group()
            )
        )

        data[0]["INNERTUBE_CONTEXT"]["client"]["hl"] = "en"

        channel_extractor = ChannelExtractor(data[1])
        channel_data = channel_extractor.channel_extract(self.name)
        channel_id = db.add_channel(
            channel_data["channel_name"],
            channel_data["channel_amount_followers"],
            channel_data["channel_link"],
        )
        db.add_channel_files(
            "image",
            channel_data["channel_avatar"],
            channel_id,
        )

        videos = self.find_keys(data[1], "videoRenderer")
        videos_ldv = [
            [
                video["videoId"],
                video["lengthText"]["simpleText"],
                video["thumbnail"]["thumbnails"][3]["url"],
            ]
            for video in videos
        ]

        for _ in range(ceil(video_amount / 30) - 1):
            self.video_pagination(data)

            videos = self.find_keys(data[1], "videoRenderer")
            videos_ldv += [
                [
                    video["videoId"],
                    video["lengthText"]["simpleText"],
                    video["thumbnail"]["thumbnails"][3]["url"],
                ]
                for video in videos
            ]

        # Collecting videos data and their comments
        for link, duration, preview in videos_ldv:
            self.load_video(
                data,
                link,
            )

            video_extractor = VideoExtractor(data[1])
            video_data = video_extractor.video_extract(
                link,
                duration,
            )
            video_id = db.add_video(
                video_data["video_name"],
                video_data["video_link"],
                video_data["video_views"],
                video_data["video_likes"],
                video_data["video_date"],
                video_data["video_duration"],
                channel_id,
            )
            db.add_video_files(
                "image",
                preview,
                video_id,
            )

            self.comment_pagination(
                data,
                comment_amount,
                db,
                video_id,
                bar,
            )

        bar.finish()
        db.conn_close()

    def comment_pagination(
        self,
        data: list,
        comment_amount: int,
        db: Database,
        video_id: str,
        bar: Bar,
    ) -> None:
        """Function for pagination of comments on videos."""
        comment_cnt = 0
        tokens = [self.find_keys(data[1], "subMenuItems")[0][0]["serviceEndpoint"]]

        while comment_amount > comment_cnt and tokens:
            token = tokens.pop()

            params = {
                "key": data[0]["INNERTUBE_API_KEY"],
            }

            json_data = {
                "context": data[0]["INNERTUBE_CONTEXT"],
                "continuation": token["continuationCommand"]["token"],
            }

            response = self.session.post(
                "https://www.youtube.com/youtubei/v1/next",
                params=params,
                json=json_data,
            ).json()

            data[1] = response
            [
                tokens.insert(0, tkn)
                for tkn in self.find_keys(data[1], "continuationEndpoint")
            ]

            comments = self.find_keys(data[1], "commentRenderer")

            for comment in comments:
                comment_extractor = CommentExtractor(comment)
                comment_data = comment_extractor.comment_extract()

                user_id = db.add_user(
                    comment_data["user_name"],
                    comment_data["user_link"],
                )
                db.add_comment(
                    comment_data["comment_text"],
                    comment_data["comment_date"],
                    comment_data["comment_likes"],
                    user_id,
                    video_id,
                )
                if comment_data["user_avatar"] != "":
                    db.add_user_files(
                        "image",
                        comment_data["user_avatar"],
                        user_id,
                    )

                bar.next()
            comment_cnt += len(comments)

    def video_pagination(
        self,
        data: list,
    ) -> None:
        """Function for pagination of videos on channel"""
        params = {
            "key": data[0]["INNERTUBE_API_KEY"],
        }
        json_data = {
            "context": data[0]["INNERTUBE_CONTEXT"],
            "continuation": self.find_keys(data[1], "continuationEndpoint")[0][
                "continuationCommand"
            ]["token"],
        }

        response = self.session.post(
            "https://www.youtube.com/youtubei/v1/browse",
            params=params,
            json=json_data,
        ).json()
        data[1] = response

    def load_video(
        self,
        data: list,
        link: str,
    ) -> None:
        """Function for collecting video data"""
        response = self.session.get(f"https://www.youtube.com/watch?v={link}").text
        data[1] = json.loads(
            re.search(
                '(?<=var ytInitialData \= )(.+?)(?=;\<\/script\>\<script nonce\=")',
                response,
            ).group()
        )

    def find_keys(
        self,
        json_data: json,
        target_key: str,
    ) -> list:
        """Function for finding keys in json"""
        results = []

        def find_key(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == target_key:
                        results.append(value)
                    find_key(value)
            elif isinstance(data, list):
                for item in data:
                    find_key(item)

        find_key(json_data)
        return results
