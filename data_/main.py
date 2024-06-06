from fetch_data import fetch_province_data, fetch_city_data, fetch_district_data, fetch_town_data, fetch_url
from database_ops import create_provinces_table, insert_province,get_all_provinces
from database_ops import create_city_table, insert_city,get_all_city
from database_ops import create_district_table, insert_district,get_all_district
from database_ops import create_town_table, insert_town
from time_logger import TimeLogger


base_url = '手动添加URL地址'


def op_provinces_data():
    create_provinces_table() 
    provinces_data = fetch_province_data(base_url)
    # 省级
    for province in provinces_data:
        print(province)
        insert_province(province['code'],province['name'],province['url'])
    print("省级数据插入完成！！！")


def op_city_data():
    create_city_table() 
    provinces_data = get_all_provinces()
    for province in provinces_data:
        city_url = fetch_url(base_url,province[2])
        city_data = fetch_city_data(city_url)
        province_code = province[0]
        if province_code not in ['11', '12', '31', '50']:
            for city in city_data:
                print(city)
                insert_city(city['code'],city['name'],province_code,city['url'])
        else:
           if city_data:  
            # print(f'特殊城市------{city_data[0]["name"]}---{city_data[0]["code"]}')
            insert_city(city_data[0]['code'], city_data[0]['name'], province_code, city_data[0]['url'])
    print("地级数据插入完成！！！")


def op_district_data():
    create_district_table()
    city_data = get_all_city()
    for city in city_data:
       if city[3]:
            district_url = fetch_url(base_url,city[3])
            district_data = fetch_district_data(district_url)
            city_code = city[0]
            p_code = city[2]
            for district in district_data:
                print(district)
                insert_district(district['code'],district['name'],city_code,p_code,district['url'])
    print("县级数据插入完成！！！")


def op_town_data():
    create_town_table()
    district_data = get_all_district()
    for district in district_data:
        town_url = fetch_url(base_url + district[3] + "/",district[4])
        town_data = fetch_town_data(town_url)
        district_code = district[0]
        p_code = district[3]
        for town in town_data:
            print(town)
            insert_town(town['code'],town['name'],district_code,p_code,town['url'])
    print("乡级数据插入完成！！！")


def main():

     # 创建 TimeLogger 实例
    time_logger = TimeLogger()

    # 开始时间
    time_logger.start()

    # op_provinces_data()
    # op_city_data()
    # op_district_data()
    op_town_data()

    # 结束时间
    time_logger.end()

    # 总耗时
    time_logger.duration()
    

if __name__ == '__main__':
    main()