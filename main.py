from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import requests
from secret import key, token
from forms import LoginForm, RegisterForm, RatingForm, AddForm

# --------------TMDB-------------------
TMDB_API_KEY = key
TMDB_BEARER_TOKEN = token

header = {
    'Authorization': f'Bearer {TMDB_BEARER_TOKEN}',
    'Content-Type': 'application/json;charset=utf-8',
}
# ---------------------------------------


app = Flask(__name__)
app.config['SECRET_KEY'] = 'VdecUOFg9_zn9h4rtVCnGg'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=True)
    year = db.Column(db.Integer, unique=False, nullable=True)
    description = db.Column(db.String(120), unique=False, nullable=True)
    rating = db.Column(db.Float, unique=False, nullable=True)
    ranking = db.Column(db.Integer, unique=False, nullable=True)
    review = db.Column(db.String(120), unique=False, nullable=True)
    img_url = db.Column(db.String(120), unique=False, nullable=True)


# db.create_all()


@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("login.html", form=form)


@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    return render_template("register.html", form=form)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    return render_template("contact.html")

@app.route("/logout")
def logout():
    pass
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        new_title = form.title.data
        query = {
            'api_key': TMDB_API_KEY,
            'query': new_title,  # URI encoded
        }
        response = requests.get('https://api.themoviedb.org/3/search/movie', params=query, headers=header)
        t = response.json()['results']
        return render_template('select.html', titles=t, lenght=len(t))
    return render_template("add.html", form=form)


@app.route("/edit/<id>", methods=['GET', 'POST'])
def edit(id):
    form = RatingForm()
    movie_id = id
    movie_to_update = Movie.query.get(movie_id)
    if form.validate_on_submit():
        new_rating = form.rating.data
        new_review = form.review.data
        movie_to_update.rating = new_rating
        movie_to_update.review = new_review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie_to_update, form=form)


@app.route("/delete")
def delete():
    movie_id = request.args.get("dele")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/select")
def select():
    try:
        year = int(request.args.get("year")[0:4])
        title = request.args.get("title")
        description = request.args.get("description")
        rating = float(request.args.get("rating"))
        img_url = f"https://image.tmdb.org/t/p/w500{request.args.get('img_url')}"
    except (ValueError, TypeError):
        print('error')
        return redirect(url_for('home'))
    else:
        title_exist = Movie.query.filter(Movie.title == title).first()
        if title_exist:
            print(title_exist)
            return redirect(url_for('home'))
        elif year and title and description and rating and img_url:
            new_movie2 = Movie(
                title=title,
                year=year,
                description=description,
                rating=rating,
                ranking=7,
                review="None",
                img_url=img_url
            )
            db.session.add(new_movie2)
            db.session.commit()
        else:
            new_movie2 = Movie(
                title=title,
                year=year,
                description=description,
                rating=rating,
                ranking=7,
                review="Picture not found",
                img_url='/static/img/404.jpg'
            )
            db.session.add(new_movie2)
            db.session.commit()
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port='5000', debug=True)
