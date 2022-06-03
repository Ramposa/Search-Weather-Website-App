from urllib import response
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db' # Establishing connnection to the DB.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # If True the Flask-SQLAlchemy will track modifications of objects and emit signals. 
app.config['SECRET_KEY'] = "b'\xf9_gVA\xcf\x02\rI]\x93\xb0\x83\xc1\xfc\xd9r\xf8\xbb\x08m\xfe\xfa5'" # Encrypt cookies, saved them to browser.

db = SQLAlchemy(app)

#@app.route('/')
#def homepage():
#    return render_template("index.html")

# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#simple-relationships - Database work
# https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application - Database work part 2

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid=83dd4856285e37cbd9f0c43d5236c40c' # API || { city } is where we get information from
    # the user search.
    returnAPI = requests.get(url).json() # . The request object holds all incoming data from the request, which includes the mimetype, referrer, IP address, raw data, HTTP method, and headers, among other things.
    return returnAPI

@app.route('/')
def index_get():

    cities = City.query.all()
    
    weather_data = []

    for city in cities:

        returnAPI = get_weather_data(city.name)
        print(returnAPI)

        #print(returnAPI) # BUG CHECKING

        weather = { # This pulls data from the API that it was called def get_weather_data(city) and return them into a variable which can be used later.
            'city' : city.name,
            'country' : returnAPI['sys']['country'],
            'temperature' : returnAPI['main']['temp'],
            'description' : returnAPI['weather'][0]['description'],
            'speed' : returnAPI['wind']['speed'],
            'icon' : returnAPI['weather'][0]['icon'],
        }

        weather_data.append(weather)

    #return render_template('weather.html', weather_data=weather_data)
    return render_template('weatherStorage.html', weather_data=weather_data)

#----------------------------------------------
@app.route('/', methods=['POST']) # Post method
def index_post():
    err_msg = ''

    new_city = request.form.get('city')
        
    if new_city:    # If statement
        existing_city = City.query.filter_by(name=new_city).first() # If existing_city exist then create error message

    if not existing_city:   # If not then add to the database
            new_city_data = get_weather_data(new_city) # Check if city exist in real life
            
            if new_city_data['cod'] == 200: # Comes from object JSON
                new_city_obj = City(name=new_city) # if new city is added then it will add dit to the database then commit.

                db.session.add(new_city_obj)
                db.session.commit()

            else: # if not 200
                err_msg = 'City does not exist in the world.'
    else: 
        err_msg = 'City already exist in the database.'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added successfully')

    return redirect(url_for('index_get'))

@app.route('/delete/<name>') # Basically deletes a row from the DB
def delete_city(name):
        city = City.query.filter_by(name=name).first()
        db.session.delete(city)
        db.session.commit()

        flash(f'Successfully deleted { city.name }', 'success')
        return redirect(url_for('index_get'))



if __name__ == '__main__': # Running the server
        print("== Running in debug mode ==")
        app.run(host='0.0.0.0', port=5014, debug=True) # Assigned Port Number