"""
行政区划数据入库脚本
将 JSON 数据导入 SQLite 数据库
"""

import json
import sqlite3
import os
from datetime import datetime


# type -> type_code 映射表
TYPE_CODE_MAP = {
    # 省级 (level=1)
    "省": 1,
    "直辖市": 2,
    "自治区": 3,
    "特别行政区": 4,
    # 地级 (level=2)
    "地级市": 10,
    "自治州": 11,
    "盟": 12,
    "地区": 13,
    # 县级 (level=3)
    "市辖区": 20,
    "县": 21,
    "县级市": 22,
    "自治县": 23,
    "旗": 24,
    "自治旗": 25,
    "林区": 26,
    "特区": 27,
    # 乡镇级 (level=4)
    "街道": 30,
    "镇": 31,
    "乡": 32,
    "民族乡": 33,
    "苏木": 34,
    "民族苏木": 35,
    "区公所": 36,
    # 新疆特有
    "团": 37,
    "农场": 38,
    "牧场": 39,
}


class RegionsImporter:
    """行政区划数据导入器"""
    
    def __init__(self, db_path="regions.db"):
        """
        初始化导入器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
    
    def create_table(self):
        """创建表结构"""
        # 删除旧表（如果存在）
        self.cursor.execute("DROP TABLE IF EXISTS regions")
        
        # 创建新表
        create_sql = """
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code VARCHAR(12) NOT NULL,
            name VARCHAR(100) NOT NULL,
            level TINYINT NOT NULL,
            depth TINYINT NOT NULL,
            parent_code VARCHAR(12),
            path VARCHAR(200),
            type VARCHAR(20),
            type_code TINYINT,
            year SMALLINT,
            status TINYINT NOT NULL DEFAULT 1,
            is_deleted TINYINT NOT NULL DEFAULT 0,
            sort_order INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_sql)
        
        # 创建唯一约束（code + year）
        self.cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS uk_code_year 
            ON regions(code, year)
        """)
        
        self.conn.commit()
        print("regions 表创建完成")
    
    def create_type_dict_table(self):
        """创建类型字典表"""
        # 删除旧表（如果存在）
        self.cursor.execute("DROP TABLE IF EXISTS region_type_dict")
        
        # 创建字典表
        create_sql = """
        CREATE TABLE IF NOT EXISTS region_type_dict (
            type_code INTEGER PRIMARY KEY,
            type_name VARCHAR(20) NOT NULL,
            level_range TINYINT NOT NULL,
            description VARCHAR(100),
            region_examples VARCHAR(200),
            sort_order INT DEFAULT 0,
            status TINYINT NOT NULL DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_sql)
        
        # 插入初始化数据
        init_data = [
            # 省级 (level=1)
            (1, '省', 1, '普通省份', '广东省、山东省', 1),
            (2, '直辖市', 1, '直辖市', '北京市、上海市、天津市、重庆市', 2),
            (3, '自治区', 1, '少数民族自治区', '内蒙古、广西、西藏、宁夏、新疆', 3),
            (4, '特别行政区', 1, '特别行政区', '香港、澳门', 4),
            # 地级 (level=2)
            (10, '地级市', 2, '地级行政单位', '广州市、深圳市', 10),
            (11, '自治州', 2, '少数民族自治州', '延边朝鲜族自治州', 11),
            (12, '盟', 2, '内蒙古特有地级单位', '锡林郭勒盟', 12),
            (13, '地区', 2, '地区行政公署', '阿里地区', 13),
            # 县级 (level=3)
            (20, '市辖区', 3, '市辖区', '海淀区、天河区', 20),
            (21, '县', 3, '县', '从化县', 21),
            (22, '县级市', 3, '县级市', '昆山市', 22),
            (23, '自治县', 3, '少数民族自治县', '连南瑶族自治县', 23),
            (24, '旗', 3, '内蒙古特有县级单位', '正蓝旗', 24),
            (25, '自治旗', 3, '少数民族自治旗', '鄂伦春自治旗', 25),
            (26, '林区', 3, '特殊县级单位', '神农架林区', 26),
            (27, '特区', 3, '特殊县级单位', '六枝特区', 27),
            # 乡镇级 (level=4)
            (30, '街道', 4, '街道办事处', '东华门街道', 30),
            (31, '镇', 4, '镇', '虎门镇', 31),
            (32, '乡', 4, '乡', '某某乡', 32),
            (33, '民族乡', 4, '少数民族乡', '某某瑶族乡', 33),
            (34, '苏木', 4, '内蒙古特有乡级单位', '某某苏木', 34),
            (35, '民族苏木', 4, '少数民族苏木', '某某达斡尔族苏木', 35),
            (36, '区公所', 4, '特殊乡级单位', '某某区公所', 36),
            (37, '团', 4, '新疆兵团特有', '某某团', 37),
            (38, '农场', 4, '新疆兵团特有', '某某农场', 38),
            (39, '牧场', 4, '新疆兵团特有', '某某牧场', 39),
        ]
        
        insert_sql = """
        INSERT INTO region_type_dict (type_code, type_name, level_range, description, region_examples, sort_order)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        for item in init_data:
            self.cursor.execute(insert_sql, item)
        
        self.conn.commit()
        print(f"region_type_dict 表创建完成，共 {len(init_data)} 条记录")
    
    def create_indexes(self):
        """创建索引"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_parent_code ON regions(parent_code)",
            "CREATE INDEX IF NOT EXISTS idx_level ON regions(level)",
            "CREATE INDEX IF NOT EXISTS idx_depth ON regions(depth)",
            "CREATE INDEX IF NOT EXISTS idx_path ON regions(path)",
            "CREATE INDEX IF NOT EXISTS idx_name ON regions(name)",
            "CREATE INDEX IF NOT EXISTS idx_status ON regions(status, is_deleted)",
            "CREATE INDEX IF NOT EXISTS idx_type_code ON regions(type_code)",
        ]
        
        for idx_sql in indexes:
            self.cursor.execute(idx_sql)
        
        self.conn.commit()
        print("索引创建完成")
    
    def build_path_map(self, regions):
        """
        构建 path 映射（从 parent_code 推导完整路径）
        
        Args:
            regions: 区划数据列表
        
        Returns:
            code -> path 的映射字典
        """
        # 先建立 code -> parent_code 映射
        parent_map = {}
        for r in regions:
            parent_map[r["code"]] = r.get("parent_code")
        
        # 计算每个 code 的完整路径
        path_map = {}
        
        def get_path(code):
            if code in path_map:
                return path_map[code]
            
            parent = parent_map.get(code)
            if not parent:
                path_map[code] = code
                return code
            
            parent_path = get_path(parent)
            path_map[code] = f"{parent_path},{code}"
            return path_map[code]
        
        for r in regions:
            get_path(r["code"])
        
        return path_map
    
    def import_data(self, json_path, year=None):
        """
        导入 JSON 数据
        
        Args:
            json_path: JSON 文件路径
            year: 数据年份（覆盖 JSON 中的 year）
        """
        print(f"正在读取: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取元数据和区划数据
        meta = data.get("meta", {})
        regions = data.get("data", [])
        
        if not regions:
            print("没有数据可导入！")
            return
        
        data_year = year or meta.get("year")
        print(f"数据年份: {data_year or '最新'}")
        print(f"总记录数: {len(regions)}")
        
        # 构建 path 映射
        print("正在构建路径映射...")
        path_map = self.build_path_map(regions)
        
        # 插入数据
        print("正在导入数据...")
        
        insert_sql = """
        INSERT INTO regions (
            code, name, level, depth, parent_code, path,
            type, type_code, year, sort_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        batch_size = 1000
        total = len(regions)
        
        for i, region in enumerate(regions, 1):
            code = region.get("code")
            name = region.get("name")
            level = region.get("level")
            depth = region.get("depth")
            parent_code = region.get("parent_code")
            path = path_map.get(code, code)
            region_type = region.get("type")
            type_code = TYPE_CODE_MAP.get(region_type, 0)
            sort_order = i  # 使用插入顺序作为排序
            
            try:
                self.cursor.execute(insert_sql, (
                    code, name, level, depth, parent_code, path,
                    region_type, type_code, data_year, sort_order
                ))
            except sqlite3.IntegrityError as e:
                print(f"跳过重复记录: {code} - {name}")
            
            if i % batch_size == 0:
                self.conn.commit()
                print(f"  进度: {i}/{total} ({i*100//total}%)")
        
        self.conn.commit()
        print(f"导入完成: {total} 条记录")
    
    def show_stats(self):
        """显示统计信息"""
        print("\n" + "=" * 50)
        print("数据统计:")
        
        # 总记录数
        self.cursor.execute("SELECT COUNT(*) FROM regions")
        total = self.cursor.fetchone()[0]
        print(f"  总记录数: {total}")
        
        # 按 level 统计
        self.cursor.execute("""
            SELECT level, COUNT(*) as cnt 
            FROM regions 
            GROUP BY level 
            ORDER BY level
        """)
        print("\n  按 level 统计:")
        for row in self.cursor.fetchall():
            print(f"    level {row[0]}: {row[1]}")
        
        # 按 type 统计 (前10)
        self.cursor.execute("""
            SELECT type, COUNT(*) as cnt 
            FROM regions 
            GROUP BY type 
            ORDER BY cnt DESC 
            LIMIT 10
        """)
        print("\n  按 type 统计 (Top 10):")
        for row in self.cursor.fetchall():
            print(f"    {row[0]}: {row[1]}")


def main():
    """主函数"""
    import sys
    
    # 默认参数
    db_path = "regions.db"
    json_path = None
    
    # 查找最新的 JSON 文件
    data_dir = "data"
    if os.path.exists(data_dir):
        json_files = [f for f in os.listdir(data_dir) if f.startswith("regions_") and f.endswith(".json") and "progress" not in f]
        if json_files:
            json_files.sort(reverse=True)
            json_path = os.path.join(data_dir, json_files[0])
    
    if not json_path:
        print("错误: 找不到 JSON 数据文件！")
        print("请先运行 fetch_regions.py 爬取数据")
        sys.exit(1)
    
    print(f"数据库: {db_path}")
    print(f"数据源: {json_path}")
    print("-" * 50)
    
    importer = RegionsImporter(db_path)
    
    try:
        importer.connect()
        importer.create_table()
        importer.create_type_dict_table()
        importer.import_data(json_path)
        importer.create_indexes()
        importer.show_stats()
    finally:
        importer.close()
    
    print("\n完成！")


if __name__ == "__main__":
    main()
