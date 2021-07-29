import os
import re
import tkinter as tk
import webbrowser
from PIL import Image, ImageTk
from tkinter import ttk

import scraper
from db import DBConnector

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, "")


class IMDbScraper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("IMDb Scraper - Top 250")

        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH)

        self.frm_films = tk.LabelFrame(self.container, text="Films")
        self.frm_films.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        self.lbx_results = tk.Listbox(self.frm_films, width=70, height=30)
        self.lbx_results.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.listbox_scroll = ttk.Scrollbar(
            self.frm_films, orient="vertical", command=self.lbx_results.yview
        )
        self.listbox_scroll.grid(row=0, column=0, pady=5, sticky="nse")
        self.lbx_results.configure(yscrollcommand=self.listbox_scroll.set)

        self.frm_data = tk.LabelFrame(self.container)
        self.frm_data.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NSEW)

        tk.Label(self.frm_data, text="Title:", font="Default 10 bold").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_title = tk.Label(self.frm_data, width=60, anchor=tk.W)
        self.lbl_title.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.frm_data, text="Year:", font="Default 10 bold").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_year = tk.Label(self.frm_data, width=60, anchor=tk.W)
        self.lbl_year.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.frm_data, text="Director:", font="Default 10 bold").grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_director = tk.Label(self.frm_data, width=60, anchor=tk.W)
        self.lbl_director.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.frm_data, text="Stars:", font="Default 10 bold").grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_stars = tk.Label(self.frm_data, width=60, anchor=tk.W)
        self.lbl_stars.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.frm_data, text="Rating:", font="Default 10 bold").grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_rating = tk.Label(self.frm_data, width=60, anchor=tk.W)
        self.lbl_rating.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        scraper.FilmScraper().get_basic_film_data()
        self.show_films()
        self.set_default_item()
        self.bindings()

        self.root.mainloop()

    def bindings(self):  # Sets the bindings for the widgets
        self.lbx_results.bind(
            "<<ListboxSelect>>",
            lambda _: self.show_film_data(self.lbx_results.curselection()[0] + 1)
            if self.lbx_results.curselection()
            else "",
        )
        self.lbx_results.bind(
            "<Double-1>",
            lambda _: self.win_film(self.lbx_results.curselection()[0] + 1),
        )

    def set_default_item(self):  # Selects the first element of the film listbox
        self.lbx_results.selection_set(0)
        self.lbx_results.event_generate("<<ListboxSelect>>")

    def show_film_data(self, id):
        """
        Shows the basic data of the selected film in the frame below
        the film listbox.
        """
        data = DBConnector().search(id)[0]

        self.lbl_title["text"] = data[1]  # Film title
        self.lbl_year["text"] = data[3]  # Release year
        self.lbl_director["text"] = data[4]  # Main director
        self.lbl_stars["text"] = data[5]  # Stars
        self.lbl_rating["text"] = data[6]  # IMDb Rating

    def show_films(self):  # Shows the scraped films in the film listbox
        self.lbx_results.delete(0, tk.END)
        films = DBConnector().read_table()

        for i, film in enumerate(films):
            self.lbx_results.insert(i, film[0])

    def win_film(self, id):
        """
        Opens the full film data window. The main window is disabled while the
        film window is open.
        """
        win = FilmWindow(id, master=self.root)
        win.transient(self.root)
        try:
            win.grab_set()
        except:
            pass
        self.root.wait_window(win)


