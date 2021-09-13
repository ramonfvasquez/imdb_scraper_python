"""View module for the program's MVC pattern.

Classes included: MainWindow, FilmWindow, and ImageSizeError (exception).
"""

import os
import webbrowser
from PIL import Image, ImageTk
from tkinter import Canvas, Frame, Label, LabelFrame, Listbox, Toplevel
from tkinter.ttk import Scrollbar, Treeview

from model import *

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, "static/")


class MainWindow:
    """Main window of the program.

    It has a a frame with a listbox in which the top-250 films are inserted, and
    a second frame that shows the basic data of the selected film, i.e title,
    year, stars, and rating.
    """

    def __init__(self, root):
        self.root = root
        self.root.resizable(False, False)
        self.root.title("IMDb Scraper - Top 250")

        self.container = Frame(self.root)
        self.container.pack(fill="both")

        self.frm_films = LabelFrame(self.container, text="Films")
        self.frm_films.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.lbx_films = Listbox(self.frm_films, width=70, height=30)
        self.lbx_films.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.lbx_films.bind(
            "<<ListboxSelect>>",
            lambda _: self.show_film_data(self.lbx_films.curselection()[0] + 1)
            if self.lbx_films.curselection()
            else "",
        )
        self.lbx_films.bind(
            "<Double-1>",
            lambda _: self.win_film(self.lbx_films.curselection()[0] + 1),
        )

        self.listbox_scroll = Scrollbar(
            self.frm_films, orient="vertical", command=self.lbx_films.yview
        )
        self.listbox_scroll.grid(row=0, column=0, pady=5, sticky="nse")

        self.lbx_films.configure(yscrollcommand=self.listbox_scroll.set)

        text1 = "Double click on a film title for further information."
        Label(self.container, text=text1, font="Default 8").grid(
            row=0, column=0, pady=10, sticky="nsew"
        )

        self.frm_film_info = LabelFrame(self.container)
        self.frm_film_info.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        Label(self.frm_film_info, text="Title:", font="Default 10 bold").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.lbl_title = Label(self.frm_film_info, width=60, anchor="w")
        self.lbl_title.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.lbl_title.bind(
            "<Double-1>",
            lambda _: self.win_film(self.lbx_films.curselection()[0] + 1),
        )

        Label(self.frm_film_info, text="Year:", font="Default 10 bold").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.lbl_year = Label(self.frm_film_info, width=60, anchor="w")
        self.lbl_year.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        Label(self.frm_film_info, text="Director:", font="Default 10 bold").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.lbl_director = Label(self.frm_film_info, width=60, anchor="w")
        self.lbl_director.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        Label(self.frm_film_info, text="Stars:", font="Default 10 bold").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        self.lbl_stars = Label(self.frm_film_info, width=60, anchor="w")
        self.lbl_stars.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        Label(self.frm_film_info, text="Rating:", font="Default 10 bold").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        self.lbl_rating = Label(self.frm_film_info, width=60, anchor="w")
        self.lbl_rating.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        text2 = "Built by Ramón Vásquez - Powered by Python + MySQL"
        self.lbl_info = Label(
            self.container, text=text2, state="disabled", font="Default 8", anchor="w"
        )
        self.lbl_info.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        self.lbl_info.bind(
            "<Button-1>",
            lambda _: open_browser(
                "https://github.com/ramonfvasquez/imdb_scraper_python"
            ),
        )

        FilmList().get_basic_data()
        self.show_films()
        self.set_default_item()

    def set_default_item(self):
        """Select the first element of the film listbox."""

        self.lbx_films.selection_set(0)
        self.lbx_films.event_generate("<<ListboxSelect>>")

    def show_film_data(self, id):
        """
        Show the basic data of the selected film in the frame below the film
        listbox.
        """

        data = DataBase().search(id)[0]

        self.lbl_title["text"] = data[1]  # Film title
        self.lbl_year["text"] = data[3]  # Release year
        self.lbl_director["text"] = data[4]  # Main director
        self.lbl_stars["text"] = data[5]  # Stars
        self.lbl_rating["text"] = data[6]  # IMDb Rating

    def show_films(self):
        """Show the scraped films in the film listbox."""

        self.lbx_films.delete(0, "end")
        films = DataBase().read_table()

        for i, film in enumerate(films):
            self.lbx_films.insert(i, " %i. %s" % (i + 1, film[0]))

    def win_film(self, id):
        """
        Open the full-film-data window. The main window is disabled while the
        film window is open.
        """

        win = FilmWindow(id, master=self.root)
        win.transient(self.root)
        try:
            win.grab_set()
        except:
            pass
        self.root.wait_window(win)


