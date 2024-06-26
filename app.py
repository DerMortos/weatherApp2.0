import os
from functools import wraps
from flask import Flask, render_template, send_file, request, redirect, session, url_for
from user_database import data
from charts import get_main_image, get_city_image

app = Flask(__name__)


def get_headers(response):
    response.headers['Cache-control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'


@app.route('/')
def main():
    """Entry point; the view for the main page """
    cities = [(record.city_id, record.city_name) for record in data]
    return render_template('main.html', cities=cities)


@app.route('/main.png')
def main_plot():
    """The view for rendering the scatter chart"""
    img = get_main_image()
    response = send_file(img, mimetype='image/png')
    get_headers(response)
    return response


@app.route('/city/<int:city_id>')       # will direct you to city in ul
def city(city_id):
    """Views for the city details"""
    city_record = data.get(city_id)
    return render_template('city.html', city_name=city_record.city_name, city_id=city_id,
                           city_climate=city_record.city_climate)


@app.route('/city<int:city_id>.png')
def city_plot(city_id):
    """Views for rendering city specific charts"""
    img = get_city_image(city_id)
    response = send_file(img, mimetype='image/png')
    get_headers(response)
    return response


@app.route('/login/<int:city_id>', methods=["GET", "POST"])
def login(city_id):
    """The view for the login page"""
    city_record = data.get(city_id)
    try:
        error = ''
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']
            if attempted_username == 'admin' and attempted_password == os.environ['USER_PASSWORD']:
                session['logged_in'] = True
                session['username'] = request.form['username']
                return redirect(url_for('edit_database', city_id=city_id))
            else:
                print('invalid credentials')
                error = 'Invalid credentials, Please try again.'
        return render_template('login.html', error=error,city_name=city_record.city_name, city_id=city_id)
    except Exception as e:
        return render_template('login.html', error=str(e), city_name=city_record.city_name, city_id=city_id)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        """login session"""
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            pass
        return redirect(url_for('login'))
        return redirect(url_for('/edit/<int:city_id>'))
    return wrap

# Key added to flask environmental variables under run-> modify run configuration
# key generated with print(os.urandom(24).hex())
app.secret_key = os.environ['FLASK_WEB_APP_KEY']


@app.route('/edit/<int:city_id>', methods=["GET", "POST"])
#@login_required
def edit_database(city_id):
    """Vies for editing city specific data"""
    month_temperature = []
    month_humidity = []
    city_record = data.get(city_id)
    meteo = [get_city_temperature(city_record), get_city_humidity(city_record)]
    try:
        if request.method == 'POST':
            # Get data from form
            for i in range(12):
                # in a production application we should validate the input data
                month_temperature.append(float(request.form[f'temperature{i}']))
                month_humidity.append(int(request.form[f'humidity{i}']))

            # Database update
            for i, month in enumerate(city_record.city_meteo_data):
                month.average_temperature = month_temperature[i]
                month.average_humidity = month_humidity[i]

            db_session.commit()
            return redirect(url_for('main', city_id=city_id))
        else:
            return render_template('edit.html', city_name = city_record.city.city_name, city_id=city_id, months=MONTHS, meteo=meteo)

    except Exception as error:
        return render_template('edit.html', city_name=city_record.city.city_name, city_id=city_id, months=MONTHS, meteo=meteo, error=error)


if __name__ == '__main__':
    app.run()
