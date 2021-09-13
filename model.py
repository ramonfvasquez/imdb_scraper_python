"""Model module for the program's MVC pattern.

Classes included: DataBase, Film, FilmList, Scraper, and WebImage.
"""

import io
import mysql.connector
import re
import requests
import urllib.request
from bs4 import BeautifulSoup
from PIL import Image, ImageTk
from tkinter import messagebox


class DataBase:
    """Manages the DB CRUD.

    Each method performs an individual action to interact with the DB. The DB
    is based on MySQL.
    """

    def connection(self, database=None):
        """Connect the program to the DB.

        database is defaulted to None to permit the first connection to MySQL
        so as to create the scheme.
        """

        try:
            return mysql.connector.connect(
                host="localhost",
                user="root",
                password="R+D@11",
                database=database,
                auth_plugin="mysql_native_password",
            )
        except mysql.connector.Error as err:
            messagebox.showerror(
                "MySQL Connection Error",
                "Oops! Something went wrong!\n\n%s" % err,
            )
            exit()

    def create_db(self):
        """Create the DB."""

        db = self.connection()

        try:
            cur = db.cursor()
            sql = "CREATE DATABASE imdb;"
            cur.execute(sql)
            print("Database created!")
        except:
            return

        db.close()

    def create_table(self):
        """Create the table to save the temporary data."""

        db = self.connection(database="imdb")

        try:
            cur = db.cursor()
            sql = """
                CREATE TABLE film (id INT(3) NOT NULL PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(256) NOT NULL COLLATE utf8_spanish2_ci, film_id 
                VARCHAR(20), year INT(4) NOT NULL, director VARCHAR(256) NOT NULL 
                COLLATE utf8_spanish2_ci, cast VARCHAR(1024) NOT NULL COLLATE 
                utf8_spanish2_ci, rating FLOAT(2, 1) NOT NULL, poster_url 
                VARCHAR(1024) NOT NULL);
                """
            cur.execute(sql)
            print("Table created!")
        except:
            return

        db.close()

    def populate_table(self, data):
        """Fill the table with the initial scraping data."""

        db = self.connection(database="imdb")

        try:
            cur = db.cursor()
            sql = """
                INSERT INTO film (title, film_id, year, director, cast, rating, poster_url) 
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
            cur.execute(sql, data)
            db.commit()
        except:
            print("An error occurred when saving the data!")

        db.close()

    def read_table(self):
        """Read the table to get the film's title."""

        db = self.connection(database="imdb")

        try:
            cur = db.cursor()
            sql = "SELECT title FROM film;"
            cur.execute(sql)
            return cur.fetchall()
        except:
            print("Cannot read from table!")

        db.close()

    def search(self, id):
        """Get all the film's basic info when a film is selected."""

        db = self.connection("imdb")

        try:
            cur = db.cursor()
            sql = "SELECT * FROM film WHERE id = %s;"
            cur.execute(sql, (id,))
            return cur.fetchall()
        except:
            print("Cannot find the film!")

        db.close()

    def clear_table(self):
        """Clear the table before saving the updated initial data."""

        db = self.connection(database="imdb")

        try:
            cur = db.cursor()
            sql = "TRUNCATE TABLE film;"
            cur.execute(sql)
            db.commit()
        except:
            return

        db.close()


