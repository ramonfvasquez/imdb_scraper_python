import io
import mysql.connector
import re
import requests
import urllib.request
from bs4 import BeautifulSoup
from PIL import Image, ImageTk


class DataBase:
    def connection(self, database=None):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database=database,
            auth_plugin="mysql_native_password",
        )

    def create_db(self):
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
            print("An error occured while saving the data!")

        db.close()

    def read_table(self):
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
        db = self.connection(database="imdb")

        try:
            cur = db.cursor()
            sql = "TRUNCATE TABLE film;"
            cur.execute(sql)
            db.commit()
        except:
            return

        db.close()


class Scraper:
    def __init__(self, url):
        self.url = url

    def scrape_crew(self):
        # Scrapes the directors, and the writers of the selected film
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
        # Scrapes the runtime, and the countries of the selected film
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

    def scrape_top_250(self):  # Scrapes the Top 250 film list
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(class_="lister-list")
        films = results.find_all("tr")
        page.close()

        film_list = []
        for film in films:
            film_list.append(film)

        return film_list


class FilmList:
    def __init__(self):
        self.scraper = Scraper("http://www.imdb.com/chart/top")

    def get_basic_data(self):  # Saves the basic film data into a DB
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


class Film:
    def __init__(self, film_id):
        self.film_id = film_id

    def get_crew(self):
        # Gets the directors, writers, and full cast. Saves them into a dictionary.
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
        url = "https://www.imdb.com/title/%s/reference" % (self.film_id)
        return Scraper(url).scrape_technical_data()

    def get_social_media_file_name(self, site):
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


class WebImage:  # Opens an image based on its URL
    def __init__(self, url):
        self.connection = urllib.request.urlopen(url)
        self.raw_data = self.connection.read()
        self.im = Image.open(io.BytesIO(self.raw_data))
        self.image = ImageTk.PhotoImage(self.im)

    def get(self):
        return self.image


def get_country_image_name(country):  # Returns the country flag image name
    country = country.replace(" ", "-").replace(".", "").lower()
    return "%s.png" % (country)
