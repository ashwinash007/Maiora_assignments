from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import requests

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Joke model with only required fields
class Joke(db.Model):
    __tablename__ = 'jokes'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    type = db.Column(db.String(50))
    joke = db.Column(db.Text, nullable=True)
    setup = db.Column(db.Text, nullable=True)
    delivery = db.Column(db.Text, nullable=True)
    nsfw = db.Column(db.Boolean)
    political = db.Column(db.Boolean)
    sexist = db.Column(db.Boolean)
    safe = db.Column(db.Boolean)
    lang = db.Column(db.String(10))

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/fetch_jokes', methods=['GET'])
def fetch_and_show_jokes():
    stored_jokes = []
    jokes_needed = 100
    batch_size = 10  # API max limit per request

    while len(stored_jokes) < jokes_needed:
        url = f"https://v2.jokeapi.dev/joke/Any?amount={batch_size}&format=json"
        response = requests.get(url)

        if response.status_code != 200:
            return "Failed to fetch jokes", 500

        jokes = response.json().get('jokes', [])

        for joke in jokes:
            new_joke = Joke(
                category=joke.get('category', ''),
                type=joke.get('type', ''),
                joke=joke.get('joke', '') if joke.get('type', '') == 'single' else None,
                setup=joke.get('setup', '') if joke.get('type', '') == 'twopart' else None,
                delivery=joke.get('delivery', '') if joke.get('type', '') == 'twopart' else None,
                nsfw=joke['flags'].get('nsfw', False),
                political=joke['flags'].get('political', False),
                sexist=joke['flags'].get('sexist', False),
                safe=joke.get('safe', False),
                lang=joke.get('lang', '')
            )
            db.session.add(new_joke)

            # Store only the joke text
            joke_text = new_joke.joke if new_joke.type == "single" else f"{new_joke.setup} {new_joke.delivery}"
            stored_jokes.append(joke_text)

            if len(stored_jokes) >= jokes_needed:
                break  # Stop when we reach 100 jokes

    db.session.commit()

    return render_template('jokes.html', jokes=stored_jokes)

if __name__ == '__main__':
    app.run(debug=True)
