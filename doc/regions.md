# 行政区划数据库表结构设计

## 概述

本文档描述了用于存储中国行政区划数据的 SQLite 数据库表结构设计。数据来源于民政部地名信息库接口。

---

## 数据特点分析

### 层级结构

| level | depth | 说明 | 示例 |
|-------|-------|------|------|
| 0 | 0 | 根节点 | 全国 |
| 1 | 1 | 省级 | 北京市、广东省、香港特别行政区 |
| 2 | 2 | 地级 | 广州市、深圳市 |
| 3 | 2/3 | 县级 | 海淀区、天河区 |
| 4 | 3/4 | 乡镇级 | 沙面街道、东华门街道 |

> [!IMPORTANT]
> `level` 是 API 返回的原始值，`depth` 是程序计算的相对深度（用于 UI 级联展示）。

### 直辖市与普通省份的差异

**普通省份：**
```
省 (level=1, depth=1) → 地级市 (level=2, depth=2) → 区县 (level=3, depth=3) → 街道 (level=4, depth=4)
```

**直辖市：**
```
直辖市 (level=1, depth=1) → 市辖区 (level=3, depth=2) → 街道 (level=4, depth=3)
```

### 行政区划类型

> [!NOTE]
> 以下 26 种类型来源于 API 实际返回数据（共 42,176 条记录统计）。

| type | type_code | level | 数量 | 说明 |
|------|-----------|-------|------|------|
| 省 | 1 | 1 | 23 | 普通省份 |
| 直辖市 | 2 | 1 | 4 | 北京、上海、天津、重庆 |
| 自治区 | 3 | 1 | 5 | 内蒙古、广西、西藏、宁夏、新疆 |
| 特别行政区 | 4 | 1 | 2 | 香港、澳门 |
| 地级市 | 10 | 2 | 293 | 地级行政单位 |
| 自治州 | 11 | 2 | 30 | 少数民族自治州 |
| 盟 | 12 | 2 | 3 | 内蒙古特有 |
| 地区 | 13 | 2 | 7 | 地区行政公署 |
| 市辖区 | 20 | 3 | 977 | 市辖区 |
| 县 | 21 | 3 | 1301 | 县 |
| 县级市 | 22 | 3 | 397 | 县级市 |
| 自治县 | 23 | 3 | 117 | 自治县 |
| 旗 | 24 | 3 | 49 | 内蒙古特有 |
| 自治旗 | 25 | 3 | 3 | 内蒙古特有 |
| 林区 | 26 | 3 | 1 | 神农架林区 |
| 特区 | 27 | 3 | 1 | 六枝特区 |
| 街道 | 30 | 4 | 9153 | 街道办事处 |
| 镇 | 31 | 4 | 21578 | 镇 |
| 乡 | 32 | 4 | 7047 | 乡 |
| 民族乡 | 33 | 4 | 962 | 少数民族乡 |
| 苏木 | 34 | 4 | 153 | 内蒙古特有 |
| 民族苏木 | 35 | 4 | 1 | 内蒙古特有 |
| 区公所 | 36 | 4 | 2 | 特殊行政单位 |
| 团 | 37 | 4 | 51 | 新疆兵团特有 |
| 农场 | 38 | 4 | 15 | 新疆兵团特有 |
| 牧场 | 39 | 4 | 1 | 新疆兵团特有 |

---

## 表结构设计

### regions 表

```sql
CREATE TABLE IF NOT EXISTS regions (
    -- ========== 主键 ==========
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- ========== 核心业务字段 ==========
    code VARCHAR(12) NOT NULL,              -- 行政区划代码
    name VARCHAR(100) NOT NULL,             -- 标准名称
    
    -- ========== 层级关系 ==========
    level TINYINT NOT NULL,                 -- API 原始级别 (0-4)
    depth TINYINT NOT NULL,                 -- 相对深度 (1-4，统一层级用于 UI)
    parent_code VARCHAR(12),                -- 父级区划代码
    path VARCHAR(200),                      -- 完整路径，如 "440000,440100,440103"
    
    -- ========== 分类字段 ==========
    type VARCHAR(20),                       -- 区划类型（中文）
    type_code TINYINT,                      -- 类型编码（枚举）
    
    -- ========== 版本控制 ==========
    year SMALLINT NOT NULL,                 -- 数据年份版本
    
    -- ========== 状态管理 ==========
    status TINYINT NOT NULL DEFAULT 1,      -- 1=有效 0=无效
    is_deleted TINYINT NOT NULL DEFAULT 0,  -- 软删除标记
    
    -- ========== 排序 ==========
    sort_order INT DEFAULT 0,               -- 排序权重
    
    -- ========== 审计字段 ==========
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- ========== 唯一约束 ==========
    UNIQUE (code, year)
);
```

