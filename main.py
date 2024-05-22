from fetch_data import fetch_province_data,fetch_city_data,fetch_district_data,fetch_url
from database_ops import create_provinces_table, insert_province, check_provinces_data, create_city_table,insert_city,check_city_data,create_district_table,insert_district,check_district_data


base_url = 'https://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2023/'


def main():
    create_provinces_table() 
    create_city_table()
    create_district_table()
    provinces_data = fetch_province_data(base_url)
    for province in provinces_data:
        insert_province(province['code'],province['name'])
        city_url = fetch_url(base_url,province['url'])
        city_data = fetch_city_data(city_url)
        province_code = province['code']
        if province_code not in ['11', '12', '31', '50']:
            for city in city_data:
                # print(city)
                insert_city(city['code'],city['name'],province_code)
                print(city)
                district_url = fetch_url(base_url,city['url'])
                district_data = fetch_district_data(district_url)
                city_code = city['code']
                for district in district_data:
                    insert_district(district['code'],district['name'],city_code)
                
        else:
           if city_data:  
            # print(f'特殊城市------{city_data[0]["name"]}---{city_data[0]["code"]}')
            insert_city(city_data[0]['code'], city_data[0]['name'], province_code)

            district_url = fetch_url(base_url,city_data[0]['url'])
            district_data = fetch_district_data(district_url)
            city_code = city_data[0]['code']
            for district in district_data:
                insert_district(district['code'],district['name'],city_code)

           else:
               print('未找到城市数据')



    # 检查并打印数据库中所有省份的数据
    # check_city_data()





if __name__ == '__main__':
    main()