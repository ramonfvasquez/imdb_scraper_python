import mysql.connector


class DBConnector:
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
