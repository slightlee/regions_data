"""
行政区划数据入库脚本
将清洗后的 JSON 数据导入 SQLite 数据库
"""

import json
import sqlite3
import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 依据 level 设定四类类型
LEVEL_TYPE_MAP = {
    1: ("省级", 1),
    2: ("地级", 2),
    3: ("县级", 3),
    4: ("乡级", 4),
}

class RegionsImporter:
    """行政区划数据导入器"""
    
    def __init__(self, db_path="data/regions.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """连接数据库"""
        try:
            # 确保数据库目录存在
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"成功连接数据库: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            sys.exit(1)
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
    
    def init_database(self):
        """初始化数据库表结构和索引"""
        logger.info("正在初始化数据库表结构...")
        
        # 1. 创建 regions 表
        self.cursor.execute("DROP TABLE IF EXISTS regions")
        self.cursor.execute("""
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
        """)
        self.cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS uk_code_year ON regions(code, year)")
        
        # 2. 创建类型字典表
        self.cursor.execute("DROP TABLE IF EXISTS region_type_dict")
        self.cursor.execute("""
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
        """)
        
        # 插入四类初始化数据
        init_data = [
            (1, '省级', 1, '省级行政单位', '广东省、山东省', 1),
            (2, '地级', 2, '地级行政单位', '广州市、延边州', 2),
            (3, '县级', 3, '县级行政单位', '海淀区、昆山市', 3),
            (4, '乡级', 4, '乡级行政单位', '某某街道、某某镇', 4),
        ]
        
        self.cursor.executemany("""
            INSERT INTO region_type_dict (type_code, type_name, level_range, description, region_examples, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        """, init_data)
        
        self.conn.commit()
        logger.info("数据库初始化完成")

    def build_path_map(self, regions):
        """构建 code 到 path 的映射"""
        logger.info("正在构建路径映射...")
        code_map = {r['code']: r for r in regions}
        path_map = {}
        
        def get_path(code):
            if code in path_map: return path_map[code]
            region = code_map.get(code)
            if not region: return code
            
            parent_code = region.get('parent_code')
            if not parent_code:
                path = code
            else:
                path = f"{get_path(parent_code)},{code}"
            
            path_map[code] = path
            return path

        for r in regions:
            get_path(r['code'])
        return path_map

    def import_data(self, json_path):
        """导入数据"""
        logger.info(f"开始从 {json_path} 导入数据...")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        regions = data.get("data", [])
        meta = data.get("meta", {})
        data_year = meta.get("year") or datetime.now().year
        
        path_map = self.build_path_map(regions)
        
        insert_sql = """
        INSERT OR IGNORE INTO regions (
            code, name, level, depth, parent_code, path,
            type, type_code, year, sort_order
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        total = len(regions)
        batch_size = 1000
        
        for i in range(0, total, batch_size):
            batch = regions[i:i+batch_size]
            batch_data = []
            for j, r in enumerate(batch):
                code = r.get("code")
                level = r.get("level")
                type_name, type_code = LEVEL_TYPE_MAP.get(level, (None, 0))
                batch_data.append((
                    code, r.get("name"), level, r.get("depth", level),
                    r.get("parent_code"), path_map.get(code, code),
                    type_name, type_code,
                    data_year, i + j + 1
                ))
            
            try:
                self.cursor.executemany(insert_sql, batch_data)
                self.conn.commit()
                logger.info(f"  进度: {min(i + batch_size, total)}/{total}")
            except Exception as e:
                logger.error(f"批量插入失败: {e}")
                self.conn.rollback()

        # 创建索引
        logger.info("正在创建索引...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_parent_code ON regions(parent_code)",
            "CREATE INDEX IF NOT EXISTS idx_level ON regions(level)",
            "CREATE INDEX IF NOT EXISTS idx_depth ON regions(depth)",
            "CREATE INDEX IF NOT EXISTS idx_path ON regions(path)",
            "CREATE INDEX IF NOT EXISTS idx_name ON regions(name)",
            "CREATE INDEX IF NOT EXISTS idx_type_code ON regions(type_code)",
        ]
        for idx in indexes:
            self.cursor.execute(idx)
        self.conn.commit()
        
        logger.info(f"导入完成！共 {total} 条记录。")

    def show_stats(self):
        """显示统计信息"""
        print("\n" + "=" * 50)
        print("数据统计分析:")
        print("-" * 50)
        
        # 总记录
        self.cursor.execute("SELECT COUNT(*) FROM regions")
        print(f"总记录数: {self.cursor.fetchone()[0]:,}")
        
        # 行政级别统计
        self.cursor.execute("SELECT level, COUNT(*) FROM regions GROUP BY level ORDER BY level")
        print("\n行政级别分布:")
        level_names = {1: "省级", 2: "地级", 3: "县级", 4: "乡级"}
        for lv, count in self.cursor.fetchall():
            print(f"  {level_names.get(lv, f'Level {lv}')}: {count:,}")
            
        print("=" * 50)

def main():
    processed_dir = Path("data/processed")
    db_path = "data/regions.db"
    # 自定义数据文件路径（优先使用命令行参数）
    json_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if json_arg and not json_arg.exists():
        logger.error(f"指定的数据文件不存在: {json_arg}")
        sys.exit(1)
    if json_arg:
        latest_json = json_arg
    else:
        if not processed_dir.exists():
            logger.error(f"目录不存在: {processed_dir}")
            sys.exit(1)
        json_files = sorted(processed_dir.glob("regions_*.json"), reverse=True)
        if not json_files:
            logger.error(f"在 {processed_dir} 中找不到清洗后的数据文件")
            sys.exit(1)
        latest_json = json_files[0]
    
    importer = RegionsImporter(db_path)
    try:
        importer.connect()
        importer.init_database()
        importer.import_data(latest_json)
        importer.show_stats()
    finally:
        importer.close()

if __name__ == "__main__":
    main()
