import WebCrawler

wc = WebCrawler.WebCrawler("baseURLs")
wc.crawl()
print(wc.get_brand_score())
