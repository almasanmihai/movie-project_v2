from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import requests
from secret import key, token
from forms import LoginForm, RegisterForm, RatingForm, AddForm
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

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

# --------------Connect to db-------------------
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ---------------------------------------

# --------------Login manager-------------------
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------


# --------------Tables config-------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    movie = relationship("Movie", back_populates="owner")


class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=True)
    year = db.Column(db.Integer, unique=False, nullable=True)
    description = db.Column(db.String(120), unique=False, nullable=True)
    rating = db.Column(db.Float, unique=False, nullable=True)
    ranking = db.Column(db.Integer, unique=False, nullable=True)
    review = db.Column(db.String(120), unique=False, nullable=True)
    img_url = db.Column(db.String(120), unique=False, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    owner = relationship("User", back_populates='movie')


# db.create_all()


# ---------------------------------------

@app.route("/")
def home():
    if current_user.is_authenticated:
        all_movies = Movie.query.filter_by(owner_id=current_user.id).order_by(Movie.rating).all()
        for i in range(len(all_movies)):
            all_movies[i].ranking = len(all_movies) - i
        db.session.commit()
        return render_template("index.html", movies=all_movies)
    else:
        return render_template("index.html", movies=[])


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash(f'User {form.email.data} does not exist. Please register instead.')
            return redirect(url_for('register'))
        elif not check_password_hash(user.password, form.password.data):
            flash('Wrong password. Please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            flash(f'Welcome back {user.name} ')
            return redirect(url_for('home'))
    return render_template("login.html", form=form)


@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_email = form.email.data
        new_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=12)
        new_name = form.name.data
        user_exists = User.query.filter_by(email=new_email).first()
        if user_exists:
            flash(f'User {new_email} exists. Login instead.')
            return redirect(url_for('login'))
        else:
            new_user = User(email=new_email, password=new_password, name=new_name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash(f'Hi {new_user.name}! Start by pressing Add Movie.')
            return redirect(url_for('home'))
    return render_template("register.html", form=form)


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
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
    movie_id = request.args.get("item_to_delete")
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
        flash(f'Something went wrong. The title you searched was not added to your top.')
        return redirect(url_for('home'))
    else:
        all_movies = Movie.query.filter_by(owner_id=current_user.id).all()
        title_exist = False
        for movie in all_movies:
            if movie.title == title:
                title_exist = True
        if title_exist:
            flash(f'{title} is already in your top.')
            return redirect(url_for('home'))
        elif year and title and description and rating and img_url:
            new_movie2 = Movie(
                title=title,
                year=year,
                description=description,
                rating=rating,
                ranking=7,
                review="Your rating.",
                img_url=img_url,
                owner=current_user
            )
            db.session.add(new_movie2)
            db.session.commit()
            flash(f'Succes. {title} was added to your top.')
        else:
            new_movie2 = Movie(
                title=title,
                year=year,
                description=description,
                rating=rating,
                ranking=7,
                review="Picture not found",
                img_url='https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1074&q=80',
                owner=current_user
            )
            db.session.add(new_movie2)
            db.session.commit()
            flash(f'Picture for {title} is not available.')
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port='5000')
