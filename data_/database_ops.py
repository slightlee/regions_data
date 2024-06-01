# database_ops.py
import sqlite3

# 省级表
def create_provinces_table():
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    with conn:
        c.execute('''
                CREATE TABLE IF NOT EXISTS provinces (
                    code TEXT UNIQUE,
                    name TEXT
                )''')

# 插入省级表
def insert_province(code,name):
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    c.execute("""
            INSERT INTO provinces (code, name) 
            VALUES (?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """, (code, name))
    conn.commit()
    conn.close()

# 查看数据
def check_provinces_data():
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM provinces'):
        print(row)
    conn.close()

# 市级表
def create_city_table():
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    with conn:
        c.execute('''
                CREATE TABLE IF NOT EXISTS city (
                    code TEXT UNIQUE,
                    name TEXT,
                    p_code TEXT
                )''')

# 插入市级表
def insert_city(code,name,p_code):
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    c.execute("""
            INSERT INTO city (code, name ,p_code) 
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """, (code, name ,p_code))
    conn.commit()
    conn.close()

# 查看市级数据
def check_city_data():
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM city'):
        print(row)
    conn.close()



# 区县级表
def create_district_table():
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    with conn:
        c.execute('''
                CREATE TABLE IF NOT EXISTS district (
                    code TEXT UNIQUE,
                    name TEXT,
                    c_code TEXT
                )''')

# 插入区县级表
def insert_district(code,name,c_code):
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    c.execute("""
            INSERT INTO district (code, name ,c_code) 
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """, (code, name ,c_code))
    conn.commit()
    conn.close()

# 查看区县级数据
def check_district_data():
    conn = sqlite3.connect('regions.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM district'):
        print(row)
    conn.close()
