from crawler import YouTubeCrawler

crawler = YouTubeCrawler("@MrBeast")

crawler.load_channel(video_amount=50, comment_amount=20000)
