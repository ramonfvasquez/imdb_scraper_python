import io
import re
import requests
import urllib.request
from bs4 import BeautifulSoup
from PIL import Image, ImageTk

from db import DBConnector


class FilmScraper:
    def scrape_film(self, film_id):
        # Scrapes the directors, and the writers of the selected film
        url = "https://www.imdb.com/title/%s/fullcredits" % (film_id)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find("div", id="fullcredits_content")
        directors_writers = results.find_all(
            "table", class_="simpleTable simpleCreditsTable"
        )
        cast = results.find("table", class_="cast_list")

        data = []
        data.append(directors_writers[0])
        data.append(directors_writers[1])
        data.append(cast)

        return data

    def get_additional_data(self, film_id):
        # Scrapes the runtime, and the countries of the selected film
        url = "https://www.imdb.com/title/%s/reference" % (film_id)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(
            "section", class_="titlereference-section-additional-details"
        )
        results = results.find_all("tr")

        data = []
        for res in results:
            data.append(res)

        runtime = data[1]
        runtime = re.sub("<.*?>", "", str(runtime))
        runtime = (
            runtime.replace(" ", "")
            .replace("Runtime", "")
            .replace("\n", "")
            .replace("min", " min")
        )

        country = ""
        if "Country" in str(data[2]):
            country = data[2].find_all("a")
            country = re.sub("<.*?>", "", str(country))
        elif "Country" in str(data[3]):
            country = data[3].find_all("a")
            country = re.sub("<.*?>", "", str(country))

        country = country.replace("[", "").replace("]", "")

        return (runtime, country)

    def get_full_film_data(self, film_id):
        # Gets the directors, writers, and full cast. Saves them into a dictionary.
        data = self.scrape_film(film_id)

        film = {}

        director_res = data[0].find_all("a")
        director = re.sub("<.*?>", "", str(director_res))
        director = director.replace("[", "").replace("]", "").replace("\n", "")
        director = director.split(",  ")
        director[0] = re.sub("^[ ]", "", director[0])
        film["director"] = sorted(set(director))

        writers_res = data[1].find_all("a")
        writers = re.sub("<.*?>", "", str(writers_res))
        writers = writers.replace("[", "").replace("]", "").replace("\n", "")
        writers = writers.split(",  ")
        writers[0] = re.sub("^[ ]", "", writers[0])
        film["writers"] = sorted(set(writers))

        actors_res = data[2].find_all("tr")
        actors = (
            re.sub("<.*?>", "", str(actors_res)).replace("  ", "").replace("\n", "")
        )
        actors = actors.replace("\n", "").replace("[", "").replace("]", "")
        actors = actors.split(",   ")
        actors.remove(actors[0])

        cast = {}
        for actor in actors:
            actor = actor.split(" ...")
            if len(actor) == 1:
                actor.append("")

            actor[0] = actor[0].replace(", Rest of cast listed alphabetically:", "")
            actor[1] = actor[1].replace(", Rest of cast listed alphabetically:", "")

            cast[actor[0]] = actor[1].replace(" /", " / ")

        film["cast"] = cast

        return film

    def scrape_film_list(self):  # Scrapes the Top 250 film list
        url = "http://www.imdb.com/chart/top"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(class_="lister-list")
        films = results.find_all("tr")
        page.close()

        film_list = []
        for film in films:
            film_list.append(film)

        return film_list

    def get_basic_film_data(self):  # Saves the basic film data into a DB
        DBConnector().clear_table()

        data = self.scrape_film_list()
        for d in data:
            title = d.find("td", class_="titleColumn")
            title = title.find("a")
            title = re.sub("<.*?>", "", str(title))

            film_id = d.find("td", class_="watchlistColumn")
            film_id = film_id.find("div")
            film_id = film_id["data-tconst"]

            year = d.find("span", class_="secondaryInfo")
            year = re.sub("<.*?>", "", str(year)).replace("(", "").replace(")", "")

            director = d.find("td", class_="titleColumn")
            director = director.find("a")
            director = director["title"]
            director, *cast = director.split(", ")
            director = director.replace(" (dir.)", "")

            rating = d.find("td", class_="ratingColumn imdbRating")
            rating = rating.find("strong")
            rating = re.sub("<.*?>", "", str(rating))

            poster = d.find("td", class_="posterColumn")
            poster = poster.find("img")["src"]
            poster = re.sub("@.+", "@._V1_FMjpg_UY474_.jpg", poster)

            DBConnector().populate_table(
                (title, film_id, year, director, ", ".join(cast), rating, poster)
            )


def get_country_image_name(country):  # Returns the country flag image name
    country = country.replace(" ", "-").replace(".", "").lower()
    return "%s.png" % (country)


class WebImage:  # Opens an image based on its URL
    def __init__(self, url):
        self.connection = urllib.request.urlopen(url)
        self.raw_data = self.connection.read()
        self.im = Image.open(io.BytesIO(self.raw_data))
        self.image = ImageTk.PhotoImage(self.im)

    def get(self):
        return self.image
