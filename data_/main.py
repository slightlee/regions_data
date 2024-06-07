from fetch_data import fetch_province_data, fetch_city_data, fetch_county_data, fetch_town_data,fetch_village_data,fetch_url
from database_ops import create_provinces_table, insert_province,get_all_provinces
from database_ops import create_city_table, insert_city,get_all_city
from database_ops import create_county_table, insert_county,get_all_county
from database_ops import create_town_table,insert_town,get_all_town
from database_ops import create_village_table,insert_village
from time_logger import TimeLogger


base_url = 'https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2023/'


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
                for city in city_data:
                    # print(f'特殊城市------{city["name"]}---{city["code"]}')
                    insert_city(city['code'], city['name'], province_code, city['url'])
    print("地级数据插入完成！！！")


def op_county_data():
    create_county_table()
    city_data = get_all_city()
    for city in city_data:
       if city[3]:
            county_url = fetch_url(base_url,city[3])
            county_data = fetch_county_data(county_url)
            city_code = city[0]
            p_code = city[2]
            for county in county_data:
                print(county)
                insert_county(county['code'],county['name'],city_code,p_code,county['url'])
    print("县级数据插入完成！！！")


def op_town_data():
    create_town_table()
    county_data = get_all_county()
    for county in county_data:
        town_url = fetch_url(base_url + county[3] + "/",county[4])
        town_data = fetch_town_data(town_url)
        county_code = county[0]
        p_code = county[3]
        c_c_code = county[4].split('/')[0] 
        for town in town_data:
            print(town)
            insert_town(town['code'],town['name'],county_code,p_code,c_c_code,town['url'])
    print("乡级数据插入完成！！！")


def op_village_data():
    create_village_table()
    town_data = get_all_town()
    for town in town_data:
        province_code = town[3]
        village_url = fetch_url(base_url + province_code + "/" + town[4] ,town[5])
        village_data = fetch_village_data(village_url)
        town_code = town[0]
        for village in village_data:
            print(village)
            insert_village(village['code'],village['name'],town_code,village['classify_code'])
    print("村级数据插入完成！！！")


def main():

     # 创建 TimeLogger 实例
    time_logger = TimeLogger()

    # 开始时间
    time_logger.start()

    # op_provinces_data()
    op_city_data()
    # op_county_data()
    # op_town_data()
    # op_village_data()

    # 结束时间
    time_logger.end()

    # 总耗时
    time_logger.duration()
    

if __name__ == '__main__':
    main()