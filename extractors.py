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


class CommentExtractor:
    """Class for extracting data from a comment"""

    def __init__(self, element: dict):
        self.element = element

    def new_comment(self) -> dict:
        return {
            "user_name": None,
            "user_link": None,
            "user_avatar": None,
            "comment_text": None,
            "comment_date": None,
            "comment_likes": None,
        }

    def comment_extract(self) -> dict:
        comment = self.new_comment()

        try:
            comment["user_name"] = self.element["authorText"]["simpleText"]
        except:
            comment["user_name"] = ""
        try:
            comment["user_link"] = self.element["authorEndpoint"]["browseEndpoint"][
                "browseId"
            ]
        except:
            comment["user_link"] = ""
        try:
            comment["comment_text"] = self.element["contentText"]["runs"][0]["text"]
        except:
            comment["comment_text"] = ""
        comment["comment_date"] = self.element["publishedTimeText"]["runs"][0]["text"]
        try:
            comment["comment_likes"] = self.element["voteCount"]["simpleText"]
        except:
            comment["comment_likes"] = 0
        try:
            comment["user_avatar"] = self.element["authorThumbnail"][2]["url"]
        except:
            comment["user_avatar"] = ""

        return comment
