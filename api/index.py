from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import sqlite3
from typing import List
import uvicorn

app = FastAPI()

# 省级数据接口
@app.get("/api/provinces")
def get_provinces():
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute("SELECT code, name FROM provinces")
    provinces_data = c.fetchall()
    conn.close()
    return provinces_data


# 市级数据接口
@app.get('/api/cities/{province_code}')
def get_cities(province_code: str):
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute("SELECT code, name FROM city WHERE p_code = ?", (province_code,))
    cities_data = c.fetchall()
    conn.close()
    return cities_data


# 区县级数据接口
@app.get('/api/districts/{city_code}')
def get_districts(city_code: str):
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute("SELECT code, name FROM district WHERE c_code = ?", (city_code,))
    district_data = c.fetchall()
    conn.close()
    return district_data


templates = Jinja2Templates(directory="../templates")

# 创建一个 route，当访问根目录 "/" 时，使用模板引擎渲染 index.html
@app.get("/")
async def read_index(request: Request):
    # 'request': request 是必须的，因为Jinja2Templates.render方法需要它来构造模板的上下文
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    # 对应 'index:app'
    # 其中 'index' 是文件名（不含 '.py'），'app' 是 FastAPI 实例的变量名
    uvicorn.run("index:app", host="127.0.0.1", port=8000, reload=True)