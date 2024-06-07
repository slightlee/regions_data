# fetch_data.py
import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
}

# 省级数据
def fetch_province_data(url):

    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding  # 根据网页内容自动确定编码

    if response.status_code != 200:
        print('获取数据失败: 状态码', response.status_code)
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    provinces_list = []  # 初始化一个空列表来存储省份数据

    # 查找省份和直辖市
    province_table = soup.find('table', class_='provincetable')  # 根据实际的class名来确定
    if province_table:
        for province_tr in province_table.find_all('tr', class_='provincetr'):
            for province_td in province_tr.find_all('td'):
                province_details = {}  # 初始化一个字典来存储单个省份的数据
                if province_td.find('a'):
                    province_details['code'] = province_td.find('a')['href'].split('.')[0]
                    province_details['url'] = province_td.find('a')['href'].strip()
                    province_details['name'] = province_td.get_text().strip()
                    provinces_list.append(province_details)  # 将省份数据添加到列表中
    else:
        print("未找到省份信息表格。")

    return provinces_list


# 市辖区数据
def fetch_city_data(url):

    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding  # 根据网页内容自动确定编码

    if response.status_code != 200:
        print('获取数据失败: 状态码', response.status_code)
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    city_list = []  # 初始化一个空列表来存储城市数据

     # 查找城市市辖区数据
    city_table = soup.find('table', class_='citytable')
    if city_table:
        for city_tr in city_table.find_all('tr', class_='citytr'):
            city_details = {}  
            # 获取区划代码
            code_td = city_tr.find('td')
            if code_td:
                code_a = code_td.find('a')
                if code_a and 'href' in code_a.attrs:
                    city_details['code'] = code_a.text.strip()
                    city_details['url'] = code_a['href'].strip()
                else:
                    city_details['code'] = code_td.text.strip()  # 如：雄安新区  
                    city_details['url'] = ''      
            # 获取名称
            name_td = code_td.find_next_sibling('td')
            if name_td and name_td.find('a'):
                city_details['name'] = name_td.find('a').text.strip()
            # 如果字典不为空，则添加到列表中
            if city_details:
                city_list.append(city_details)
    else:
        print("未找到市辖区信息表格。")

    return city_list


# 区县数据
def fetch_county_data(url):

    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding  # 根据网页内容自动确定编码

    if response.status_code != 200:
        print('获取数据失败: 状态码', response.status_code)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    county_list = []  # 初始化一个空列表来存储区县数据

    # 查找区县的表格
    county_table = soup.find('table', class_='countytable')
    if county_table:
        for county_tr in county_table.find_all('tr', class_='countytr'):
            county_details = {}  
            # 获取区划代码
            code_td = county_tr.find('td')
            if code_td:
                code_a = code_td.find('a')
                if code_a and 'href' in code_a.attrs:
                    county_details['code'] = code_a.text.strip()
                    county_details['url'] = code_a['href'].strip()
                else:
                    county_details['code'] = code_td.text.strip()  # 如：河北省/石家庄市/市辖区  
                    county_details['url'] = ''      
            # 获取名称
            name_td = code_td.find_next_sibling('td')
            if name_td and name_td.find('a'):
                county_details['name'] = name_td.find('a').text.strip()
            else:
                county_details['name'] = name_td.text.strip()
            # 如果字典不为空，则添加到列表中
            if county_details:
                county_list.append(county_details)
    else:
        print("未找到区县信息表格。。")

    return county_list

# 乡镇街道数据
def fetch_town_data(url):
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding  # 根据网页内容自动确定编码

    if response.status_code != 200:
        print('获取数据失败: 状态码', response.status_code)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    town_list = [] 

    town_table = soup.find('table', class_='towntable')  
    if town_table:
        for town_tr in town_table.find_all('tr', class_='towntr'):
            town_details = {}  
            code_td = town_tr.find('td')
            if code_td and code_td.find('a'):
                town_details['code'] = code_td.find('a').text.strip()
                town_details['url'] = code_td.find('a')['href'].strip()
            name_td = code_td.find_next_sibling('td')
            if name_td and name_td.find('a'):
                town_details['name'] = name_td.find('a').text.strip()
            if town_details:
                town_list.append(town_details) 
    else:
        print("未找到乡镇街道信息表格。")

    return town_list


# 村级数据
def fetch_village_data(url):
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding

    if response.status_code != 200:
        print('获取数据失败: 状态码', response.status_code)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    village_list = [] 

    village_table = soup.find('table', class_='villagetable')  
    if village_table:
        for village_tr in village_table.find_all('tr', class_='villagetr'):
            village_details = {}  
            tds = village_tr.find_all('td')
            if len(tds) >= 3:
                village_details['code'] = tds[0].text.strip()
                village_details['classify_code'] = tds[1].text.strip()
                village_details['name'] = tds[2].text.strip()
                village_list.append(village_details) 
    else:
        print("未找到村级信息表格。")

    return village_list


# 拼接地址 
def fetch_url(base_url, _url):
    # 确保 base_url 以斜杠结束
    if not base_url.endswith('/'):
        base_url += '/'
    # 确保是字符串
    _url_str = str(_url)
    # 构建对应页面URL地址  
    __url = f"{base_url}{_url_str}"
    return __url
    