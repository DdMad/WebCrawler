from Tkinter import *

titles = ['Country', 'iPhone', 'Samsung', 'HTC', 'LG', 'Xiaomi', 'Huawei', 'Sony', 'Nexus', 'Lumia']
countries = ['UK', 'US', 'Singapore', 'India', 'Canada', 'Australia']

class App:

    def __init__(self, master, rows=6, columns=10):

        start = Button(master, text="Start", command=self.start)
        start.grid(row=0)

        for column in range(columns):
            title = Label(master, text=titles[column], borderwidth=1)
            title.grid(row=1, column=column, sticky="nsew", padx=1, pady=1)

        for row in range(rows):
            content = Label(master, text=countries[row], borderwidth=1)
            content.grid(row=2+row, column=0, sticky="nsew", padx=1, pady=1)

    def start(self):
        print "Start Crawling!"

root = Tk()
root.title("Web Crawler")

app = App(root)

root.mainloop()