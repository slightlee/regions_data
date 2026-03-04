"""
行政区划数据脚本（新版 API）
使用新的 POST 接口获取数据
数据来源：国家地名信息库
"""

import requests
import json
import time
import os
from datetime import datetime
import urllib3

from pathlib import Path

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NewRegionsFetcher:
    """新版行政区划数据获取器"""
    
    GET_LIST_URL = "https://dmfw.mca.gov.cn/xzqh/getList"
    GET_CODE_LIST_URL = "https://dmfw.mca.gov.cn/xzqh/getCodeList"
    
    def __init__(self, table_name="Xzqh20251231", output_dir="data/raw"):
        """
        初始化
        
        Args:
            table_name: 表名，格式为 Xzqh + 日期
            output_dir: 输出目录
        """
        self.table_name = table_name
        self.output_dir = output_dir
        self.all_regions = []  # 存储所有区划数据
        self.seen_codes = set()  # 用于去重
        self.start_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.request_count = 0
        self.failed_requests = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 尝试加载进度
        self._load_progress()
        
        # 配置 session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://dmfw.mca.gov.cn',
            'Referer': 'https://dmfw.mca.gov.cn/XzqhVersionPublish.html',
        })

    def _load_progress(self):
        """扫描并加载最新的临时进度文件"""
        output_path = Path(self.output_dir)
        tmp_files = sorted(output_path.glob("regions_*_tmp.json"), reverse=True)
        
        if not tmp_files:
            return

        latest_tmp = tmp_files[0]
        print(f"🔍 发现临时进度文件: {latest_tmp.name}")
        try:
            with open(latest_tmp, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
                data = progress_data.get("data", [])
                if data:
                    self.all_regions = data
                    self.seen_codes = {r["code"] for r in data}
                    self.start_timestamp = progress_data.get("meta", {}).get("crawl_time", self.start_timestamp)
                    print(f"✅ 已恢复 {len(self.all_regions)} 条记录，将继续采集...")
        except Exception as e:
            print(f"⚠️  加载进度文件失败: {e}，将重新开始采集。")
    
    def fetch_provinces(self, show_progress=False, retry_count=3):
        """
        获取省级数据（使用 getList 接口）
        
        Returns:
            省级数据列表
        """
        params = {
            'trimCode': 'true',
            'maxLevel': '1'
        }
        
        for attempt in range(retry_count):
            try:
                self.request_count += 1
                if show_progress:
                    retry_info = f" (重试 {attempt + 1}/{retry_count})" if attempt > 0 else ""
                    print(f"    [请求 #{self.request_count}] 获取省级数据{retry_info}...", end=" ", flush=True)
                
                response = self.session.get(self.GET_LIST_URL, params=params, timeout=30, verify=False)
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == 200:
                    data = result.get("data", {})
                    children = data.get("children", [])
                    
                    if show_progress:
                        print(f"✅ 获取 {len(children)} 个省级单位")
                    
                    return children
                else:
                    if show_progress:
                        print(f"❌ 错误: {result.get('message', 'Unknown')}")
                    
                    if attempt < retry_count - 1:
                        time.sleep(3)
                        continue
                    
                    return []
                    
            except Exception as e:
                if show_progress:
                    print(f"❌ 异常: {str(e)[:50]}")
                
                if attempt < retry_count - 1:
                    time.sleep(3)
                    continue
                
                return []
        
        return []
    
    def fetch_data(self, parent_code, region_type, show_progress=False, retry_count=3):
        """
        获取数据（使用 getCodeList 接口）
        
        Args:
            parent_code: 父级代码（完整的 code，如 110000000000）
            region_type: 类型（2=地级，3=县级，4=乡级）
            show_progress: 是否显示进度
            retry_count: 重试次数
        
        Returns:
            数据列表
        """
        # 设置 Content-Type 为 form-urlencoded
        headers = self.session.headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        data = {
            'parentCode': parent_code,
            'placeCode': '',
            'title': '',
            'tableName': self.table_name,
            'type': region_type,
            'pageNum': '1',
            'pageSize': '1000'  # 设置足够大，一次获取所有数据
        }
        
        for attempt in range(retry_count):
            try:
                self.request_count += 1
                if show_progress:
                    retry_info = f" (重试 {attempt + 1}/{retry_count})" if attempt > 0 else ""
                    print(f"    [请求 #{self.request_count}] parentCode={parent_code}, type={region_type}{retry_info}...", end=" ", flush=True)
                
                response = self.session.post(self.GET_CODE_LIST_URL, data=data, headers=headers, timeout=30, verify=False)
                response.raise_for_status()
                result = response.json()
                
                # 检查是否限流
                if result.get("status") == 2 and "频繁" in result.get("message", ""):
                    wait_time = 10 * (attempt + 1)  # 增加等待时间：10秒、20秒、30秒
                    if show_progress:
                        print(f"⚠️  限流，等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                
                if result.get("status") == 200:
                    data_list = result.get("data", [])
                    
                    # 检查数据是否异常
                    if data_list is None:
                        if show_progress:
                            print(f"⚠️  返回数据为空，等待后重试...")
                        time.sleep(5)
                        if attempt < retry_count - 1:
                            continue
                        return []
                    
                    if show_progress:
                        print(f"✅ 获取 {len(data_list)} 条")
                    
                    return data_list
                else:
                    if show_progress:
                        print(f"❌ 错误: {result.get('message', 'Unknown')}")
                    
                    if attempt < retry_count - 1:
                        time.sleep(3)
                        continue
                    
                    self.failed_requests.append({
                        "parent_code": parent_code,
                        "type": region_type,
                        "error": result.get("message", "Unknown error")
                    })
                    return []
                    
            except Exception as e:
                if show_progress:
                    print(f"❌ 异常: {str(e)[:50]}")
                
                if attempt < retry_count - 1:
                    time.sleep(3)
                    continue
                
                self.failed_requests.append({
                    "parent_code": parent_code,
                    "type": region_type,
                    "error": str(e)
                })
                return []
        
        return []
    
    def fetch_children(self, parent_code, region_type, show_progress=False):
        """
        获取子级数据
        
        Args:
            parent_code: 父级完整代码
            region_type: 类型
            show_progress: 是否显示进度
        
        Returns:
            子级数据列表（已过滤掉第一条父级数据）
        """
        data = self.fetch_data(parent_code, region_type, show_progress)
        
        if not data:
            return []
        
        # API Bug: 当使用短代码（省级简码，如 11、13）作为 parentCode 时，
        # 返回的第一条数据是父级本身，需要跳过
        # 判断依据：第一条数据的 parentCode 为 "0" 或 "000000000000" 表示顶级
        first_item = data[0]
        first_parent_code = first_item.get("parentCode", "")
        
        if first_parent_code in ["0", "000000000000"]:
            return data[1:]  # 跳过第一条父级数据
        
        return data
    
    def _add_regions(self, regions, parent_code):
        """
        批量添加区划数据到 all_regions，并进行去重
        
        Args:
            regions: 区划数据列表
            parent_code: 父级代码
        """
        added_count = 0
        for region in regions:
            code = region.get("code")
            if not code:
                continue

            # 检查 code 是否已存在
            if code not in self.seen_codes:
                self.all_regions.append({
                    "code": code,
                    "name": region.get("name"),
                    "level": region.get("level"),
                    "type": region.get("type"),
                    "parent_code": parent_code,
                    "year": region.get("year"),
                    "name_path": region.get("namePath", "")
                })
                self.seen_codes.add(code)
                added_count += 1
        return added_count
    
    def crawl_all(self):
        """
        获取全量数据
        """
        print("=" * 80)
        print("开始获取行政区划数据（新版 API）")
        print(f"表名: {self.table_name}")
        print("=" * 80)
        
        start_time = time.time()
        
        # 第一步：获取所有省级数据（使用 getList 接口）
        print("\n[1/4] 获取省级数据...")
        print("-" * 80)
        provinces = self.fetch_provinces(show_progress=True)
        print(f"\n  ✅ 获取 {len(provinces)} 个省级单位")
        
        for province in provinces:
            self._add_regions([province], parent_code=None)
        
        # 第二步：获取所有地级数据（使用 getCodeList 接口）
        print("\n[2/4] 获取地级数据...")
        print("-" * 80)
        city_count = 0
        
        # 建立已处理父级映射，用于断点续传
        processed_parents = {r['parent_code'] for r in self.all_regions if r['parent_code']}
        
        for i, province in enumerate(provinces, 1):
            province_code = province.get("code", "")
            province_name = province.get("name", "")
            
            # 断点续传检查
            if province_code in processed_parents:
                # 统计已有的数量
                existing_count = sum(1 for r in self.all_regions if r['parent_code'] == province_code)
                print(f"  [{i:2d}/{len(provinces)}] {province_name:<12} (code={province_code}) ⏭️  已存在 {existing_count} 条，跳过")
                city_count += existing_count
                continue

            print(f"  [{i:2d}/{len(provinces)}] {province_name:<12} (code={province_code})")
            
            cities = self.fetch_children(parent_code=province_code, region_type="2", show_progress=True)
            
            if cities:
                added_count = self._add_regions(cities, province_code)
                city_count += added_count
            
            time.sleep(1.0)  # 增加省级请求间隔，避免限流
            
            # 每 5 个省保存一次临时结果
            if i % 5 == 0:
                self._save_final(is_tmp=True)
        
        print(f"\n  ✅ 共获取 {city_count} 个地级单位")
        self._save_final(is_tmp=True)
        
        # 第三步：获取所有县级数据
        print("\n[3/4] 获取县级数据...")
        print("-" * 80)
        county_count = 0
        
        # 获取所有省级和地级单位作为父级
        parents = [r for r in self.all_regions if r["level"] in [1, 2]]
        
        # 更新已处理父级映射
        processed_parents = {r['parent_code'] for r in self.all_regions if r['parent_code']}
        
        print(f"  需要处理 {len(parents)} 个父级单位（省级+地级）")
        
        for i, parent in enumerate(parents, 1):
            parent_code = parent.get("code", "")
            parent_name = parent.get("name", "")
            parent_level = parent.get("level")
            
            # 断点续传检查
            if parent_code in processed_parents and parent_level < 3:
                # 如果这个父级下已经有三级数据了，跳过
                existing_count = sum(1 for r in self.all_regions if r['parent_code'] == parent_code and r['level'] == 3)
                if existing_count > 0:
                    print(f"  [{i:3d}/{len(parents)}] {parent_name:<15} (code={parent_code}) ⏭️  已存在 {existing_count} 条，跳过")
                    county_count += existing_count
                    continue

            print(f"  [{i:3d}/{len(parents)}] {parent_name:<15} (level={parent_level}, code={parent_code})")
            
            counties = self.fetch_children(parent_code=parent_code, region_type="3", show_progress=True)
            
            if counties:
                added_count = self._add_regions(counties, parent_code)
                county_count += added_count
            
            time.sleep(0.8)  # 增加请求间隔，避免限流
            
            # 每 20 个父级保存一次临时结果
            if i % 20 == 0:
                self._save_final(is_tmp=True)
        
        print(f"\n  ✅ 共获取 {county_count} 个县级单位")
        self._save_final(is_tmp=True)
        
        # 第四步：获取所有乡级数据
        print("\n[4/4] 获取乡级数据...")
        print("-" * 80)
        town_count = 0
        counties = [r for r in self.all_regions if r["level"] == 3]
        
        # 更新已处理父级映射
        processed_parents = {r['parent_code'] for r in self.all_regions if r['parent_code']}
        
        print(f"  需要处理 {len(counties)} 个县级单位")
        
        for i, county in enumerate(counties, 1):
            county_code = county.get("code", "")
            county_name = county.get("name", "")
            
            # 断点续传检查
            if county_code in processed_parents:
                existing_count = sum(1 for r in self.all_regions if r['parent_code'] == county_code)
                print(f"  [{i:4d}/{len(counties)}] {county_name:<20} (code={county_code}) ⏭️  已存在 {existing_count} 条，跳过")
                town_count += existing_count
                continue

            print(f"  [{i:4d}/{len(counties)}] {county_name:<20} (code={county_code})")
            
            towns = self.fetch_children(parent_code=county_code, region_type="4", show_progress=True)
            
            if towns:
                added_count = self._add_regions(towns, county_code)
                town_count += added_count
            
            time.sleep(0.7)  # 增加请求间隔，避免限流
            
            # 每 50 个县保存一次临时结果
            if i % 50 == 0:
                self._save_final(is_tmp=True)
        
        print(f"\n  ✅ 共获取 {town_count} 个乡级单位")
        
        elapsed = time.time() - start_time
        
        print(f"\n{'=' * 80}")
        print(f"获取完成！")
        print(f"总记录数: {len(self.all_regions):,}")
        print(f"请求次数: {self.request_count}")
        print(f"失败请求: {len(self.failed_requests)}")
        print(f"耗时: {elapsed:.2f} 秒 ({elapsed/60:.1f} 分钟)")
        print(f"{'=' * 80}")
        
        # 保存结果
        self._save_final()
        
        # 统计分析
        self._analyze_data()
        
        return self.all_regions
    
    def _save_final(self, is_tmp=False):
        """保存最终结果"""
        timestamp = self.start_timestamp
        suffix = "_tmp" if is_tmp else ""
        
        # 保存完整数据
        filename = f"regions_{timestamp}{suffix}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "meta": {
                    "table_name": self.table_name,
                    "total": len(self.all_regions),
                    "request_count": self.request_count,
                    "failed_count": len(self.failed_requests),
                    "crawl_time": timestamp,
                    "method": "new_post_api",
                    "is_partial": is_tmp
                },
                "data": self.all_regions
            }, f, ensure_ascii=False, indent=2)
        
        if not is_tmp:
            print(f"\n✅ 数据已保存到: {filepath}")
            # 如果存在临时文件，在最终保存后删除
            tmp_path = os.path.join(self.output_dir, f"regions_{timestamp}_tmp.json")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        else:
            # 临时保存不打印太多日志，只在重要节点提示
            pass
        
        # 保存失败记录
        if self.failed_requests:
            fail_path = os.path.join(self.output_dir, f"failed_requests_{timestamp}.json")
            with open(fail_path, 'w', encoding='utf-8') as f:
                json.dump(self.failed_requests, f, ensure_ascii=False, indent=2)
            print(f"⚠️  失败记录已保存到: {fail_path}")
    
    def _analyze_data(self):
        """分析数据统计"""
        print(f"\n{'=' * 80}")
        print("数据统计分析")
        print(f"{'=' * 80}")
        
        # 按 level 统计
        level_stats = {}
        for region in self.all_regions:
            level = region.get("level", -1)
            level_stats[level] = level_stats.get(level, 0) + 1
        
        level_names = {
            1: "省级",
            2: "地级",
            3: "县级",
            4: "乡级"
        }
        
        print("\n按行政级别统计:")
        for level in sorted(level_stats.keys()):
            count = level_stats[level]
            level_name = level_names.get(level, f"level={level}")
            print(f"  {level_name}: {count:,} 个")
        
        # 按 type 统计
        type_stats = {}
        for region in self.all_regions:
            t = region.get("type")
            if t:
                type_stats[t] = type_stats.get(t, 0) + 1
        
        print("\n按区划类型统计 (Top 10):")
        sorted_types = sorted(type_stats.items(), key=lambda x: -x[1])[:10]
        for t, count in sorted_types:
            print(f"  {t}: {count:,} 个")


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     行政区划数据获取工具（新版 API）                            ║
║                                                                              ║
║  特点：                                                                       ║
║  • 使用官方最新的 POST 接口                                                  ║
║  • 包含 namePath 等额外信息                                                    ║
║                                                                              ║
║  数据来源：国家地名信息库 (https://dmfw.mca.gov.cn)                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    fetcher = NewRegionsFetcher(
        table_name="Xzqh20251231",  # 2025年12月31日的数据
        output_dir="data"
    )
    
    fetcher.crawl_all()
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              获取完成！                                        ║
║                                                                              ║
║  下一步：                                                                     ║
║  1. 运行 python scripts/clean_regions_data.py 清洗数据                         ║
║  2. 运行 python scripts/import_regions.py 导入数据库                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
