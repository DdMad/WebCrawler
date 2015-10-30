from Tkinter import *
import WebCrawler
import csv

titles = ['Country', 'iPhone', 'Samsung', 'Nexus', 'Lumia', 'HTC', 'Sony', 'LG', 'Xiaomi', 'Huawei']
countries = ['UK', 'US', 'Singapore', 'India', 'Canada', 'Australia']

brand = ['iphone', 'samsung', 'nexus', 'lumia', 'htc', 'sony', 'lg', 'xiaomi', 'huawei']
url = ['ukurl', 'usurl', 'sgurl', 'inurl', 'caurl', 'auurl']

class App:

    def __init__(self, master, rows=6, columns=10):

        self.root = master

        master.minsize(width=700, height=320)
        master.maxsize(width=700, height=320)

        start = Button(master, text="Start", command=self.start)
        start.grid(row=9, column=0, pady=5, padx=5)

        export = Button(master, text="Export", command=self.export)
        export.grid(row=9, column=1, pady=5, padx=5)

        clear = Button(master, text="Clear", command=self.clear)
        clear.grid(row=9, column=2, pady=5, padx=5)

        exit = Button(master, text="Exit", command=master.quit)
        exit.grid(row=9, column=3, pady=5, padx=5)

        for column in range(columns):
            title = Label(master, text=titles[column], borderwidth=1, font=("Helvetica", 15))
            title.grid(row=0, column=column, sticky="nsew", padx=10, pady=5)

        for row in range(rows):
            content = Label(master, text=countries[row], borderwidth=1, font=("Helvetica", 15))
            content.grid(row=2+row, column=0, sticky="nsew", padx=5, pady=10)

        self.clear()

    def setTableCell(self, row, column, score):
        cell = Label(self.root, text=score)
        cell.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)

    def start(self):
        print "Start Crawling!"
        for country in range(6):
            print("######################### " + url[country] + " #########################")
            crawler = WebCrawler.WebCrawler(url[country])
            crawler.crawl()
            crawler.write_files(countries[country])
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

        with open('test.csv', 'w', newline='') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows()

    def clear(self):
        for country in range(6):
            for bd in range(9):
                self.setTableCell(country+2, bd+1, 0)


root = Tk()
root.title("Web Crawler")

app = App(root)

root.mainloop()