### 索引设计

```sql
-- 业务查询索引
CREATE UNIQUE INDEX IF NOT EXISTS uk_code_year ON regions(code, year);
CREATE INDEX IF NOT EXISTS idx_parent_code ON regions(parent_code);
CREATE INDEX IF NOT EXISTS idx_level ON regions(level);
CREATE INDEX IF NOT EXISTS idx_depth ON regions(depth);
CREATE INDEX IF NOT EXISTS idx_path ON regions(path);

-- 名称搜索索引
CREATE INDEX IF NOT EXISTS idx_name ON regions(name);

-- 状态筛选索引
CREATE INDEX IF NOT EXISTS idx_status ON regions(status, is_deleted);

-- 类型筛选索引
CREATE INDEX IF NOT EXISTS idx_type_code ON regions(type_code);
```

### region_type_dict 表（类型字典）

存储行政区划类型的元数据，便于独立维护和扩展。

```sql
CREATE TABLE IF NOT EXISTS region_type_dict (
    -- ========== 主键 ==========
    type_code INTEGER PRIMARY KEY,              -- 类型编码
    
    -- ========== 核心字段 ==========
    type_name VARCHAR(20) NOT NULL,             -- 类型名称（中文）
    level_range TINYINT NOT NULL,               -- 所属行政级别 (1-4)
    
    -- ========== 描述信息 ==========
    description VARCHAR(100),                   -- 详细说明
    region_examples VARCHAR(200),               -- 示例区划
    
    -- ========== 排序和状态 ==========
    sort_order INT DEFAULT 0,                   -- 排序权重
    status TINYINT NOT NULL DEFAULT 1,          -- 1=有效 0=无效
    
    -- ========== 审计字段 ==========
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 字典表初始化数据

```sql
INSERT INTO region_type_dict (type_code, type_name, level_range, description, region_examples, sort_order) VALUES
-- 省级 (level=1)
(1, '省', 1, '普通省份', '广东省、山东省', 1),
(2, '直辖市', 1, '直辖市', '北京市、上海市、天津市、重庆市', 2),
(3, '自治区', 1, '少数民族自治区', '内蒙古、广西、西藏、宁夏、新疆', 3),
(4, '特别行政区', 1, '特别行政区', '香港、澳门', 4),
-- 地级 (level=2)
(10, '地级市', 2, '地级行政单位', '广州市、深圳市', 10),
(11, '自治州', 2, '少数民族自治州', '延边朝鲜族自治州', 11),
(12, '盟', 2, '内蒙古特有地级单位', '锡林郭勒盟', 12),
(13, '地区', 2, '地区行政公署', '阿里地区', 13),
-- 县级 (level=3)
(20, '市辖区', 3, '市辖区', '海淀区、天河区', 20),
(21, '县', 3, '县', '从化县', 21),
(22, '县级市', 3, '县级市', '昆山市', 22),
(23, '自治县', 3, '少数民族自治县', '连南瑶族自治县', 23),
(24, '旗', 3, '内蒙古特有县级单位', '正蓝旗', 24),
(25, '自治旗', 3, '少数民族自治旗', '鄂伦春自治旗', 25),
(26, '林区', 3, '特殊县级单位', '神农架林区', 26),
(27, '特区', 3, '特殊县级单位', '六枝特区', 27),
-- 乡镇级 (level=4)
(30, '街道', 4, '街道办事处', '东华门街道', 30),
(31, '镇', 4, '镇', '虎门镇', 31),
(32, '乡', 4, '乡', '某某乡', 32),
(33, '民族乡', 4, '少数民族乡', '某某瑶族乡', 33),
(34, '苏木', 4, '内蒙古特有乡级单位', '某某苏木', 34),
(35, '民族苏木', 4, '少数民族苏木', '某某达斡尔族苏木', 35),
(36, '区公所', 4, '特殊乡级单位', '某某区公所', 36),
(37, '团', 4, '新疆兵团特有', '某某团', 37),
(38, '农场', 4, '新疆兵团特有', '某某农场', 38),
(39, '牧场', 4, '新疆兵团特有', '某某牧场', 39);
```

---

## 字段说明

### 主键

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | 自增主键，系统自动生成，不暴露业务含义 |

### 核心业务字段

| 字段 | 类型 | 约束 | 来源 | 说明 |
|------|------|------|------|------|
| code | VARCHAR(12) | NOT NULL | API | 12位行政区划代码，如 `110000000000`（北京市） |
| name | VARCHAR(100) | NOT NULL | API | 行政区划标准名称，如「北京市」「海淀区」 |

### 层级关系字段

| 字段 | 类型 | 约束 | 来源 | 说明 |
|------|------|------|------|------|
| level | TINYINT | NOT NULL | API | API 返回的原始级别。取值：`0`=根节点，`1`=省级，`2`=地级，`3`=县级，`4`=乡镇级 |
| depth | TINYINT | NOT NULL | 程序计算 | 相对于根节点的深度。用于 UI 级联展示，解决直辖市跳级问题。取值：`1`-`4` |
| parent_code | VARCHAR(12) | | 程序推算 | 父级行政区划代码。省级区划为 `NULL` |
| path | VARCHAR(200) | | 程序计算 | 从根到当前节点的完整路径，逗号分隔。如 `440000000000,440100000000,440103000000` |

> [!TIP]
> `level` 和 `depth` 的区别：直辖市下属区县 `level=3` 但 `depth=2`，便于 UI 展示为第二级。

### 分类字段

| 字段 | 类型 | 约束 | 来源 | 说明 |
|------|------|------|------|------|
| type | VARCHAR(20) | | API | 区划类型（中文），如「省」「直辖市」「市辖区」「街道」等，共 23 种 |
| type_code | TINYINT | | 程序映射 | 类型枚举编码，便于查询。编码规则见上方「行政区划类型」表 |

### 版本控制字段

| 字段 | 类型 | 约束 | 来源 | 说明 |
|------|------|------|------|------|
| year | SMALLINT | | API 参数 | 数据年份版本，如 `2024`。为空表示最新版本 |

### 状态管理字段

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| status | TINYINT | NOT NULL | 1 | 有效状态。`1`=有效，`0`=无效 |
| is_deleted | TINYINT | NOT NULL | 0 | 软删除标记。`0`=正常，`1`=已删除 |
| sort_order | INT | | 0 | 排序权重，值越小越靠前。默认按数据插入顺序 |

### 审计字段

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 记录最后更新时间 |

### 唯一约束

| 约束名 | 字段 | 说明 |
|--------|------|------|
| uk_code_year | (code, year) | 同一年份内 code 唯一 |

---

## 数据示例

| code | name | level | depth | type | parent_code | path |
|------|------|-------|-------|------|-------------|------|
| 110000000000 | 北京市 | 1 | 1 | 直辖市 | NULL | 110000000000 |
| 110101000000 | 东城区 | 3 | 2 | 市辖区 | 110000000000 | 110000000000,110101000000 |
| 110101001000 | 东华门街道 | 4 | 3 | 街道 | 110101000000 | 110000000000,110101000000,110101001000 |
| 440000000000 | 广东省 | 1 | 1 | 省 | NULL | 440000000000 |
| 440100000000 | 广州市 | 2 | 2 | 地级市 | 440000000000 | 440000000000,440100000000 |
| 440103000000 | 荔湾区 | 3 | 3 | 市辖区 | 440100000000 | 440000000000,440100000000,440103000000 |
| 440103001000 | 沙面街道 | 4 | 4 | 街道 | 440103000000 | 440000000000,440100000000,440103000000,440103001000 |

---

## 常用查询示例

### 查询所有省级行政区划

```sql
SELECT * FROM regions 
WHERE depth = 1 AND is_deleted = 0 
ORDER BY sort_order, code;
```

### 级联菜单：获取下一级（UI 推荐）

```sql
-- 根据父级 code 获取子级，自动适配直辖市/普通省份
SELECT * FROM regions 
WHERE parent_code = ? AND is_deleted = 0 
ORDER BY sort_order, code;
```

### 通过 path 快速查询所有上级

```sql
-- 查询某区划的所有上级（无需递归）
SELECT * FROM regions 
WHERE code IN ('440000000000', '440100000000', '440103000000')
ORDER BY depth;
```

### 模糊搜索

```sql
SELECT * FROM regions 
WHERE name LIKE '%天河%' AND is_deleted = 0;
```

---

## 扩展字段（第二阶段）

后续可根据需求添加以下字段：

| 字段 | 类型 | 来源 | 用途 |
|------|------|------|------|
| pinyin | VARCHAR(200) | pypinyin 生成 | 拼音搜索 |
| pinyin_short | VARCHAR(50) | pypinyin 生成 | 首字母搜索 |
| short_name | VARCHAR(50) | 外部数据 | 简称（京、沪） |
| longitude | DECIMAL(10,6) | 地图 API | 经度 |
| latitude | DECIMAL(10,6) | 地图 API | 纬度 |
