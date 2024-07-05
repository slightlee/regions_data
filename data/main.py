# 保留基础表结构数据、保存json格式数据
import sqlite3
import sys
import json
import os
from tqdm import tqdm

sys.path.append("..")

from data_.database_ops import (
    get_all_provinces,
    get_all_city,
    get_all_county,
    get_all_town,
    get_all_village,
)

from data_ops import (
    create_provinces_table,
    insert_province,
    create_city_table,
    insert_city,
    create_county_table,
    insert_county,
    create_town_table,
    create_village_table,
)


def write_to_json(data, keys, output_file):
    # 列表推导式
    data_list = [dict(zip(keys, item)) for item in data]

    # 获取保存文件的路径
    output_path = os.path.join(os.path.dirname(__file__), "json", output_file)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 将数据写入 JSON 文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)


# 省数据


def write_provinces_to_json(provinces_data, output_file="province.json"):
    keys = ["code", "name"]
    write_to_json(provinces_data, keys, output_file)


def op_provinces_data():
    create_provinces_table()
    provinces_data = get_all_provinces()
    with tqdm(total=len(provinces_data), desc="🚀省数据插入中", ncols=100) as pbar:
        for province in provinces_data:
            insert_province(province[0], province[1])
            pbar.update()
    write_provinces_to_json(provinces_data)


# 市数据


def write_city_to_json(city_data, output_file="city.json"):
    keys = ["code", "name", "p_code"]
    write_to_json(city_data, keys, output_file)


def op_citys_data():
    create_city_table()
    city_data = get_all_city()
    with tqdm(total=len(city_data), desc="🚀🚀市数据插入中", ncols=100) as pbar:
        for city in city_data:
            insert_city(city[0], city[1], city[2])
            pbar.update()
    write_city_to_json(city_data)


# 区县数据


def write_county_to_json(county_data, output_file="county.json"):
    keys = ["code", "name", "c_code"]
    write_to_json(county_data, keys, output_file)


def op_countys_data():
    create_county_table()
    county_data = get_all_county()
    with tqdm(total=len(county_data), desc="🚀🚀🚀区县数据插入中", ncols=100) as pbar:
        for county in county_data:
            insert_county(county[0], county[1], county[2])
            pbar.update()
    write_county_to_json(county_data)


# 乡镇数据


def write_town_to_json(town_data, output_file="town.json"):
    keys = ["code", "name", "c_code"]
    write_to_json(town_data, keys, output_file)


def op_towns_data():
    create_town_table()
    town_data = get_all_town()

    towns_to_insert = [(town[0], town[1], town[2]) for town in town_data]

    # 将数据分成适当大小的批次
    batch_size = 1000
    batches = [
        towns_to_insert[i : i + batch_size]
        for i in range(0, len(towns_to_insert), batch_size)
    ]

    with tqdm(
        total=len(towns_to_insert), desc="🚀🚀🚀🚀🚀乡镇数据插入中", ncols=100
    ) as pbar:
        conn = sqlite3.connect("./sqlite/regions.db")
        try:
            conn.execute("BEGIN TRANSACTION")

            for batch in batches:
                insert_towns(conn, batch)
                pbar.update(len(batch))

            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
        finally:
            conn.close()

    write_town_to_json(town_data)


def insert_towns(conn, towns):
    try:
        c = conn.cursor()
        c.executemany(
            """
            INSERT INTO town (code, name, c_code) 
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """,
            towns,
        )
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        conn.rollback()
    else:
        conn.commit()


# 村数据


def write_village_to_json(village_data, output_file="village.json"):
    keys = ["code", "name", "t_code"]
    write_to_json(village_data, keys, output_file)


def op_villages_data():
    create_village_table()
    village_data = get_all_village()

    villages_to_insert = [
        (village[0], village[1], village[2]) for village in village_data
    ]

    # 将数据分成适当大小的批次
    batch_size = 1000
    batches = [
        villages_to_insert[i : i + batch_size]
        for i in range(0, len(villages_to_insert), batch_size)
    ]

    with tqdm(
        total=len(villages_to_insert), desc="🚀🚀🚀🚀🚀村数据插入中", ncols=100
    ) as pbar:
        conn = sqlite3.connect("./sqlite/regions.db")
        try:
            conn.execute("BEGIN TRANSACTION")

            for batch in batches:
                insert_villages(conn, batch)
                pbar.update(len(batch))

            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error: {e}")
        finally:
            conn.close()

    write_village_to_json(village_data)


def insert_villages(conn, villages):
    try:
        c = conn.cursor()
        c.executemany(
            """
            INSERT INTO village (code, name, t_code) 
            VALUES (?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
            name = excluded.name;
            """,
            villages,
        )
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        conn.rollback()
    else:
        conn.commit()


def main():

    op_provinces_data()
    op_citys_data()
    op_countys_data()
    op_towns_data()
    op_villages_data()


if __name__ == "__main__":
    main()
