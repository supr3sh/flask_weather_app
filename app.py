from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import pyrebase

app = Flask(__name__)

API_key = "api key from openweathermap"
url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid='+ API_key

#FireBase
firebaseConfig = {
    #Config from firebase realtime database
}
fire = pyrebase.initialize_app(firebaseConfig)
fireDB = fire.database()

def get_weather_data(city):
    r = requests.get(url.format(city)).json()
    return r

@app.route('/')
def index_get():
    weather_data = []

    cityDict = fireDB.get()
    cityVal = cityDict.val()

    if cityVal == None:
        return render_template('index.html')

    for city in cityVal.values():
        r = get_weather_data(city)
        weather = {
            "city": city, 
            "temperature": r['main']['temp'],
            "description": r['weather'][0]['description'],
            "icon": r['weather'][0]['icon']
        }

        weather_data.append(weather)

    
    return render_template('index.html', weather_data = weather_data)


@app.route('/', methods=['POST'])
def index_post():
    error_msg = ''
    new_city = request.form.get('city')
    if new_city.strip() == "":
        error_msg = 'Add a city name.'
    elif new_city:
        cityDict = fireDB.get()
        cityVal = cityDict.val()
        found = False
        if cityVal == None:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                fireDB.child(new_city).set(new_city)
            else:
                error_msg = 'City does not exist!'

        elif new_city in cityVal.values():
            found = True
        if not found:
            new_city_data = get_weather_data(new_city)

            if new_city_data['cod'] == 200:
                fireDB.child(new_city).set(new_city)
            else:
                error_msg = 'City does not exist!'
        else:
            error_msg = 'City already added!'
    
    if error_msg:
        flash(error_msg, 'error')
    else:
        flash('City added successfully.')
        
    return redirect(url_for('index_get'))

@app.route('/delete/<name>')
def delete_city(name):
    cityDict = fireDB.get()
    cityVal = cityDict.val()

    for  cityName in cityVal.values():
        if cityName == name:
            fireDB.child(cityName).remove()
            flash(f'Successfully deleted { cityName }', 'success')
            break
    return redirect(url_for('index_get'))

if __name__ == "__main__":
        app.secret_key = 'super secret key'
        app.config['SESSION_TYPE'] = 'filesystem'
        app.run(debug=True)
