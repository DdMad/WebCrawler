import csv
import nltk
import time
import socket
import urlparse
import traceback
import threading
from bs4 import BeautifulSoup
from ipwhois import IPWhois
from threading import Thread
from nltk.corpus import stopwords
from readability.readability import Document


class WebCrawler:
    PAGE_TO_CRAWL = 10
    PAGE_LENGTH_LIMIT = 100
    BACKUP_THRESHOLD = 5

    # read in all the brands provided
    brandList = open("brands", "r").read().split(",")
    # read in all the keywords for judging relevance of a web site
    keywordList = open("keywords", "r").read().split(",")

    def __init__(self, path):
        self.urlList = []   # URLs to crawl
        self.visited = []   # visited URLs
        self.relevant = []  # relevant URLs according to the judging algorithm
        self.threadList = []    # concurrent thread IDs
        # dictionary of score of brands for a particular country, format: <brand name> : score
        self.brand_score = {}
        # human-judged relevant base URLs provided by the user
        self.baseURLs = open(path, "r").read().split("\n")
        # country domain of the brand score dictionary
        self.country = self.baseURLs.pop(0)

    def crawl(self):
        for baseURL in self.baseURLs:
            self.urlList.append(baseURL)
            t = Thread(target=self.crawler)
            t.start()
            self.threadList.append(t)

        for b in self.threadList:
            b.join()

        print str(len(self.relevant)) + " Relevant URLs:" + str(self.relevant)
        print(self.brand_score)

    # fetch html file of a given URL and measure the response time
    @staticmethod
    def geturl(url):
        url = urlparse.urlparse(url)

        host = url.hostname
        address = socket.gethostbyname(host)
        path = url.path
        if path == "":
            path = "/"

        port = url.port
        if port is None:
            port = 80

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # allow socket reuse
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(None)
        s.connect((address, port))
        # measure response time
        start_time = time.time()
        s.send("GET " + path + " HTTP/1.0\r\nHost: " + host + "\r\n\r\n")

        html = ""
        while True:
            data = (s.recv(100000000))
            if data == "":
                break
            html += data
        end_time = time.time()

        response_time = end_time - start_time

        # s.shutdown(socket.SHUT_RDWR)
        s.close()

        return [html, response_time]

    def backup(self, country, thread_ID=""):
        v = open(str(country) + "_Visited" + str(thread_ID) + ".txt", "w")
        r = open(str(country) + "_Relevant" + str(thread_ID) + ".txt", "w")

        v.writelines("Number of visited web sites;" + str(len(self.visited)) + "\n")
        v.writelines(["%s\n" % link for link in self.visited])
        v.close()

        r.writelines("Number of relevant web sites;" + str(len(self.relevant)) + "\n")
        r.writelines(["(Link: %s,RTT: %s)\n" % (link, rtt) for (link, rtt) in self.relevant])
        r.close()

    def crawler(self):
        #print(threading.current_thread().ident)
        while len(self.urlList) > 0 and len(self.relevant) < WebCrawler.PAGE_TO_CRAWL:
            url = self.urlList.pop(0)
            if url not in self.visited:
                self.visited.append(url)
                try:
                    #ip_address = socket.gethostbyname(urlparse.urlparse(url).hostname)
                    #record = IPWhois(ip_address)
                    #region = record.lookup()['asn_country_code']
                    #print str(url)
                    if True:
                        web_page = WebCrawler.geturl(url)
                        html = web_page[0]
                        rtt = web_page[1]
                        # judge relevance of the html
                        is_relevant = self.processHtml(html)
                        if is_relevant:
                            self.relevant.append((url, rtt))
                            # write status file in case cant achieve target number of web pages
                            if len(self.relevant) % WebCrawler.BACKUP_THRESHOLD == 0:
                                self.backup(self.country, threading.current_thread().ident)
                            # find all links in this html and append them to urlList
                            soup = BeautifulSoup(html, "html.parser")
                            links = soup.find_all("a", href=True)
                            for link in links:
                                raw_link = urlparse.urlparse(link["href"])
                                host = raw_link.hostname
                                path = raw_link.path
                                # internal links
                                if host is None:
                                    host = urlparse.urlparse(url).hostname
                                new_url = "http://" + host + path
                                self.urlList.append(new_url)
                except:
                    print "ERROR when dealing with: " + str(url)
                    print(traceback.format_exc())

    # return True if the web page is regarded as relevant
    def processHtml(self, html):
        # split into header & body fields, ignore the header of the reply
        html_body = html.split("\r\n\r\n")[1]
        # html_body = html_body.decode('gbk', 'ignore').encode('utf-8')
        # convert html to readable format
        article = Document(html_body).summary()
        # record title to judge relevance
        title = Document(html_body).title()
        # parse content of the web page
        soup = BeautifulSoup(article, "html.parser")
        text = soup.getText()
        # print "===TITLE===" + title + "\n===CONTENT===" + text

        # ignore small document
        if len(text) < WebCrawler.PAGE_LENGTH_LIMIT:
            return False

        # convert all words to lower case & tokenize the web page content
        tokens = nltk.word_tokenize(text.lower())
        # remove all stop words for accuracy
        filtered = [w for w in tokens if w not in stopwords.words('english')]

        # check if the title contains keywords
        is_title_relevant = False
        for word in self.brandList:
            if word in title.lower():
                is_title_relevant = True
                break

        if not is_title_relevant:
            return False

        '''
        tunable values
        '''
        # compute document relevance
        score = 0
        for word in filtered:
            if word in WebCrawler.brandList:
                score += 50
            if word in WebCrawler.keywordList:
                score += 20
        print("Score: " + str(score))

        # assign weight to document based on score
        if score < 100:
            return False
        elif score < 200:
            weight = 100
        elif score < 400:
            weight = 200
        elif score < 800:
            weight = 300
        elif score < 1600:
            weight = 400
        else:
            weight = 500
        print("Page Relevance: " + str(weight))
        '''
        end
        '''
        # number of times(percentage) a brand appear in the relevant web page, format: <brand name> : percentage
        brand_dict = {}
        total_count = 0
        # compute brand % over all brand counts
        for brand in WebCrawler.brandList:
            brand_count = 0
            for word in filtered:
                if brand in word:
                    brand_count += 1
            brand_dict[brand] = brand_count
            total_count += brand_count

        # convert occurrence to % format
        for brand, count in brand_dict.items():
            brand_dict[brand] = float(count)/total_count

        # compute contribution of each brand to the country domain
        for brand, percentage in brand_dict.items():
            if brand in self.brand_score:
                self.brand_score[brand] += weight * percentage
            else:
                self.brand_score[brand] = weight * percentage

        return True

    def get_brand_score(self):
        return self.brand_score

    def get_relevant_links(self):
        return self.relevant

    def get_visited_links(self):
        return self.visited

    def write_files(self, country):
        self.backup(country)

    def write_score(self, country):
        s = csv.writer(open(str(country) + "_Score.txt", "w"))
        for brand in self.brand_score:
            s.writerow([brand, self.brand_score[brand]])
