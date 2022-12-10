import wtforms
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy, Model
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0skojoiKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-10-movie.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)


class Rating(FlaskForm):
    rating = StringField(label='Rating', validators=[DataRequired()])
    review = StringField(label='Review', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


class Add(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    year = db.Column(db.Integer)
    description = db.Column(db.String(250))
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String)


db.create_all()
all_movies = db.session.query(Movie).all()


@app.route("/", methods=['GET', 'POST'])
def home():
    all_movies = db.session.query(Movie).all()
    total_length = len(all_movies)
    for LENGTH in range(total_length):
        all_movies[LENGTH].ranking = total_length - LENGTH
    return render_template("index.html", movies=all_movies)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form_add = Add()
    if request.method == 'POST':
        data = request.form
        name = data['title']
        # print(name)
        movie_api_key = '37e21e37fc426382db6f6c5afe742f0c'

        query = {
            'api_key': movie_api_key,
            'query': name
        }
        movie_api = 'https://api.themoviedb.org/3/search/movie'
        response = requests.get(movie_api, params=query)
        Data = response.json()['results']
        print(Data)
        return render_template('select.html', data=Data)
    return render_template('add.html', form=form_add)


@app.route('/find')
def find():
    movie_id = request.args.get("id")
    print(movie_id)
    if movie_id:
        movie_api_key = '37e21e37fc426382db6f6c5afe742f0c'
        movie_api = 'https://api.themoviedb.org/3/movie'
        movie_api_url = f'{movie_api}/{movie_id}'
        response = requests.get(movie_api_url, params={"api_key": movie_api_key,
                                                       "language": "en-US"})  # , params={"api_key": movie_api_key, "language": "en-US"})
        data = response.json()
        print(data)
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"https://image.tmdb.org/t/p/w500/{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('edit', id=new_movie.id))
    return render_template('index.html')


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    id = request.args.get('id')
    movie = Movie.query.filter_by(id=id).first()
    flask_form = Rating()
    if request.method == 'POST':
        movie = Movie.query.filter_by(id=id).first()
        data = request.form
        rating = data['rating']
        movie.rating = rating
        review = data['review']
        movie.review = review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie, form=flask_form)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    movie_id = request.args.get('id')
    movie_delete = Movie.query.get(movie_id)
    db.session.delete(movie_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
