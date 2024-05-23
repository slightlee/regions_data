## 项目说明：

> 本项目为中国行政区划数据，包括省级、地级、县级、乡级和村级五级行政区划数据。（初步完成前三级）

## 数据存储：

> 数据存储：
>
> sqlite3 db 数据文件 （其它格式根据需要再做补充）

## 数据来源：

> 国家统计局：
> https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2023/
>
> 【2023 年度全国统计用区划代码和城乡划分代码更新维护的标准时点调整为 2023 年 6 月 30 日】

## 数据同步时间：【2024-05-22】

## 声明：

> 本项目仅供交流学习使用，请勿用于违法用途，如有侵权，请联系删除。

## 使用方法：

> 1. 下载本项目
> 2. 安装依赖：`pip install -r requirements.txt`
> 3. 运行：`python main.py`
> 4. 生成的数据文件保存在 `regions.db` 中

### 预览效果

> 1. 运行： `python app.py`
> 2. 访问： `http://127.0.0.1:5000/`

![xg](./images/xg.gif)


## 拓展

> 1. 生成`requirements.txt`文件命令： `pipreqs ./ --encoding=utf8`