class Film:
    """Gathers the full data of the selected film."""

    def __init__(self, film_id):
        self.film_id = film_id

    def get_crew(self):
        """Get the directors, writers, and full cast. Save them into a dictionary."""

        url = "https://www.imdb.com/title/%s/fullcredits" % (self.film_id)
        scraper = Scraper(url)

        data = scraper.scrape_crew()

        crew = {}

        directors = data[0].find_all("a")
        directors = re.sub("<.*?>", "", str(directors))
        directors = directors.replace("[", "").replace("]", "").replace("\n", "")
        directors = directors.split(",  ")
        directors[0] = re.sub("^[ ]", "", directors[0])
        crew["directors"] = sorted(set(directors))

        writers = data[1].find_all("a")
        writers = re.sub("<.*?>", "", str(writers))
        writers = writers.replace("[", "").replace("]", "").replace("\n", "")
        writers = writers.split(",  ")
        writers[0] = re.sub("^[ ]", "", writers[0])
        crew["writers"] = sorted(set(writers))

        actors = data[2].find_all("tr")
        actors = re.sub("<.*?>", "", str(actors)).replace("  ", "").replace("\n", "")
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

        crew["cast"] = cast

        return crew

    def get_technical_details(self):
        """Get the countries, runtime, color, and languages of the film."""

        url = "https://www.imdb.com/title/%s/reference" % (self.film_id)
        return Scraper(url).scrape_technical_data()

    def get_social_media_file_name(self, site):
        """Get the social media links of the film."""

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

    def get_social_media_text(self, site):
        """Format the names of the social media links."""

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


class FilmList:
    """IMDB's Top 250 film list."""

    def __init__(self):
        self.scraper = Scraper("http://www.imdb.com/chart/top")

    def get_basic_data(self):
        """Get the basic data of the selected film and save it into the DB."""

        db = DataBase().clear_table()

        data = self.scraper.scrape_top_250()
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

            DataBase().populate_table(
                (title, film_id, year, director, ", ".join(cast), rating, poster)
            )


class Scraper:
    """Scrapes the IMDb's Top 250 film list.

    When the program loads, it gets the full film list and all the basic info
    of each film (title, director, stars, and year), and saves it into the DB.
    """

    def __init__(self, url):
        self.url = url

    def scrape_crew(self):
        """Scrape the directors, and the writers of the selected film."""

        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find("div", id="fullcredits_content")
        directors_and_writers = results.find_all(
            "table", class_="simpleTable simpleCreditsTable"
        )
        cast = results.find("table", class_="cast_list")

        crew = []
        crew.append(directors_and_writers[0])
        crew.append(directors_and_writers[1])
        crew.append(cast)

        return crew

    def scrape_technical_data(self):
        """Scrape the runtime, and the countries of the selected film."""

        page = requests.get(self.url)
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
        languages = []
        color = ""
        social = {}
        if "Country</td>" in str(data[2]):
            country = data[2].find_all("a")
            country = re.sub("<.*?>", "", str(country))

            languages = data[3].find_all("a")
            languages = re.sub("<.*?>", "", str(languages))

            color = data[4].find_all("a")
            color = re.sub("<.*?>", "", str(color))
        elif "Country</td>" in str(data[3]):
            sites = data[2].find_all("a")
            for site in sites:
                key = (
                    re.sub("<.*?>", "", str(site))
                    .replace("\n", "")
                    .replace("    ", "")
                    .replace("                                ", "")
                )
                social[key] = site["href"]

            country = data[3].find_all("a")
            country = re.sub("<.*?>", "", str(country))

            languages = data[4].find_all("a")
            languages = re.sub("<.*?>", "", str(languages))

            color = data[5].find_all("a")
            color = re.sub("<.*?>", "", str(color))

        country = country.replace("[", "").replace("]", "")
        languages = languages.replace("[", "").replace("]", "")
        color = color.replace("[", "").replace("]", "")

        return (runtime, country, languages, color, social)

    def scrape_top_250(self):
        """Scrape the top 250 film list."""

        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(class_="lister-list")
        films = results.find_all("tr")
        page.close()

        film_list = []
        for film in films:
            film_list.append(film)

        return film_list


class WebImage:
    """Opens an image based on its URL."""

    def __init__(self, url):
        self.connection = urllib.request.urlopen(url)
        self.raw_data = self.connection.read()
        self.im = Image.open(io.BytesIO(self.raw_data))
        self.image = ImageTk.PhotoImage(self.im)

    def get(self):
        return self.image


def get_country_image_name(country):
    """Return the country flag image name."""

    country = country.replace(" ", "-").replace(".", "").lower()
    return "%s.png" % (country)
