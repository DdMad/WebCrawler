import socket
import urlparse
from bs4 import BeautifulSoup
from readability.readability import Document


def geturl(url):
    url = urlparse.urlparse(url)
    print(url)

    host = url.hostname
    path = url.path
    if path == "":
        path = "/"
    port = url.port
    if port is None:
        port = 80

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # allow socket reuse
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.connect((host, port))
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


brandList = open("brands", "r").read().split(",")
# read in all the keywords for judge a web site as relevant
keywordList = open("keywords", "r").read().split(",")
# open file contains base urls to begin crawl with, each country has one base url
baseURLs = open("baseURLs", "r").read().split("\n")

visited = []

# for each base url, fetch the web page for content processing
while len(baseURLs) > 0 and len(visited) < 50:
    url = baseURLs.pop(0)
    try:
        if url not in visited:
            visited.append(url)
            html_text = geturl(url)
            print(html_text)
            # trim http response header
            html_body = html_text.split("\r\n\r\n")[1]
            # convert html to readable format
            article = Document(html_body).summary()
            print(article)
            # record title for judge relevance
            title = Document(html_body).short_title()
            # parse page brands
            soup = BeautifulSoup(article, "lxml")
            text = soup.text
            print(len(text), text)
            links = BeautifulSoup(html_body,"html.parser").find_all("a", href=True)
            for link in links:
                rawLink = urlparse.urlparse(link["href"])
                h = rawLink.hostname
                p = rawLink.path
                if h is None:
                    h = urlparse.urlparse(url).hostname
                new_url = "http://" + h + p
                baseURLs.append(new_url)
    except:
        print(url)
        pass
print(len(visited), visited)
