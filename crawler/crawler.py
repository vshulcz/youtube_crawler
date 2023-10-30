import requests
import re
import json

from typing import Callable
from math import ceil
from crawler.extractors import VideoExtractor, ChannelExtractor, CommentExtractor
from crawler.db import Database
from crawler.find_keys import find_keys


class YouTubeCrawler:
    """
    Class for extracting important data from a channel.
    You need to pass the YouTube channel id to the class.
    For example: YouTubeCrawler("@MrBeast")
    """

    def __init__(self, name: str) -> None:
        self.session = requests.session()
        self.session.headers[
            "User-Agent"
        ] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.2296 YaBrowser/23.9.0.2296 Yowser/2.5 Safari/537.36"
        self.name = name

    def load_channel(
        self,
        progress_callback: Callable[[int], None],
        video_amount: int = 10,
        comment_amount: int = 1000,
        path: str = "youtube.db",
    ) -> None:
        """
        Function for collecting data about the channel and its videos.
        It should transmit the number of videos that need to be parsed and the number of
        comments that need to be collected under each video.
        """
        db = Database(path)
        db.initialize()

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

        videos = find_keys(data[1], "videoRenderer")
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

            videos = find_keys(data[1], "videoRenderer")
            videos_ldv += [
                [
                    video["videoId"],
                    video["lengthText"]["simpleText"],
                    video["thumbnail"]["thumbnails"][3]["url"],
                ]
                for video in videos
            ]

        progress = 0
        precent = 100 / video_amount

        # Collecting videos data and their comments
        for i in range(video_amount):
            self.load_video(
                data,
                videos_ldv[i][0],
            )

            video_extractor = VideoExtractor(data[1])
            video_data = video_extractor.video_extract(
                videos_ldv[i][0],
                videos_ldv[i][1],
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
                videos_ldv[i][2],
                video_id,
            )

            self.comment_pagination(
                data,
                comment_amount,
                db,
                video_id,
            )
            progress += precent
            progress_callback(progress)
        progress_callback(100)
        db.conn_close()

    def comment_pagination(
        self,
        data: list,
        comment_amount: int,
        db: Database,
        video_id: str,
    ) -> None:
        """Function for pagination of comments on videos."""
        comment_cnt = 0
        tokens = [find_keys(data[1], "subMenuItems")[0][0]["serviceEndpoint"]]

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
                for tkn in find_keys(data[1], "continuationEndpoint")
            ]

            comments = find_keys(data[1], "commentRenderer")

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
            "continuation": find_keys(data[1], "continuationEndpoint")[0][
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
