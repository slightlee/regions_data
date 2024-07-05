# database_ops.py
import sqlite3


# 省级表
def create_provinces_table():
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    with conn:
        c.execute(
            """
                CREATE TABLE IF NOT EXISTS province (
                    code TEXT UNIQUE,
                    name TEXT
                )"""
        )


# 插入省级表
def insert_province(code, name):
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    c.execute(
        """
            INSERT INTO province (code, name) 
            VALUES (?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """,
        (code, name),
    )
    conn.commit()
    conn.close()


# 市级表
def create_city_table():
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    with conn:
        c.execute(
            """
                CREATE TABLE IF NOT EXISTS city (
                    code TEXT UNIQUE,
                    name TEXT,
                    p_code TEXT
                )"""
        )


# 插入市级表
def insert_city(code, name, p_code):
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    c.execute(
        """
            INSERT INTO city (code, name, p_code) 
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """,
        (code, name, p_code),
    )
    conn.commit()
    conn.close()


# 区县级表
def create_county_table():
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    with conn:
        c.execute(
            """
                CREATE TABLE IF NOT EXISTS county (
                    code TEXT UNIQUE,
                    name TEXT,
                    c_code TEXT
                )"""
        )


# 插入区县级表
def insert_county(code, name, c_code):
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    c.execute(
        """
            INSERT INTO county (code, name, c_code) 
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """,
        (code, name, c_code),
    )
    conn.commit()
    conn.close()


# 乡镇街道表
def create_town_table():
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    with conn:
        c.execute(
            """
                CREATE TABLE IF NOT EXISTS town (
                    code TEXT UNIQUE,
                    name TEXT,
                    c_code TEXT
                )"""
        )


# 插入乡镇街道表
def insert_town(code, name, c_code):
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    c.execute(
        """
            INSERT INTO town (code, name, c_code) 
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """,
        (code, name, c_code),
    )
    conn.commit()
    conn.close()


def create_village_table():
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    with conn:
        c.execute(
            """
                CREATE TABLE IF NOT EXISTS village (
                    code TEXT UNIQUE,
                    name TEXT,
                    t_code TEXT
                )"""
        )


# 插入村级表
def insert_village(code, name, t_code):
    conn = sqlite3.connect("./sqlite/regions.db")
    c = conn.cursor()
    c.execute(
        """
            INSERT INTO village (code, name, t_code) 
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """,
        (code, name, t_code),
    )
    conn.commit()
    conn.close()
