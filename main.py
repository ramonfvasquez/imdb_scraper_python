import tkinter as tk
from tkinter import ttk

import db
import scraper


class IMDbScraper:
    def __init__(self):
        self.image = None

        self.root = tk.Tk()
        self.root.title("IMDb Scraper - Top 250")

        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH)

        self.frm_films = tk.LabelFrame(container, text="Films")
        self.frm_films.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)

        self.lbx_results = tk.Listbox(self.frm_films, width=60)
        self.lbx_results.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.lbx_results.bind(
            "<<ListboxSelect>>",
            lambda _: [self.show_film_data(self.lbx_results.curselection()[0] + 1)],
        )
        self.listbox_scroll = ttk.Scrollbar(
            self.frm_films, orient="vertical", command=self.lbx_results.yview
        )
        self.listbox_scroll.grid(row=0, column=0, pady=5, sticky="nse")
        self.lbx_results.configure(yscrollcommand=self.listbox_scroll.set)

        self.frm_data = tk.LabelFrame(container)
        self.frm_data.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)

        tk.Label(self.frm_data, text="Title:", font="Default 10 bold").grid(
            row=0, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_title = tk.Label(self.frm_data, width=50, anchor=tk.W)
        self.lbl_title.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.frm_data, text="Year:", font="Default 10 bold").grid(
            row=1, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_year = tk.Label(self.frm_data, width=50, anchor=tk.W)
        self.lbl_year.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.frm_data, text="Director:", font="Default 10 bold").grid(
            row=2, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_director = tk.Label(self.frm_data, width=50, anchor=tk.W)
        self.lbl_director.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.frm_data, text="Cast:", font="Default 10 bold").grid(
            row=3, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_cast = tk.Label(self.frm_data, width=50, anchor=tk.W)
        self.lbl_cast.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        tk.Label(self.frm_data, text="Rating:", font="Default 10 bold").grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.E
        )
        self.lbl_rating = tk.Label(self.frm_data, width=50, anchor=tk.W)
        self.lbl_rating.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)

        scraper.get_film_data()
        self.show_films()

        self.root.mainloop()

    def show_films(self):
        self.lbx_results.delete(0, tk.END)
        films = db.read_table()

        i = 0
        for film in films:
            self.lbx_results.insert(i, f"{i+1:03}. {film[0]}")
            i += 1

    def show_film_data(self, id):
        index, title, year, director, cast, rating = db.search(id)[0]

        self.lbl_title["text"] = title
        self.lbl_year["text"] = year
        self.lbl_director["text"] = director
        self.lbl_cast["text"] = cast
        self.lbl_rating["text"] = rating


def main():
    db.create_db()
    db.create_table()
    app = IMDbScraper()


if __name__ == "__main__":
    main()
