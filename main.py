from crawler import YouTubeCrawler

crawler = YouTubeCrawler("@MrBeast")

crawler.load_channel(video_amount=200, comment_amount=5000)
