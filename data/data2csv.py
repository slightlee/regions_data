import json
import csv
import os


def json_to_csv(json_file_path, csv_file_path, headers):
    """
    将 JSON 文件转换为 CSV 文件。

    参数:
    - json_file_path: JSON 文件的路径
    - csv_file_path: CSV 文件的路径
    - headers: CSV 文件的表头和对应的 JSON 键
    """
    csv_directory = os.path.dirname(csv_file_path)

    # 确保目标目录存在
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)

    # 读取 JSON 文件
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    # 写入 CSV 文件
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)

        # 写入表头
        writer.writerow(headers.keys())

        # 写入数据
        for item in data:
            row = [item.get(headers[key], "") for key in headers]
            writer.writerow(row)


# 定义文件路径和对应的表头
files = [
    {
        "json": "./json/province.json",
        "csv": "./csv/province.csv",
        "headers": {"code": "code", "name": "name"},
    },
    {
        "json": "./json/city.json",
        "csv": "./csv/city.csv",
        "headers": {"code": "code", "name": "name", "p_code": "p_code"},
    },
    {
        "json": "./json/county.json",
        "csv": "./csv/county.csv",
        "headers": {"code": "code", "name": "name", "c_code": "c_code"},
    },
    {
        "json": "./json/town.json",
        "csv": "./csv/town.csv",
        "headers": {"code": "code", "name": "name", "c_code": "c_code"},
    },
    {
        "json": "./json/village.json",
        "csv": "./csv/village.csv",
        "headers": {"code": "code", "name": "name", "t_code": "t_code"},
    },
]

# 执行转换
for file in files:
    json_to_csv(file["json"], file["csv"], file["headers"])