class FilmWindow(Toplevel):
    """Shows full film's data.

    It has a canvas for the poster and three frames:
        -cast and crew;
        -social media links (it is only created if the film has any; if not, this
        frame will not appear);
        -technical data (countries, languages, color, and runtime).
    """

    def __init__(self, id, master=None):
        Toplevel.__init__(self, master=master)
        self.data = DataBase().search(id)[0]
        self.film_title = "[%s] %s" % (self.data[3], self.data[1])
        self.film_id = self.data[2]
        self.stars = self.data[5].split(", ")
        self.rating = self.data[6]
        self.url = self.data[7]
        self.film = Film(self.film_id)

        self.resizable(False, False)
        self.title(self.film_title)

        self.container = Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frm_data = Frame(self.container)
        self.frm_data.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # POSTER
        self.cnv_poster = Canvas(self.frm_data, width=400, height=570, bg="black")
        self.cnv_poster.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.cnv_poster.bind(
            "<Button-1>",
            lambda event: open_browser(
                "https://www.imdb.com/title/%s/reference" % (self.film_id)
            ),
        )

        # CAST & CREW
        self.frm_cast_and_crew = LabelFrame(self.frm_data, text="Cast & Crew")
        self.frm_cast_and_crew.grid(
            row=0, column=1, padx=10, pady=10, ipadx=5, ipady=5, sticky="nsew"
        )

        Label(self.frm_cast_and_crew, text="Director:", font="Default 10 bold").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.lbl_director = Label(self.frm_cast_and_crew, width=80, anchor="w")
        self.lbl_director.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        Label(self.frm_cast_and_crew, text="Writers:", font="Default 10 bold").grid(
            row=1, column=0, padx=5, pady=5, sticky="ne"
        )
        self.tree_writers = Treeview(self.frm_cast_and_crew, show="tree", height=4)
        self.tree_writers.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.tree_writers["columns"] = ["writer"]
        self.tree_writers.column("#0", width=0, stretch="no")
        self.tree_writers.column("writer", anchor="nw", width=750, stretch="no")
        self.tree_writers.bindtags((self.tree_writers, self.frm_cast_and_crew, "all"))
        self.tree_writers.bind(
            "<Enter>", lambda event: self._bound_to_mousewheel(event, self.tree_writers)
        )
        self.tree_writers.bind(
            "<Leave>",
            lambda event: self._unbound_to_mousewheel(event, self.tree_writers),
        )

        self.writers_scroll = Scrollbar(
            self.frm_cast_and_crew, orient="vertical", command=self.tree_writers.yview
        )
        self.writers_scroll.grid(row=1, column=1, pady=5, sticky="nse")

        self.tree_writers.configure(yscrollcommand=self.writers_scroll.set)

        Label(self.frm_cast_and_crew, text="Cast:", font="Default 10 bold").grid(
            row=2, column=0, padx=5, pady=5, sticky="ne"
        )
        self.tree_cast = Treeview(self.frm_cast_and_crew, height=20)
        self.tree_cast.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        self.tree_cast["columns"] = ["actor", "character"]
        self.tree_cast.column("#0", width=0, stretch="no")
        self.tree_cast.column("actor", anchor="nw", width=250, stretch="no")
        self.tree_cast.column("character", anchor="nw", width=500, stretch="no")
        self.tree_cast.heading("#0", text="", anchor="center")
        self.tree_cast.heading("actor", text="Actor", anchor="center")
        self.tree_cast.heading("character", text="Character", anchor="center")
        self.tree_cast.bindtags((self.tree_cast, self.frm_cast_and_crew, "all"))
        self.tree_cast.bind(
            "<Enter>", lambda event: self._bound_to_mousewheel(event, self.tree_cast)
        )
        self.tree_cast.bind(
            "<Leave>", lambda event: self._unbound_to_mousewheel(event, self.tree_cast)
        )

        self.cast_scroll = Scrollbar(
            self.frm_cast_and_crew, orient="vertical", command=self.tree_cast.yview
        )
        self.cast_scroll.grid(row=2, column=1, pady=5, sticky="nse")

        self.tree_cast.configure(yscrollcommand=self.cast_scroll.set)

        # TECHNICAL DETAILS
        self.frm_technical_details = LabelFrame(self.frm_data, text="Technical Details")
        self.frm_technical_details.grid(
            row=1, column=1, padx=10, pady=10, ipadx=5, ipady=5, sticky="nsew"
        )

        Label(self.frm_technical_details, text="Country:", font="Default 10 bold").grid(
            row=3, column=0, padx=5, pady=5, sticky="ne"
        )

        self.frm_country = Frame(self.frm_technical_details)
        self.frm_country.grid(row=3, column=1, sticky="w")

        Label(
            self.frm_technical_details, text="Language:", font="Default 10 bold"
        ).grid(row=4, column=0, padx=5, pady=5, sticky="ne")
        self.lbl_language = Label(self.frm_technical_details, width=80, anchor="w")
        self.lbl_language.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")

        Label(self.frm_technical_details, text="Color:", font="Default 10 bold").grid(
            row=5, column=0, padx=5, pady=5, sticky="ne"
        )
        self.lbl_color = Label(self.frm_technical_details, anchor="w")
        self.lbl_color.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        Label(self.frm_technical_details, text="Runtime:", font="Default 10 bold").grid(
            row=6, column=0, padx=5, pady=5, sticky="ne"
        )
        self.lbl_runtime = Label(self.frm_technical_details, width=80, anchor="w")
        self.lbl_runtime.grid(row=6, column=1, padx=5, pady=5, sticky="nsew")

        self.show_poster()
        self.show_rating()
        self.show_full_data()

    def open_map(self, country):
        """Show the selected country in Google Maps (if the country exists)."""

        open_browser("https://www.google.com/maps/place/%s" % (country))

    def open_wikipedia(self, country):
        """
        Show the selected country in Wikipedia (when the country does not
        exist).
        """

        open_browser("https://en.wikipedia.org/wiki/%s" % (country))

    def poster_available(self):
        """Create the film poster."""

        self.cnv_poster.create_image(200, 265, anchor="center", image=self.poster)

    def poster_unavailable(self):
        """Create a message for unavailable posters."""

        unavailable = "Oh, no! The poster is not available! :("

        self.cnv_poster.create_text(
            340,
            265,
            text=unavailable,
            anchor="ne",
            font="Default 10 bold",
            fill="red",
        )

    def show_actors(self, cast):
        """Show the full cast in a treeview."""

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

        # Bold the names of the stars
        self.tree_cast.tag_configure("star", font="Default 10 bold")

    def show_flags(self, countries):
        """Show a flag next to each country name."""

        eval_map = lambda x: (lambda p: self.open_map(x))
        eval_wiki = lambda x: (lambda p: self.open_wikipedia(x))
        for i, country in enumerate(countries):
            path = "%sflags/%s" % (
                STATIC_ROOT,
                get_country_image_name(country),
            )

            if os.path.isfile(path):
                img = Image.open(path).resize((16, 16))
                self.flag = ImageTk.PhotoImage(img)
            else:
                self.flag = None

            lbl_country = Label(
                self.frm_country,
                text=(" " if self.flag else "") + country,
                compound="left",
                image=self.flag,
                anchor="w",
            )
            lbl_country.grid(row=3, column=i + 1, padx=5, pady=5, sticky="nsew")
            lbl_country.image = self.flag
            lbl_country.bind(
                "<Button-1>",
                eval_map(country) if self.flag else eval_wiki(country),
            )

    def show_full_data(self):
        """Show the scraped data of the selected film."""

        data = self.film.get_crew()

        # Directors
        directors = data["directors"]
        self.lbl_director["text"] = ", ".join(sorted(directors))

        # Writers
        writers = data["writers"]
        self.show_writers(writers, directors)

        # Full cast
        cast = data["cast"]
        self.show_actors(cast)

        (
            runtime,
            countries,
            languages,
            color,
            social,
        ) = self.film.get_technical_details()

        # Social media
        self.show_social_media(social)

        # Countries
        countries = sorted(countries.split(", "))
        self.show_flags(countries)

        # Languages
        self.lbl_language["text"] = ", ".join(sorted(languages.split(", ")))

        # Color
        self.lbl_color["text"] = color
        if "Black" in color.capitalize():
            self.lbl_color.config(bg="black", fg="white")
        elif "Color" in color.capitalize():
            self.lbl_color["fg"] = "red"

        # Runtime
        self.lbl_runtime["text"] = runtime

    def show_poster(self):
        """Show the poster in the canvas."""

        text = "Click on the poster to access the film's IMDb page."
        self.cnv_poster.create_text(
            333, 10, text=text, anchor="ne", font="Default 8", fill="white"
        )

        # Show the film poster if available; if not, show a message
        try:
            self.poster = WebImage(self.url).get()
            if self.poster.width() > 100 and self.poster.height() > 100:

                # If the poster is too little, show a message instead of the poster
                self.poster_available()
            else:
                raise ImageSizeError

            if not self.poster:
                raise urllib.error.HTTPError
        except ImageSizeError as err1:
            self.poster_unavailable()

            print("ImageSizeError %s: %s" % (err1.errno, str(err1)))
        except urllib.error.HTTPError as err2:
            self.url = re.sub("@.*", "@@._V1_FMjpg_UY473_.jpg", self.url)
            self.poster = WebImage(self.url).get()

            self.poster_available()

            print(
                "%s - The URL does not exist. A new URL has been created." % (str(err2))
            )

    def show_rating(self):
        """Show the rating in the canvas."""

        im = Image.open("%sicons/imdb.png" % (STATIC_ROOT)).resize((64, 64))
        self.img = ImageTk.PhotoImage(im)
        self.cnv_poster.create_image(135, 541, anchor="center", image=self.img)

        self.cnv_poster.create_text(
            290,
            530,
            text="Rating: %s" % (self.rating),
            anchor="ne",
            font="Default 14 bold",
            fill="white",
        )

    def show_social_media(self, social):
        """
        If the selected film has social media, insert a frame, and within it
        some labels depending on the number of sites.

        For every multiple of 4, the new labels are placed in a new column. Bind
        each label with a link to its corresponding URL.
        """

        if social:
            self.frm_social = LabelFrame(self.frm_data, text="Social Media")
            self.frm_social.grid(
                row=1, column=0, padx=10, pady=10, ipadx=10, ipady=5, sticky="nsew"
            )

            eval_link = lambda x: (lambda p: open_browser(x))
            i = 0
            j = 0
            for key, value in social.items():
                lbl_social = Label(
                    self.frm_social, fg="blue", anchor="w", cursor="hand2"
                )
                lbl_social.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                lbl_social.bind("<Button-1>", eval_link(value))

                self.social_icon = None

                file_name = self.film.get_social_media_file_name(key)
                text = self.film.get_social_media_text(key)

                if file_name:
                    img = Image.open(
                        "%sicons/%s.png" % (STATIC_ROOT, file_name)
                    ).resize((16, 16))
                    self.social_icon = ImageTk.PhotoImage(img)

                    lbl_social["text"] = " " + text
                    lbl_social["compound"] = "left"
                    lbl_social["image"] = self.social_icon
                    lbl_social.image = self.social_icon

                else:
                    lbl_social["text"] = text

                i += 1

                if i % 4 == 0:
                    i = 0
                    j += 1

    def show_writers(self, writers, directors):
        """Show the writers in a treeview."""

        for i, writer in enumerate(writers):
            self.tree_writers.insert(
                parent="",
                index=i,
                iid=i,
                values=(writer,),
                tags=("writer",) if writer in directors else "",
            )
        self.tree_writers.tag_configure("writer", font="Default 10 bold")

    def _bound_to_mousewheel(self, event, listbox):
        """Bind widgets to the mousewheel."""

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

    def _on_mousewheel_down(self, event, listbox):
        """Mousewheel scrolling down."""

        listbox.yview_scroll(-1, "units")

    def _on_mousewheel_up(self, event, listbox):
        """Mousewheel scrolling up."""

        listbox.yview_scroll(1, "units")

    def _unbound_to_mousewheel(self, event, listbox):
        """Unbind widgets from the mousewheel."""

        # On Linux
        listbox.unbind_all("<Button-4>")
        listbox.unbind_all("<Button-5>")

        # On Windows
        listbox.unbind_all("<MouseWheel>")


class ImageSizeError(Exception):
    """Custom exception for when a poster image's width is below 100 pixels."""

    errno = 123456789

    def __str__(self):
        return "The image is too little."


def open_browser(url):
    """Open the default web browser."""

    webbrowser.open(url)
