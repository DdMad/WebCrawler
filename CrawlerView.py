from Tkinter import *
import WebCrawler

titles = ['Country', 'iPhone', 'Samsung', 'Nexus', 'Lumia', 'HTC', 'Sony', 'LG', 'Xiaomi', 'Huawei']
countries = ['UK', 'US', 'Singapore', 'India', 'Canada', 'Australia']

brand = ['iphone', 'samsung', 'nexus', 'lumia', 'htc', 'sony', 'lg', 'xiaomi', 'huawei']
url = ['ukurl', 'usurl', 'sgurl', 'inurl', 'caurl', 'auurl']

class App:

    def __init__(self, master, rows=6, columns=10):

        self.root = master

        start = Button(master, text="Start", command=self.start)
        start.grid(row=0, column=0)

        export = Button(master, text="Export", command=self.export)
        export.grid(row=0, column=1)

        for column in range(columns):
            title = Label(master, text=titles[column], borderwidth=1)
            title.grid(row=1, column=column, sticky="nsew", padx=1, pady=1)

        for row in range(rows):
            content = Label(master, text=countries[row], borderwidth=1)
            content.grid(row=2+row, column=0, sticky="nsew", padx=1, pady=1)

    def setTableCell(self, row, column, score):
        cell = Label(self.root, text=score)
        cell.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)

    def start(self):
        print "Start Crawling!"
        # self.setTableCell(4, 4, "test")
        for country in range(6):
            crawler = WebCrawler.WebCrawler(url[country])
            crawler.crawl()
            result = crawler.get_brand_score()

            if result:
                for bd in range(9):
                    if result[brand[bd]]:
                        self.setTableCell(country+2, bd+1, float("{0:.2f}".format(result[brand[bd]])))
                    else:
                        self.setTableCell(country+2, bd+1, 0)
        # crawler = WebCrawler.WebCrawler("ukurl")
        # crawler.crawl()
        # result = crawler.get_brand_score()
        #
        # print result

        # if result:
        #     for bd in range(9):
        #         if result[brand[bd]]:
        #             self.setTableCell(2, bd+1, float("{0:.2f}".format(result[brand[bd]])))
        #         else:
        #             self.setTableCell(2, bd+1, 0)


    def export(self):
        print "Export!"

root = Tk()
root.title("Web Crawler")

app = App(root)

# crawler = WebCrawler.WebCrawler("")
# result = crawler.crawl()
# print result["iphone"]





root.mainloop()