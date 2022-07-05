import os
import sqlite3
import config
import folium
from flask import Flask, render_template, g, url_for, request, redirect


app = Flask(__name__)
app.config.from_object(config)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'database.db')))


# Database
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    return conn


def create_db():
    db = connect_db()
    with app.open_resource('sql_request.sql', mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


# Render map
def render_map():
    map = folium.Map(location=[51.1605227, 71.4703558], default_zoom_start=35)
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM subjects")
    for subject in cursor.fetchall():
        folium.Marker(
            location=[subject[-3], subject[-2]],
            popup=f'''<b>ИИН:</b> {subject[4]}<br>
                      <b>Фамилия:</b> {subject[2]}<br>
                      <b>Имя:</b> {subject[1]}<br>
                      <b>Адрес:</b>{subject[6]} {subject[7]}<br>
                      <b>Площадь(кв.м.):</b>{subject[-5]}<br>
                      <b>Кадастровый номер:</b>{subject[9]}<br>
                      <a href="/table/update/{subject[0]}"
                      target="_blank">Изменить<a>''',
            tooltip=subject[1] + " " + subject[2],
            icon=folium.Icon(color=subject[-1])
        ).add_to(map)
    db.close()
    map.save(os.path.join(app.root_path, 'templates/map.html'))


# Routes
@app.route("/")
@app.route("/map/")
def index():
    return render_template("index.html", title="Карта")


@app.route("/onlymap/")
def map():
    render_map()
    return render_template("map.html")


@app.route("/table/")
def table():
    subjects = []
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT last_name, first_name, patronymic,\
                    cadastral_number, area_size, city, street, home_number,\
                    apartment_number, id FROM subjects ORDER BY last_name")
    for subject in cursor.fetchall():
        subjects.append([subject[0] + " " + subject[1] + " " + subject[2],
                        subject[3], subject[4],
                        subject[5] + ", " + subject[6] +
                        " " + subject[7] + subject[8], subject[9]])
    return render_template(
                           "table.html",
                           title="Анкеты",
                           subjects=enumerate(subjects, 1),
                           count=len(subjects))


@app.route("/add_subject/", methods=["GET", "POST"])
def add_subject():
    if request.method == "POST":
        data = request.form
        first_name = data["first_name"]
        last_name = data["last_name"]
        patronymic = "" if "patronymic" not in data else data["patronymic"]
        iin = data["iin"]
        city = data["city"]
        street = data["street"]
        home_number = data["home_number"]
        apartment_number = data["apartment_number"]
        cadastral_number = "" if "cadastral_number" not in data else data["cadastral_number"]
        area_size = "" if "area_size" not in data else data["area_size"]
        notes = "" if "notes" not in data else data["notes"]
        print(type(data["longitude"]))
        longitude = float(data["longitude"])
        latitude = float(data["latitude"])
        mark_color = data["mark_color"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO subjects\
                        (first_name, last_name, patronymic,\
                        iin, city, street, home_number, \
                        apartment_number, cadastral_number, area_size,\
                        notes, longitude, latitude, mark_color) \
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (first_name, last_name, patronymic,
                        iin, city, street, home_number,
                        apartment_number, cadastral_number,
                        area_size, notes, longitude, latitude, mark_color))
        db.commit()

        return redirect(url_for("table"))

    return render_template("add_subject.html", title="Создать анкету")


@app.route("/table/update/<id>", methods=["GET", "POST"])
def update_subject(id):
    db = get_db()
    cursor = db.cursor()
    if request.method == "POST":
        data = request.form
        first_name = data["first_name"]
        last_name = data["last_name"]
        patronymic = "" if "patronymic" not in data else data["patronymic"]
        iin = data["iin"]
        cadastral_number = "" if "cadastral_number" not in data else data["cadastral_number"]
        area_size = "" if "area_size" not in data else data["area_size"]
        notes = "" if "notes" not in data else data["notes"]
        mark_color = data["mark_color"]
        cursor.execute(f"UPDATE subjects SET\
                        first_name = '{first_name}',\
                        last_name = '{last_name}',\
                        patronymic = '{patronymic}',\
                        iin = '{iin}',\
                        cadastral_number = '{cadastral_number}',\
                        notes = '{notes}',\
                        area_size = '{area_size}',\
                        mark_color = '{mark_color}'\
                        WHERE id = {id}")
        db.commit()
        return redirect(url_for("index"))

    cursor.execute(f"SELECT * FROM subjects WHERE id = {id}")
    subject = cursor.fetchone()
    return render_template("update_subject.html", title="Изменить анкету", subject=subject)


@app.route("/table/delete/<id>")
def delete_subject(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM subjects WHERE ID = {id}")
    db.commit()
    return redirect(url_for("table"))


@app.errorhandler(404)
def pageNotFound(error):
    return render_template('page404.html', title="Страница не найдена"), 404


if __name__ == "__main__":
    app.run()
