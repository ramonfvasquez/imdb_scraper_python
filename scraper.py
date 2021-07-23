import re
import requests
from bs4 import BeautifulSoup

import db


def scrape_data():
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


def get_film_data():
    db.clear_table()

    data = scrape_data()
    for d in data:
        title = d.find("td", class_="titleColumn")
        title = title.find("a")
        title = re.sub("<.*?>", "", str(title))

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

        db.populate_table((title, year, director, ", ".join(cast), rating))
