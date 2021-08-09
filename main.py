import os
import re
import tkinter as tk
from tkinter import PhotoImage, font
from tkinter.constants import ANCHOR
import webbrowser
from PIL import Image, ImageTk
from tkinter import ttk

import scraper
from db import DBConnector

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, "static/")


class IMDbScraper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title("IMDb Scraper - Top 250")

        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH)

        self.frm_films = tk.LabelFrame(self.container, text="Films")
        self.frm_films.grid(row=1, column=0, padx=20, pady=10, sticky=tk.NSEW)

        self.lbx_results = tk.Listbox(self.frm_films, width=70, height=30)
        self.lbx_results.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.listbox_scroll = ttk.Scrollbar(
            self.frm_films, orient="vertical", command=self.lbx_results.yview
        )
        self.listbox_scroll.grid(row=0, column=0, pady=5, sticky="nse")
        self.lbx_results.configure(yscrollcommand=self.listbox_scroll.set)

        tk.Label(
            self.container,
            text="Double click on a film title for further information.",
            bg="dark green",
            fg="white",
        ).grid(row=0, column=0, pady=10, ipadx=2, ipady=2, sticky=tk.NSEW)

        self.frm_data = tk.LabelFrame(self.container)
        self.frm_data.grid(row=2, column=0, padx=20, pady=10, sticky=tk.NSEW)

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

        self.lbl_info = tk.Label(
            self.container,
            text="Built by Ramón Vásquez - Powered by Python + MySQL",
            state="disabled",
            font="Default 8",
            anchor=tk.W,
        )
        self.lbl_info.grid(row=3, column=0, padx=20, pady=10, sticky=tk.NSEW)

        scraper.FilmScraper().get_basic_data()
        self.bindings()
        self.show_films()
        self.set_default_item()

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

        self.lbl_title.bind(
            "<Double-1>",
            lambda _: self.win_film(self.lbx_results.curselection()[0] + 1),
        )

        self.lbl_info.bind(
            "<Button-1>",
            lambda event: open_browser(
                event, "https://github.com/ramonfvasquez/imdb_scraper_python"
            ),
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
            self.lbx_results.insert(i, " %i. %s" % (i + 1, film[0]))

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

        self.frm_data = tk.Frame(self.container)
        self.frm_data.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        # POSTER

        self.cnv_poster = tk.Canvas(self.frm_data, width=400, height=570, bg="black")
        self.cnv_poster.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)

        # CAST & CREW

        self.frm_cast_and_crew = tk.LabelFrame(self.frm_data, text="Cast & Crew")
        self.frm_cast_and_crew.grid(
            row=0, column=1, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW
        )

        tk.Label(self.frm_cast_and_crew, text="Director:", font="Default 10 bold").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_director = tk.Label(self.frm_cast_and_crew, width=80, anchor=tk.W)
        self.lbl_director.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)

        tk.Label(self.frm_cast_and_crew, text="Writers:", font="Default 10 bold").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.NE
        )
        self.tree_writers = ttk.Treeview(self.frm_cast_and_crew, show="tree", height=4)
        self.tree_writers.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.tree_writers["columns"] = ["writer"]

        self.tree_writers.column("#0", width=0, stretch=tk.NO)
        self.tree_writers.column("writer", anchor=tk.NW, width=750, stretch=tk.NO)

        self.writers_scroll = ttk.Scrollbar(
            self.frm_cast_and_crew, orient="vertical", command=self.tree_writers.yview
        )
        self.writers_scroll.grid(row=1, column=1, pady=5, sticky="nse")
        self.tree_writers.configure(yscrollcommand=self.writers_scroll.set)

        tk.Label(self.frm_cast_and_crew, text="Cast:", font="Default 10 bold").grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.NE
        )
        self.tree_cast = ttk.Treeview(self.frm_cast_and_crew, height=20)
        self.tree_cast.grid(row=2, column=1, padx=5, pady=5, sticky=tk.NSEW)
        self.tree_cast["columns"] = ["actor", "character"]

        self.tree_cast.column("#0", width=0, stretch=tk.NO)
        self.tree_cast.column("actor", anchor=tk.NW, width=250, stretch=tk.NO)
        self.tree_cast.column("character", anchor=tk.NW, width=500, stretch=tk.NO)

        self.tree_cast.heading("#0", text="", anchor=tk.CENTER)
        self.tree_cast.heading("actor", text="Actor", anchor=tk.CENTER)
        self.tree_cast.heading("character", text="Character", anchor=tk.CENTER)

        self.cast_scroll = ttk.Scrollbar(
            self.frm_cast_and_crew, orient="vertical", command=self.tree_cast.yview
        )
        self.cast_scroll.grid(row=2, column=1, pady=5, sticky="nse")
        self.tree_cast.configure(yscrollcommand=self.cast_scroll.set)

        # TECHNICAL DATA

        self.frm_technical_details = tk.LabelFrame(
            self.frm_data, text="Technical Details"
        )
        self.frm_technical_details.grid(
            row=1, column=1, padx=10, pady=10, ipadx=5, ipady=5, sticky=tk.NSEW
        )

        tk.Label(
            self.frm_technical_details, text="Country:", font="Default 10 bold"
        ).grid(row=3, column=0, padx=5, pady=5, sticky=tk.NE)

        self.frm_country = tk.Frame(self.frm_technical_details)
        self.frm_country.grid(row=3, column=1, sticky=tk.W)

        tk.Label(
            self.frm_technical_details, text="Language:", font="Default 10 bold"
        ).grid(row=4, column=0, padx=5, pady=5, sticky=tk.NE)
        self.lbl_language = tk.Label(self.frm_technical_details, width=80, anchor=tk.W)
        self.lbl_language.grid(row=4, column=1, padx=5, pady=5, sticky=tk.NSEW)

        tk.Label(
            self.frm_technical_details, text="Color:", font="Default 10 bold"
        ).grid(row=5, column=0, padx=5, pady=5, sticky=tk.NE)
        self.lbl_color = tk.Label(self.frm_technical_details, anchor=tk.W)
        self.lbl_color.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(
            self.frm_technical_details, text="Runtime:", font="Default 10 bold"
        ).grid(row=6, column=0, padx=5, pady=5, sticky=tk.NE)
        self.lbl_runtime = tk.Label(self.frm_technical_details, width=80, anchor=tk.W)
        self.lbl_runtime.grid(row=6, column=1, padx=5, pady=5, sticky=tk.NSEW)

        self.show_poster()
        self.show_rating()
        self.show_full_data()
        self.bindings()

    def bindings(self):  # Sets the bindings for the widgets
        self.cnv_poster.bind(
            "<Button-1>",
            lambda event: open_browser(
                "https://www.imdb.com/title/%s/reference" % (self.film_id)
            ),
        )

        self.tree_writers.bindtags((self.tree_writers, self.frm_cast_and_crew, "all"))
        self.tree_writers.bind(
            "<Enter>", lambda event: self._bound_to_mousewheel(event, self.tree_writers)
        )
        self.tree_writers.bind(
            "<Leave>",
            lambda event: self._unbound_to_mousewheel(event, self.tree_writers),
        )
        self.tree_cast.bindtags((self.tree_cast, self.frm_cast_and_crew, "all"))
        self.tree_cast.bind(
            "<Enter>", lambda event: self._bound_to_mousewheel(event, self.tree_cast)
        )
        self.tree_cast.bind(
            "<Leave>", lambda event: self._unbound_to_mousewheel(event, self.tree_cast)
        )

    def poster_available(self):  # Creates the film poster
        self.cnv_poster.create_image(200, 265, anchor=tk.CENTER, image=self.poster)

    def poster_unavailable(self):  # Creates a message for unavailable posters
        unavailable = "Oh, no! The poster is not available! :("

        self.cnv_poster.create_text(
            340,
            265,
            text=unavailable,
            anchor=tk.NE,
            font="Default 10 bold",
            fill="red",
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
        data = scraper.FilmScraper().get_crew(self.film_id)

        director = data["director"]

        self.lbl_director["text"] = ", ".join(sorted(director))  # Directors

        writers = data["writers"]  # Writers
        self.show_writers(writers, director)

        cast = data["cast"]  # Full cast
        self.show_actors(cast)

        (
            runtime,
            countries,
            languages,
            color,
            social,
        ) = scraper.FilmScraper().scrape_technical_data(self.film_id)

        self.show_social_media(social)

        countries = sorted(countries.split(", "))  # Countries
        self.show_flags(countries)

        # Languages
        self.lbl_language["text"] = ", ".join(sorted(languages.split(", ")))

        self.lbl_color["text"] = color  # Color
        if "Black" in color.capitalize():
            self.lbl_color.config(bg="black", fg="white")
        elif "Color" in color.capitalize():
            self.lbl_color["fg"] = "red"

        self.lbl_runtime["text"] = runtime  # Runtime

    def show_poster(self):
        self.cnv_poster.create_text(
            333,
            10,
            text="Click on the poster to access the film's IMDb page.",
            anchor=tk.NE,
            font="Default 8",
            fill="white",
        )

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

    def show_rating(self):
        # self.img = PhotoImage(file="%sicons/imdb.png" % (STATIC_ROOT))
        im = Image.open("%sicons/imdb.png" % (STATIC_ROOT)).resize((64, 64))
        self.img = ImageTk.PhotoImage(im)
        self.cnv_poster.create_image(135, 541, anchor=tk.CENTER, image=self.img)

        self.cnv_poster.create_text(
            290,
            530,
            text="Rating: %s" % (self.rating),
            anchor=tk.NE,
            font="Default 14 bold",
            fill="white",
        )

    def show_social_media(self, social):
        """
        If the selected film has social media, inserts a frame, and within it
        some labels depending on the number of sites. For every multiple of 4,
        the new labels are placed in a new column. Binds each label with a link
        to its corresponding URL.
        """
        if social:
            self.frm_social = tk.LabelFrame(self.frm_data, text="Social Media")
            self.frm_social.grid(
                row=1, column=0, padx=10, pady=10, ipadx=10, ipady=5, sticky=tk.NSEW
            )

            eval_link = lambda x: (lambda p: open_browser(x))
            i = 0
            j = 0
            for key, value in social.items():
                lbl_social = tk.Label(
                    self.frm_social, fg="blue", anchor=tk.W, cursor="hand2"
                )
                lbl_social.grid(row=i, column=j, padx=5, pady=5, sticky=tk.NSEW)
                lbl_social.bind("<Button-1>", eval_link(value))

                self.social_icon = None

                file_name = get_social_media_file_name(key)
                text = get_social_media_text(key)

                if file_name:
                    img = Image.open(
                        "%sicons/%s.png" % (STATIC_ROOT, file_name)
                    ).resize((16, 16))
                    self.social_icon = ImageTk.PhotoImage(img)

                    lbl_social["text"] = " " + text
                    lbl_social["compound"] = tk.LEFT
                    lbl_social["image"] = self.social_icon
                    lbl_social.image = self.social_icon

                else:
                    lbl_social["text"] = text

                i += 1

                if i % 4 == 0:
                    i = 0
                    j += 1

    def show_writers(self, writers, directors):  # Shows the writers in a treeview
        for i, writer in enumerate(writers):
            self.tree_writers.insert(
                parent="",
                index=i,
                iid=i,
                values=(writer,),
                tags=("writer",) if writer in directors else "",
            )
        self.tree_writers.tag_configure("writer", font="Default 10 bold")

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


def get_social_media_file_name(site):
    social = ""
    if "Facebook" in site.title():
        social = "facebook"
    elif "Instagram" in site.title():
        social = "instagram"
    elif "Tumblr" in site.title():
        social = "tumblr"
    elif "Twitter" in site.title():
        social = "twitter"
    elif "Youtube" in site.title():
        social = "youtube"

    return social


def get_social_media_text(site):
    text = ""
    if not "Official Site" in site.title():
        text = site.replace("Official ", "")
    else:
        text = site

    if len(text) > 20:
        text = site[:14] + "..."
    else:
        text = text

    return text


def open_browser(url):
    webbrowser.open(url)


def main():
    database = DBConnector()
    database.create_db()
    database.create_table()
    app = IMDbScraper()


if __name__ == "__main__":
    main()
