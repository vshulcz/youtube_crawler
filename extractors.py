import json


class VideoExtractor:
    """Сlass for extracting data from a video"""

    def __init__(self, element: dict):
        self.element = element

    def new_video(self) -> dict:
        return {
            "video_name": None,
            "video_link": None,
            "video_views": None,
            "video_likes": None,
            "video_date": None,
            "video_duration": None,
            "video_preview": None,
        }

    def video_extract(self, link: str, duration: str) -> dict:
        video = self.new_video()

        video["video_name"] = self.element["contents"]["twoColumnWatchNextResults"][
            "results"
        ]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["title"]["runs"][0][
            "text"
        ]
        video["video_link"] = f"https://www.youtube.com/watch?v={link}"
        video["video_views"] = self.element["contents"]["twoColumnWatchNextResults"][
            "results"
        ]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["viewCount"][
            "videoViewCountRenderer"
        ][
            "viewCount"
        ][
            "simpleText"
        ]
        video["video_likes"] = self.element["contents"]["twoColumnWatchNextResults"][
            "results"
        ]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["videoActions"][
            "menuRenderer"
        ][
            "topLevelButtons"
        ][
            0
        ][
            "segmentedLikeDislikeButtonRenderer"
        ][
            "likeButton"
        ][
            "toggleButtonRenderer"
        ][
            "defaultText"
        ][
            "accessibility"
        ][
            "accessibilityData"
        ][
            "label"
        ]
        video["video_date"] = self.element["contents"]["twoColumnWatchNextResults"][
            "results"
        ]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["dateText"][
            "simpleText"
        ]
        video["video_duration"] = duration
        video["video_preview"] = self.element["contents"]["twoColumnWatchNextResults"][
            "results"
        ]["results"]["contents"][1]["videoSecondaryInfoRenderer"]["owner"][
            "videoOwnerRenderer"
        ][
            "thumbnail"
        ][
            "thumbnails"
        ][
            2
        ][
            "url"
        ]

        return video


class ChannelExtractor:
    """Class for extracting data from a channel"""

    def __init__(self, element: dict):
        self.element = element

    def new_channel(self) -> dict:
        return {
            "channel_name": None,
            "channel_amount_followers": None,
            "channel_link": None,
            "channel_avatar": None,
        }

    def channel_extract(self, name: str) -> dict:
        channel = self.new_channel()

        channel["channel_name"] = name
        channel["channel_amount_followers"] = self.element["header"][
            "c4TabbedHeaderRenderer"
        ]["subscriberCountText"]["simpleText"]
        channel["channel_link"] = f"https://www.youtube.com/{name}"
        channel["channel_avatar"] = self.element["header"]["c4TabbedHeaderRenderer"][
            "avatar"
        ]["thumbnails"][-1]["url"]

        return channel


def parse_comment(data: dict) -> dict:
    try:
        comment = data["commentThreadRenderer"]["comment"]["commentRenderer"]
    except AttributeError:
        comment = data["commentRenderer"]

    user_name = comment["authorText"]["simpleText"]
    user_link = comment["authorEndpoint"]["browseEndpoint"]["browseId"]
    comment_text = comment["contentText"]["runs"][0]["text"]
    comment_date = comment["publishedTimeText"]["runs"][0]["text"]
    try:
        comment_likes = comment["voteCount"]["simpleText"]
    except AttributeError:
        comment_likes = 0

    return {
        "user_name": user_name,
        "user_link": user_link,
        "comment_text": comment_text,
        "comment_date": comment_date,
        "comment_likes": comment_likes,
    }
