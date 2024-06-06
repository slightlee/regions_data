# database_ops.py
import sqlite3

# 省级表
def create_provinces_table():
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    with conn:
        c.execute('''
                CREATE TABLE IF NOT EXISTS provinces (
                    code TEXT UNIQUE,
                    name TEXT,
                    url TEXT
                )''')

# 插入省级表
def insert_province(code,name,url):
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute("""
            INSERT INTO provinces (code, name, url) 
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """, (code, name, url))
    conn.commit()
    conn.close()


# 获取省级数据
def get_all_provinces():
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute('SELECT code, name, url FROM provinces')
    provinces = c.fetchall()
    conn.close()
    return provinces
    

# 市级表
def create_city_table():
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    with conn:
        c.execute('''
                CREATE TABLE IF NOT EXISTS city (
                    code TEXT UNIQUE,
                    name TEXT,
                    p_code TEXT,
                    url TEXT
                )''')

# 插入市级表
def insert_city(code,name,p_code,url):
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute("""
            INSERT INTO city (code, name, p_code, url) 
            VALUES (?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """, (code, name, p_code, url))
    conn.commit()
    conn.close()

# 获取市级数据
def get_all_city():
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute('SELECT * FROM city')
    city = c.fetchall()
    conn.close()
    return city


# 区县级表
def create_district_table():
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    with conn:
        c.execute('''
                CREATE TABLE IF NOT EXISTS district (
                    code TEXT UNIQUE,
                    name TEXT,
                    c_code TEXT,
                    p_code TEXT,
                    url TEXT
                )''')

# 插入区县级表
def insert_district(code,name,c_code,p_code,url):
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute("""
            INSERT INTO district (code, name, c_code, p_code, url) 
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """, (code, name ,c_code, p_code, url))
    conn.commit()
    conn.close()


# 获取区县级数据
def get_all_district():
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute('SELECT * FROM district')
    district = c.fetchall()
    conn.close()
    return district


# 乡镇街道表
def create_town_table():
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    with conn:
        c.execute('''
                CREATE TABLE IF NOT EXISTS town (
                    code TEXT UNIQUE,
                    name TEXT,
                    c_code TEXT,
                    p_code TEXT,
                    url TEXT
                )''')

# 插入乡镇街道表
def insert_town(code,name,c_code,p_code,url):
    conn = sqlite3.connect('../regions.db')
    c = conn.cursor()
    c.execute("""
            INSERT INTO town (code, name, c_code, p_code, url) 
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """, (code, name, c_code, p_code, url))
    conn.commit()
    conn.close()

