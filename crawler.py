import requests
import logging
import re
import json

from progress.bar import Bar
from extractors import VideoExtractor, ChannelExtractor, parse_comment
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
        # Without important metadata, you will not be able to parse
        try:
            data = self.load_meta()
        except Exception as e:
            logging.warning(e)
            return None

        db = Database(path)
        db.initialize()
        bar = Bar(
            "Parsing", max=video_amount * comment_amount, suffix="%(percent).2f%%"
        )

        channel_extractor = ChannelExtractor(data[1])
        channel_data = channel_extractor.channel_extract(self.name)
        channel_id = db.add_channel(
            channel_data["channel_name"],
            channel_data["channel_amount_followers"],
            channel_data["channel_link"],
        )

        video_links = [
            data[1]["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][1][
                "tabRenderer"
            ]["content"]["richGridRenderer"]["contents"][i]["richItemRenderer"][
                "content"
            ][
                "videoRenderer"
            ][
                "videoId"
            ]
            for i in range(30)
        ]
        # On the page of the video itself, it is difficult to collect its duration
        video_durations = [
            data[1]["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][1][
                "tabRenderer"
            ]["content"]["richGridRenderer"]["contents"][i]["richItemRenderer"][
                "content"
            ][
                "videoRenderer"
            ][
                "lengthText"
            ][
                "simpleText"
            ]
            for i in range(30)
        ]

        for i in range(ceil(video_amount / 30) - 1):
            req = self.video_pagination()

            video_links += [
                req["onResponseReceivedActions"][0]["appendContinuationItemsAction"][
                    "continuationItems"
                ][i]["richItemRenderer"]["content"]["videoRenderer"]["videoId"]
                for i in range(30)
            ]
            video_durations += [
                req["onResponseReceivedActions"][0]["appendContinuationItemsAction"][
                    "continuationItems"
                ][i]["richItemRenderer"]["content"]["videoRenderer"]["viewCountText"][
                    "simpleText"
                ]
                for i in range(30)
            ]

        # Collecting videos data and their comments
        for i in range(video_amount):
            response = self.load_video_info(video_links[i])
            video_extractor = VideoExtractor(response)
            video_data = video_extractor.video_extract(
                video_links[i], video_durations[i]
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

            self.comment_pagination(
                video_links[i],
                comment_amount,
                db,
                video_id,
                bar,
            )

        bar.finish()
        db.conn_close()

        logging.warning("Well done!")

    def comment_pagination(
        self,
        link: str,
        comment_amount: int,
        db: Database,
        video_id: str,
        bar: Bar,
    ):
        """Function for pagination of comments on videos."""

        headers = {
            "authority": "www.youtube.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
            "sec-ch-ua-arch": '"arm"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version-list": '"Not)A;Brand";v="24.0.0.0", "Chromium";v="116.0.5845.96"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"macOS"',
            "sec-ch-ua-platform-version": '"14.0.0"',
            "sec-ch-ua-wow64": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.2296 Safari/537.36",
        }

        params = {
            "v": link,
        }

        response = self.session.get(
            "https://www.youtube.com/watch", params=params, headers=headers
        ).text

        data = json.loads(
            re.search(
                '(?<=var ytInitialData \= )(.+?)(?=;\<\/script\>\<script nonce\=")',
                response,
            ).group()
        )

        # Metadata that needs to be changed every pagination
        self.click_tracking_params = data["engagementPanels"][-2][
            "engagementPanelSectionListRenderer"
        ]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"][
            "contents"
        ][
            0
        ][
            "continuationItemRenderer"
        ][
            "continuationEndpoint"
        ][
            "clickTrackingParams"
        ]
        self.continuation = data["engagementPanels"][-2][
            "engagementPanelSectionListRenderer"
        ]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"][
            "contents"
        ][
            0
        ][
            "continuationItemRenderer"
        ][
            "continuationEndpoint"
        ][
            "continuationCommand"
        ][
            "token"
        ]

        cookies = self.session.cookies.get_dict()
        cookies["PREF"] = "tz=Europe.Moscow&f4=4000000"

        headers = {
            "authority": "www.youtube.com",
            "accept": "*/*",
            "accept-language": "en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://www.youtube.com",
            "pragma": "no-cache",
            "referer": f"https://www.youtube.com/watch?v={link}",
            "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
            "sec-ch-ua-arch": '"arm"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version": '"116.0.5845.96"',
            "sec-ch-ua-full-version-list": '"Not)A;Brand";v="24.0.0.0", "Chromium";v="116.0.5845.96"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"macOS"',
            "sec-ch-ua-platform-version": '"14.0.0"',
            "sec-ch-ua-wow64": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "same-origin",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.2296 Safari/537.36",
            "x-goog-visitor-id": self.visitor_data,
            "x-youtube-bootstrap-logged-in": "false",
            "x-youtube-client-name": "1",
            "x-youtube-client-version": self.client_version,
        }

        params = {
            "key": self.api_key,
            "prettyPrint": "false",
        }

        json_data = {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "remoteHost": self.remote_host,
                    "deviceMake": "Apple",
                    "deviceModel": "",
                    "visitorData": self.visitor_data,
                    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.2296 Safari/537.36,gzip(gfe)",
                    "clientName": "WEB",
                    "clientVersion": self.client_version,
                    "osName": "Macintosh",
                    "osVersion": "10_15_7",
                    "originalUrl": f"'https://www.youtube.com/watch?v={link}",
                    "platform": "DESKTOP",
                    "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                    "configInfo": {
                        "appInstallData": self.app_install_data,
                    },
                    "userInterfaceTheme": "USER_INTERFACE_THEME_LIGHT",
                    "browserName": "Chrome",
                    "browserVersion": "116.0.5845.2296",
                    "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "deviceExperimentId": self.device_experiment_id,
                    "screenWidthPoints": 616,
                    "screenHeightPoints": 706,
                    "screenPixelDensity": 2,
                    "screenDensityFloat": 2,
                    "utcOffsetMinutes": 180,
                    "connectionType": "CONN_CELLULAR_4G",
                    "memoryTotalKbytes": "8000000",
                    "mainAppWebInfo": {
                        "graftUrl": f"https://www.youtube.com/watch?v={link}",
                        "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_UNKNOWN",
                        "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                        "isWebNativeShareAvailable": False,
                    },
                    "timeZone": "Europe/Moscow",
                },
                "user": {
                    "lockedSafetyMode": False,
                },
                "request": {
                    "useSsl": True,
                    "internalExperimentFlags": [],
                    "consistencyTokenJars": [],
                },
                "clickTracking": {
                    "clickTrackingParams": self.click_tracking_params,
                },
            },
            "continuation": self.continuation,
        }

        # The first response has slightly different keys in json
        response = self.session.post(
            "https://www.youtube.com/youtubei/v1/next",
            params=params,
            headers=headers,
            cookies=cookies,
            json=json_data,
        ).json()

        cnt = len(
            response["onResponseReceivedEndpoints"][-1][
                "reloadContinuationItemsCommand"
            ]["continuationItems"]
        )

        for i in range(cnt - 1):
            comment_data = parse_comment(
                response["onResponseReceivedEndpoints"][-1][
                    "reloadContinuationItemsCommand"
                ]["continuationItems"][i]
            )
            user_id = db.add_user(comment_data["user_name"], comment_data["user_link"])
            db.add_comment(
                comment_data["comment_text"],
                comment_data["comment_date"],
                comment_data["comment_likes"],
                user_id,
                video_id,
            )

            bar.next()

        # Metadata that needs to be changed every pagination
        self.click_tracking_params = response["onResponseReceivedEndpoints"][-1][
            "reloadContinuationItemsCommand"
        ]["continuationItems"][-1]["continuationItemRenderer"]["continuationEndpoint"][
            "clickTrackingParams"
        ]
        self.continuation = response["onResponseReceivedEndpoints"][-1][
            "reloadContinuationItemsCommand"
        ]["continuationItems"][-1]["continuationItemRenderer"]["continuationEndpoint"][
            "continuationCommand"
        ][
            "token"
        ]
        json_data["context"]["clickTracking"][
            "clickTrackingParams"
        ] = self.click_tracking_params
        json_data["continuation"] = self.continuation

        # Collecting other comments and adding them to the database
        for i in range(ceil(comment_amount / 20) - 1):
            response = self.session.post(
                "https://www.youtube.com/youtubei/v1/next",
                params=params,
                headers=headers,
                cookies=cookies,
                json=json_data,
            ).json()

            if "'error': {'code': 503,'message':" in str(response):
                logging.warning("Error 503")
                return

            cnt = len(
                response["onResponseReceivedEndpoints"][-1][
                    "appendContinuationItemsAction"
                ]["continuationItems"]
            )
            for i in range(cnt - 1):
                chcktxt = str(
                    response["onResponseReceivedEndpoints"][-1][
                        "appendContinuationItemsAction"
                    ]["continuationItems"][i]
                )
                if "token" in chcktxt:
                    click_tracking_params = re.search(
                        "(?<='continuationEndpoint': \{'clickTrackingParams': ')[^']+",
                        chcktxt,
                    ).group()
                    continuation = re.search("(?<='token': ')[^']+", chcktxt).group()

                comment_data = parse_comment(
                    response["onResponseReceivedEndpoints"][-1][
                        "appendContinuationItemsAction"
                    ]["continuationItems"][i]
                )
                user_id = db.add_user(
                    comment_data["user_name"], comment_data["user_link"]
                )
                db.add_comment(
                    comment_data["comment_text"],
                    comment_data["comment_date"],
                    comment_data["comment_likes"],
                    user_id,
                    video_id,
                )

                bar.next()

            # Metadata that needs to be changed every pagination
            try:
                self.click_tracking_params = response["onResponseReceivedEndpoints"][
                    -1
                ]["appendContinuationItemsAction"]["continuationItems"][-1][
                    "continuationItemRenderer"
                ][
                    "continuationEndpoint"
                ][
                    "clickTrackingParams"
                ]
                self.continuation = response["onResponseReceivedEndpoints"][-1][
                    "appendContinuationItemsAction"
                ]["continuationItems"][-1]["continuationItemRenderer"][
                    "continuationEndpoint"
                ][
                    "continuationCommand"
                ][
                    "token"
                ]
            except:
                self.click_tracking_params = click_tracking_params
                self.continuation = continuation

            json_data["context"]["clickTracking"][
                "clickTrackingParams"
            ] = self.click_tracking_params
            json_data["continuation"] = self.continuation

    def load_meta(self):
        """Function for getting important meta data"""

        headers = {
            "authority": "www.youtube.com",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en;q=0.9",
            "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
            "sec-ch-ua-arch": '"arm"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version-list": '"Not)A;Brand";v="24.0.0.0", "Chromium";v="116.0.5845.96"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"macOS"',
            "sec-ch-ua-platform-version": '"14.0.0"',
            "sec-ch-ua-wow64": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.2296 Safari/537.36",
        }

        response = self.session.get(
            f"https://www.youtube.com/{self.name}/videos", headers=headers
        ).text

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

        try:
            self.api_key = data[0]["INNERTUBE_API_KEY"]
            self.continuation = data[1]["contents"]["twoColumnBrowseResultsRenderer"][
                "tabs"
            ][1]["tabRenderer"]["content"]["richGridRenderer"]["contents"][-1][
                "continuationItemRenderer"
            ][
                "continuationEndpoint"
            ][
                "continuationCommand"
            ][
                "token"
            ]
            self.visitor_data = data[1]["responseContext"][
                "webResponseContextExtensionData"
            ]["ytConfigData"]["visitorData"]
            self.client_version = data[0]["INNERTUBE_CONTEXT"]["client"][
                "clientVersion"
            ]
            self.remote_host = data[0]["INNERTUBE_CONTEXT"]["client"]["remoteHost"]
            self.app_install_data = data[0]["INNERTUBE_CONTEXT"]["client"][
                "configInfo"
            ]["appInstallData"]
            self.device_experiment_id = data[0]["INNERTUBE_CONTEXT"]["client"][
                "deviceExperimentId"
            ]
            self.click_tracking_params = data[1]["contents"][
                "twoColumnBrowseResultsRenderer"
            ]["tabs"][1]["tabRenderer"]["content"]["richGridRenderer"]["contents"][-1][
                "continuationItemRenderer"
            ][
                "continuationEndpoint"
            ][
                "clickTrackingParams"
            ]
        except Exception as e:
            raise e

        return data

    def video_pagination(self):
        """Function for pagination of videos on channel"""

        cookies = self.session.cookies.get_dict()
        cookies["PREF"] = "tz=Europe.Moscow&f4=4000000"

        headers = {
            "authority": "www.youtube.com",
            "accept": "*/*",
            "accept-language": "en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://www.youtube.com",
            "pragma": "no-cache",
            "referer": f"https://www.youtube.com/{self.name}/videos",
            "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
            "sec-ch-ua-arch": '"arm"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version": '"116.0.5845.96"',
            "sec-ch-ua-full-version-list": '"Not)A;Brand";v="24.0.0.0", "Chromium";v="116.0.5845.96"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"macOS"',
            "sec-ch-ua-platform-version": '"14.0.0"',
            "sec-ch-ua-wow64": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "same-origin",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.2296 Safari/537.36",
            "x-goog-visitor-id": self.visitor_data,
            "x-youtube-bootstrap-logged-in": "false",
            "x-youtube-client-name": "1",
            "x-youtube-client-version": self.client_version,
        }

        params = {
            "key": self.api_key,
            "prettyPrint": "false",
        }

        json_data = {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "remoteHost": self.remote_host,
                    "deviceMake": "Apple",
                    "deviceModel": "",
                    "visitorData": self.visitor_data,
                    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.2296 Safari/537.36,gzip(gfe)",
                    "clientName": "WEB",
                    "clientVersion": self.client_version,
                    "osName": "Macintosh",
                    "osVersion": "10_15_7",
                    "originalUrl": f"https://www.youtube.com/{self.name}/videos",
                    "screenPixelDensity": 2,
                    "platform": "DESKTOP",
                    "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                    "configInfo": {
                        "appInstallData": self.app_install_data,
                    },
                    "screenDensityFloat": 2,
                    "userInterfaceTheme": "USER_INTERFACE_THEME_LIGHT",
                    "timeZone": "Europe/Moscow",
                    "browserName": "Chrome",
                    "browserVersion": "116.0.5845.2296",
                    "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "deviceExperimentId": self.device_experiment_id,
                    "screenWidthPoints": 616,
                    "screenHeightPoints": 706,
                    "utcOffsetMinutes": 180,
                    "connectionType": "CONN_CELLULAR_4G",
                    "memoryTotalKbytes": "8000000",
                    "mainAppWebInfo": {
                        "graftUrl": f"https://www.youtube.com/{self.name}/videos",
                        "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_UNKNOWN",
                        "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                        "isWebNativeShareAvailable": False,
                    },
                },
                "user": {
                    "lockedSafetyMode": False,
                },
                "request": {
                    "useSsl": True,
                    "internalExperimentFlags": [],
                    "consistencyTokenJars": [],
                },
                "clickTracking": {
                    "clickTrackingParams": self.click_tracking_params,
                },
            },
            "continuation": self.continuation,
        }

        response = self.session.post(
            "https://www.youtube.com/youtubei/v1/browse",
            params=params,
            cookies=cookies,
            headers=headers,
            json=json_data,
        ).json()

        # Metadata that needs to be changed every pagination
        self.click_tracking_params = response["onResponseReceivedActions"][0][
            "appendContinuationItemsAction"
        ]["continuationItems"][-1]["continuationItemRenderer"]["continuationEndpoint"][
            "clickTrackingParams"
        ]
        self.continuation = response["onResponseReceivedActions"][0][
            "appendContinuationItemsAction"
        ]["continuationItems"][-1]["continuationItemRenderer"]["continuationEndpoint"][
            "continuationCommand"
        ][
            "token"
        ]

        return response

    def load_video_info(self, link: str):
        """Function for collecting video data"""

        cookies = self.session.cookies.get_dict()
        cookies["PREF"] = "tz=Europe.Moscow&f4=4000000"

        headers = {
            "authority": "www.youtube.com",
            "accept": "*/*",
            "accept-language": "en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://www.youtube.com",
            "pragma": "no-cache",
            "referer": f"https://www.youtube.com/watch?v={link}",
            "sec-ch-ua": '"Not)A;Brand";v="24", "Chromium";v="116"',
            "sec-ch-ua-arch": '"arm"',
            "sec-ch-ua-bitness": '"64"',
            "sec-ch-ua-full-version": '"116.0.5845.96"',
            "sec-ch-ua-full-version-list": '"Not)A;Brand";v="24.0.0.0", "Chromium";v="116.0.5845.96"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": '""',
            "sec-ch-ua-platform": '"macOS"',
            "sec-ch-ua-platform-version": '"14.0.0"',
            "sec-ch-ua-wow64": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "same-origin",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.2296 Safari/537.36",
            "x-goog-visitor-id": self.visitor_data,
            "x-youtube-bootstrap-logged-in": "false",
            "x-youtube-client-name": "1",
            "x-youtube-client-version": self.client_version,
        }

        params = {
            "key": self.api_key,
            "prettyPrint": "false",
        }

        json_data = {
            "context": {
                "client": {
                    "hl": "en",
                    "gl": "US",
                    "remoteHost": self.remote_host,
                    "deviceMake": "Apple",
                    "deviceModel": "",
                    "visitorData": self.visitor_data,
                    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.2296 Safari/537.36,gzip(gfe)",
                    "clientName": "WEB",
                    "clientVersion": self.client_version,
                    "osName": "Macintosh",
                    "osVersion": "10_15_7",
                    "originalUrl": f"https://www.youtube.com/watch?v={link}",
                    "screenPixelDensity": 2,
                    "platform": "DESKTOP",
                    "clientFormFactor": "UNKNOWN_FORM_FACTOR",
                    "configInfo": {
                        "appInstallData": self.app_install_data,
                    },
                    "screenDensityFloat": 2,
                    "userInterfaceTheme": "USER_INTERFACE_THEME_LIGHT",
                    "timeZone": "Europe/Moscow",
                    "browserName": "Chrome",
                    "browserVersion": "116.0.5845.2296",
                    "acceptHeader": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "deviceExperimentId": self.device_experiment_id,
                    "screenWidthPoints": 616,
                    "screenHeightPoints": 706,
                    "utcOffsetMinutes": 180,
                    "memoryTotalKbytes": "8000000",
                    "clientScreen": "WATCH",
                    "mainAppWebInfo": {
                        "graftUrl": f"/watch?v={link}",
                        "pwaInstallabilityStatus": "PWA_INSTALLABILITY_STATUS_UNKNOWN",
                        "webDisplayMode": "WEB_DISPLAY_MODE_BROWSER",
                        "isWebNativeShareAvailable": False,
                    },
                },
                "user": {
                    "lockedSafetyMode": False,
                },
                "request": {
                    "useSsl": True,
                    "internalExperimentFlags": [],
                    "consistencyTokenJars": [],
                },
                "clickTracking": {
                    "clickTrackingParams": self.click_tracking_params,
                },
            },
            "videoId": link,
            "racyCheckOk": False,
            "contentCheckOk": False,
            "autonavState": "STATE_NONE",
            "playbackContext": {
                "vis": 0,
                "lactMilliseconds": "-1",
            },
            "captionsRequested": False,
        }

        response = self.session.post(
            "https://www.youtube.com/youtubei/v1/next",
            params=params,
            cookies=cookies,
            headers=headers,
            json=json_data,
        ).json()

        # Metadata that needs to be changed every pagination
        self.click_tracking_params = response["contents"]["twoColumnWatchNextResults"][
            "secondaryResults"
        ]["secondaryResults"]["results"][-1]["continuationItemRenderer"][
            "continuationEndpoint"
        ][
            "clickTrackingParams"
        ]
        self.continuation = response["contents"]["twoColumnWatchNextResults"][
            "secondaryResults"
        ]["secondaryResults"]["results"][-1]["continuationItemRenderer"][
            "continuationEndpoint"
        ][
            "continuationCommand"
        ][
            "token"
        ]

        return response
