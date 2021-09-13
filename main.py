"""Basic scraper for IMDb's Top 250 films.

It is fully built on Tkinter.

When loading, the program scrapes the top 250 film list and shows some
basic info for each film when selected. This data is temporarily saved
into a MySQL table.

Double-clicking on any film will open a second window that shows more
detailed information about the movie, i.e., directors, writers, full
cast, some technical data, poster, and social media links. This data
is saved into a dictionary, instead of a database.
"""

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
