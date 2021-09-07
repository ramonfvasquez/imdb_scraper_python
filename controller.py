from tkinter import Tk

from view import MainWindow


class IMDbScraper:
    def __init__(self, root):
        self.root = root
        MainWindow(self.root)


if __name__ == "__main__":
    root = Tk()
    app = IMDbScraper(root)
    root.mainloop()
