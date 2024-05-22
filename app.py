from flask import Flask,render_template, jsonify
import sqlite3

app = Flask(__name__)

# 省级数据接口
@app.route('/api/provinces')
def get_provinces():
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    c.execute("SELECT code, name FROM provinces")
    provinces_data = c.fetchall()
    conn.close()
    return jsonify(provinces_data)

# 市级数据接口
@app.route('/api/cities/<province_code>')
def get_cities(province_code):
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    c.execute("SELECT code, name FROM city WHERE p_code = ?", (province_code,))
    cities_data = c.fetchall()
    conn.close()
    return jsonify(cities_data)

# 区县级数据接口
@app.route('/api/districts/<city_code>')
def get_districts(city_code):
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    c.execute("SELECT code, name FROM district WHERE c_code = ?", (city_code,))
    district_data = c.fetchall()
    conn.close()
    return jsonify(district_data)


# 示例页面
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)