class FilmWindow(tk.Toplevel):
    def __init__(self, id, master=None):
        tk.Toplevel.__init__(self, master=master)
        self.data = DBConnector().search(id)[0]
        self.film_title = "[%s] %s" % (self.data[3], self.data[1])
        self.film_id = self.data[2]
        self.stars = self.data[5].split(", ")
        self.rating = self.data[6]
        self.url = self.data[7]

        self.resizable(False, False)
        self.title(self.film_title)

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.cnv_poster = tk.Canvas(self.container, width=400, height=500, bg="black")
        self.cnv_poster.grid(row=0, column=0, padx=20, pady=20, sticky=tk.NSEW)

        self.frm_data = tk.LabelFrame(self.container, text="Cast & Crew")
        self.frm_data.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NSEW)

        tk.Label(self.frm_data, text="Director:", font="Default 10 bold").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_director = tk.Label(self.frm_data, width=80, anchor=tk.W)
        self.lbl_director.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)

        tk.Label(self.frm_data, text="Writers:", font="Default 10 bold").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NE
        )
        self.tree_writers = ttk.Treeview(self.frm_data, show="tree", height=4)
        self.tree_writers.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.tree_writers["columns"] = ["writer"]

        self.tree_writers.column("#0", width=0, stretch=tk.NO)
        self.tree_writers.column("writer", anchor=tk.NW, width=750, stretch=tk.NO)

        self.writers_scroll = ttk.Scrollbar(
            self.frm_data, orient="vertical", command=self.tree_writers.yview
        )
        self.writers_scroll.grid(row=1, column=1, pady=5, sticky="nse")
        self.tree_writers.configure(yscrollcommand=self.writers_scroll.set)

        tk.Label(self.frm_data, text="Cast:", font="Default 10 bold").grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NE
        )
        self.tree_cast = ttk.Treeview(self.frm_data, height=20)
        self.tree_cast.grid(row=2, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.tree_cast["columns"] = ["actor", "character"]

        self.tree_cast.column("#0", width=0, stretch=tk.NO)
        self.tree_cast.column("actor", anchor=tk.NW, width=250, stretch=tk.NO)
        self.tree_cast.column("character", anchor=tk.NW, width=500, stretch=tk.NO)

        self.tree_cast.heading("#0", text="", anchor=tk.CENTER)
        self.tree_cast.heading("actor", text="Actor", anchor=tk.CENTER)
        self.tree_cast.heading("character", text="Character", anchor=tk.CENTER)

        self.cast_scroll = ttk.Scrollbar(
            self.frm_data, orient="vertical", command=self.tree_cast.yview
        )
        self.cast_scroll.grid(row=2, column=1, pady=5, sticky="nse")
        self.tree_cast.configure(yscrollcommand=self.cast_scroll.set)

        tk.Label(self.frm_data, text="Country:", font="Default 10 bold").grid(
            row=3, column=0
        )

        self.frm_country = tk.Frame(self.frm_data)
        self.frm_country.grid(row=3, column=1, sticky=tk.W)

        tk.Label(self.frm_data, text="Runtime:", font="Default 10 bold").grid(
            row=4, column=0
        )
        self.lbl_runtime = tk.Label(self.frm_data, width=80, anchor=tk.W)
        self.lbl_runtime.grid(row=4, column=1, padx=5, pady=5, sticky=tk.NSEW)

        self.show_poster()
        self.show_full_data()
        self.bindings()

    def bindings(self):  # Sets the bindings for the widgets
        self.cnv_poster.bind("<Button-1>", self.open_browser)

        self.tree_writers.bindtags((self.tree_writers, self.frm_data, "all"))
        self.tree_writers.bind(
            "<Enter>", lambda event: self._bound_to_mousewheel(event, self.tree_writers)
        )
        self.tree_writers.bind(
            "<Leave>",
            lambda event: self._unbound_to_mousewheel(event, self.tree_writers),
        )
        self.tree_cast.bindtags((self.tree_cast, self.frm_data, "all"))
        self.tree_cast.bind(
            "<Enter>", lambda event: self._bound_to_mousewheel(event, self.tree_cast)
        )
        self.tree_cast.bind(
            "<Leave>", lambda event: self._unbound_to_mousewheel(event, self.tree_cast)
        )

    def open_browser(self, event):  # Opens the IMDb page of the selected film
        webbrowser.open("https://www.imdb.com/title/%s/reference" % (self.film_id))

    def poster_available(self):  # Creates the film poster
        self.cnv_poster.create_text(
            240,
            550,
            text="Rating: %s" % (self.rating),
            anchor=tk.NE,
            font="Default 10 bold",
            fill="white",
        )
        self.cnv_poster.create_image(200, 270, anchor=tk.CENTER, image=self.poster)

    def poster_unavailable(self):  # Creates a message for unavailable posters
        unavailable = "Oh, no! The poster is not available! :("

        self.cnv_poster.create_text(
            330,
            270,
            text=unavailable,
            anchor=tk.NE,
            font="Default 10 bold",
            fill="red",
        )
        self.cnv_poster.create_text(
            240,
            550,
            text="Rating: %s" % (self.rating),
            anchor=tk.NE,
            font="Default 10 bold",
            fill="white",
        )

    def show_actors(self, cast):  # Shows the full cast in a treeview
        i = 0
        for actor, character in cast.items():
            self.tree_cast.insert(
                parent="",
                index=i,
                iid=i,
                values=(actor, character),
                tags=("star",) if actor in self.stars else "",
            )
            i += 1
        # Bolds the names of the stars
        self.tree_cast.tag_configure("star", font="Default 10 bold")

    def show_flags(self, countries):
        for i, country in enumerate(countries):
            path = "%sflags/%s" % (
                STATIC_ROOT,
                scraper.get_country_image_name(country),
            )

            if os.path.isfile(path):
                img = Image.open(path).resize((16, 16))
                self.flag = ImageTk.PhotoImage(img)
            else:
                self.flag = None

            lbl_country = tk.Label(
                self.frm_country,
                text=(" " if self.flag else "") + country,
                compound=tk.LEFT,
                image=self.flag,
                anchor=tk.W,
            )
            lbl_country.grid(row=3, column=i + 1, padx=5, pady=5, sticky=tk.NSEW)
            lbl_country.image = self.flag

    def show_full_data(self):  # Shows the scraped data of the selected film
        data = scraper.FilmScraper().get_full_film_data(self.film_id)

        self.lbl_director["text"] = ", ".join(sorted(data["director"]))  # Directors

        writers = data["writers"]  # Writers
        self.show_writers(writers)

        cast = data["cast"]  # Full cast
        self.show_actors(cast)

        runtime, countries = scraper.FilmScraper().get_additional_data(self.film_id)

        countries = sorted(countries.split(", "))  # Countries
        self.show_flags(countries)

        self.lbl_runtime["text"] = runtime  # Runtime

    def show_poster(self):
        # Shows the film poster if available, if not, shows a message
        try:
            self.poster = scraper.WebImage(self.url).get()
            if self.poster.width() > 100 and self.poster.height() > 100:
                # If the poster is too little, shows a message instead of the poster
                self.poster_available()
            else:
                self.poster_unavailable()
        except:
            self.url = re.sub("@.*", "@@._V1_FMjpg_UY473_.jpg", self.url)
            self.poster = scraper.WebImage(self.url).get()
            self.poster_available()

    def show_writers(self, writers):  # Shows the writers in a treeview
        for i, writer in enumerate(writers):
            self.tree_writers.insert(parent="", index=i, iid=i, values=(writer,))

    def _bound_to_mousewheel(self, event, listbox):  # Binds widgets to the mousewheel
        # On Linux
        listbox.bind_all(
            "<Button-4>", lambda event: self._on_mousewheel_down(event, listbox)
        )
        listbox.bind_all(
            "<Button-5>", lambda event: self._on_mousewheel_up(event, listbox)
        )

        # On Windows
        listbox.bind_all(
            "<MouseWheel>", lambda event: self._on_mousewheel_up(event, listbox)
        )

    def _on_mousewheel_down(self, event, listbox):  # Mousewheel scrolling down
        listbox.yview_scroll(-1, "units")

    def _on_mousewheel_up(self, event, listbox):  # Mousewheel scrolling up
        listbox.yview_scroll(1, "units")

    def _unbound_to_mousewheel(self, event, listbox):
        # Unbinds widgets from the mousewheel

        # On Linux
        listbox.unbind_all("<Button-4>")
        listbox.unbind_all("<Button-5>")

        # On Windows
        listbox.unbind_all("<MouseWheel>")


def main():
    database = DBConnector()
    database.create_db()
    database.create_table()
    app = IMDbScraper()


if __name__ == "__main__":
    main()
