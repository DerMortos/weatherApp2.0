from flask import Flask, render_template, send_file
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


@app.route('/city/<int:city_id>')
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


if __name__ == '__main__':
    app.run(debug=True)
