import nltk
import socket
import urlparse
from threading import Thread
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from readability.readability import Document


urlList = []
visited = []
relevant = []
threadList = []
THRESHOLD = 50

# brand dictionary of a particular country
country = {}

brandList = open("brands", "r").read().split(",")
# read in all the keywords for judge a web site as relevant
keywordList = open("keywords", "r").read().split(",")
# open file contains base urls to begin crawl with, each country has one base url
baseURLs = open("baseURLs", "r").read().split("\n")


# fetch html file for a given url
def geturl(url):
    url = urlparse.urlparse(url)

    host = url.hostname
    ip_addr = socket.gethostbyname(host)
    path = url.path
    if path == "":
        path = "/"

    port = url.port
    if port is None:
        port = 80

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # allow socket reuse
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.connect((ip_addr, port))
    s.send("GET " + path + " HTTP/1.0\r\nHost: " + host + "\r\n\r\n")

    html = ""
    while True:
        data = (s.recv(100000000))
        if data == "":
            break
        html += data

    s.shutdown(socket.SHUT_RDWR)
    s.close()

    return html


#  simple web crawler
def crawler(country_dict):
    while len(urlList) > 0 and len(relevant) < THRESHOLD:
        url = urlList.pop(0)
        if url not in visited:
            visited.append(url)
            try:
                html = geturl(url)
                # judge relevance of the html
                is_relevant = processHtml(html, country_dict)
                if is_relevant:
                    relevant.append(url)
                    # find all links in this html and append to urlList
                    soup = BeautifulSoup(html, "html.parser")
                    links = soup.find_all("a", href=True)
                    for link in links:
                        raw_link = urlparse.urlparse(link["href"])
                        host = raw_link.hostname
                        path = raw_link.path
                        if host is None:
                            host = urlparse.urlparse(url).hostname
                        new_url = "http://" + host + path
                        urlList.append(new_url)
                    print(urlList)
            except:
                print(url)


def processHtml(html, country_dict):
    html_body = html.split("\r\n\r\n")[1]
    # convert html to readable format
    article = Document(html_body).summary()
    # record title for judge relevance
    title = Document(html_body).title()
    # parse web page article
    soup = BeautifulSoup(article, "lxml")
    text = soup.text
    print(title, text)
    # do not consider small document
    if len(text) < 500:
        return False

    # convert to lower case & tokenize web page brands
    tokens = nltk.word_tokenize(text.lower())
    # remove all stop words
    filtered = [w for w in tokens if w not in stopwords.words('english')]

    # check keyword in title
    is_title_relevant = False
    print(title.lower())
    for word in brandList:
        if word in title.lower():
            is_title_relevant = True
            break

    if not is_title_relevant:
        return False

    # compute document relevance
    score = 0
    for word in filtered:
        if word in brandList:
            score += 10
        if word in keywordList:
            score += 5
    print("score " + str(score))
    # assign weight to document based on score
    weight = 0
    if score < 100:
        return False
    elif score < 200:
        weight = 200
    elif score < 300:
        weight = 300
    elif score < 400:
        weight = 400
    else:
        weight = 500
    print("weight " + str(weight))

    brand_dict = {}
    total_count = 0
    # compute brand % over all brand counts
    for brand in brandList:
        brand_count = 0
        for word in filtered:
            if brand in word:
                brand_count += 1
        brand_dict[brand] = brand_count
        total_count += brand_count

    # compute contribution for each brand to the country domain
    for brand, count in brand_dict.items():
        brand_dict[brand] = float(count)/total_count

    for brand, percentage in brand_dict.items():
        if brand in country_dict:
            country_dict[brand] += weight * percentage
        else:
            country_dict[brand] = weight * percentage

    return True


for baseURL in baseURLs:
    urlList.append(baseURL)
    t = Thread(target=crawler, args=(country,))
    t.start()
    threadList.append(t)
    print(len(threadList))

for b in threadList:
    b.join()
print(visited)
print(relevant)
print(country)
