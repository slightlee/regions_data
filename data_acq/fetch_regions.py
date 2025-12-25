"""
行政区划数据爬取脚本
数据来源：民政部地名信息库 
"""

import requests
import json
import time
import os
from datetime import datetime


class RegionsFetcher:
    """行政区划数据获取"""
    
    BASE_URL = "换成实际接口地址"
    
    def __init__(self, year=None, max_level=2, output_dir="data"):
        """
        初始化
        
        Args:
            year: 数据年份，默认为最新年份
            max_level: 每次请求的最大深度 (0-2)
            output_dir: 输出目录
        """
        self.year = year
        self.max_level = max_level
        self.output_dir = output_dir
        self.all_regions = []  # 存储所有区划数据
        self.request_count = 0
        self.failed_requests = []
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
    
    def fetch(self, code=None, max_level=None):
        """
        调用 API 获取数据
        
        Args:
            code: 行政区划代码，为空则获取省级列表
            max_level: 最大查询深度
        
        Returns:
            API 返回的 data 字段
        """
        params = {
            "maxLevel": max_level if max_level is not None else self.max_level
        }
        if self.year:
            params["year"] = self.year
        if code:
            params["code"] = code
        
        try:
            self.request_count += 1
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == 200:
                return result.get("data")
            else:
                print(f"API 返回错误: {result}")
                return None
                
        except Exception as e:
            print(f"请求失败 [code={code}]: {e}")
            self.failed_requests.append({"code": code, "error": str(e)})
            return None
    
    def process_region(self, region, parent_code=None, depth=1):
        """
        处理单个区划数据，提取并扁平化
        
        Args:
            region: API 返回的区划数据
            parent_code: 父级代码
            depth: 当前深度
        
        Returns:
            处理后的区划记录
        """
        if not region or not region.get("code"):
            return None
        
        record = {
            "code": region.get("code"),
            "name": region.get("name"),
            "level": region.get("level"),
            "depth": depth,
            "type": region.get("type"),
            "parent_code": parent_code
        }
        
        return record
    
    def crawl_all(self):
        """
        获取全量数据
        """
        print(f"开始获取行政区划数据...")
        print(f"年份: {self.year or '最新'}")
        print("-" * 50)
        
        start_time = time.time()
        
        # 第一步：获取所有省份
        print("Step 1: 获取省级数据...")
        provinces_data = self.fetch(max_level=1)
        
        if not provinces_data or not provinces_data.get("children"):
            print("获取省级数据失败！")
            return
        
        provinces = provinces_data.get("children", [])
        print(f"共 {len(provinces)} 个省级单位")
        
        # 遍历每个省份
        for i, province in enumerate(provinces, 1):
            province_code = province.get("code")
            province_name = province.get("name")
            print(f"\n[{i}/{len(provinces)}] {province_name} ({province_code})")
            
            # 保存省级记录
            province_record = self.process_region(province, parent_code=None, depth=1)
            if province_record:
                self.all_regions.append(province_record)
            
            # 获取该省的下级数据 (地级市/区县)
            province_detail = self.fetch(code=province_code, max_level=2)
            time.sleep(0.3)  # 请求间隔，避免被限流
            
            if not province_detail:
                continue
            
            children_level2 = province_detail.get("children", [])
            
            for child2 in children_level2:
                child2_code = child2.get("code")
                child2_level = child2.get("level")
                
                # 直辖市的子级是 level=3（区县），普通省份的子级是 level=2（地级市）
                is_municipality_district = (child2_level == 3)  # 直辖市下属区县
                child2_depth = 2  # 无论是地级市还是直辖市区县，都是第2层
                
                child2_record = self.process_region(child2, parent_code=province_code, depth=child2_depth)
                if child2_record:
                    self.all_regions.append(child2_record)
                
                # === 直辖市特殊处理 ===
                # 直辖市的 child2 已经是区县（level=3），需要直接获取其乡镇
                if is_municipality_district:
                    # 获取直辖市区县的乡镇数据
                    district_detail = self.fetch(code=child2_code, max_level=1)
                    time.sleep(0.2)
                    
                    if district_detail:
                        children_level4 = district_detail.get("children", [])
                        for child4 in children_level4:
                            child4_record = self.process_region(child4, parent_code=child2_code, depth=3)
                            if child4_record:
                                self.all_regions.append(child4_record)
                    continue  # 直辖市处理完毕，跳到下一个 child2
                
                # === 普通省份处理 ===
                # 处理第三级 (区县)
                children_level3 = child2.get("children", [])
                for child3 in children_level3:
                    child3_depth = child2_depth + 1
                    child3_record = self.process_region(child3, parent_code=child2_code, depth=child3_depth)
                    if child3_record:
                        self.all_regions.append(child3_record)
                    
                    # 获取乡镇级数据
                    child3_code = child3.get("code")
                    child3_detail = self.fetch(code=child3_code, max_level=1)
                    time.sleep(0.2)
                    
                    if child3_detail:
                        children_level4 = child3_detail.get("children", [])
                        for child4 in children_level4:
                            child4_record = self.process_region(child4, parent_code=child3_code, depth=child3_depth + 1)
                            if child4_record:
                                self.all_regions.append(child4_record)
            
            # 每处理完一个省份保存一次进度
            if i % 5 == 0:
                self._save_progress()
        
        elapsed = time.time() - start_time
        print(f"\n{'=' * 50}")
        print(f"获取完成！")
        print(f"总记录数: {len(self.all_regions)}")
        print(f"请求次数: {self.request_count}")
        print(f"失败请求: {len(self.failed_requests)}")
        print(f"耗时: {elapsed:.2f} 秒")
        
        # 保存最终结果
        self._save_final()
        
        return self.all_regions
    
    def _save_progress(self):
        """保存进度"""
        filepath = os.path.join(self.output_dir, "regions_progress.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.all_regions, f, ensure_ascii=False, indent=2)
        print(f"  [进度已保存: {len(self.all_regions)} 条]")
    
    def _save_final(self):
        """保存最终结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        year_suffix = f"_{self.year}" if self.year else ""
        
        # 保存完整数据
        filepath = os.path.join(self.output_dir, f"regions{year_suffix}_{timestamp}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "meta": {
                    "year": self.year,
                    "total": len(self.all_regions),
                    "request_count": self.request_count,
                    "failed_count": len(self.failed_requests),
                    "crawl_time": timestamp
                },
                "data": self.all_regions
            }, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到: {filepath}")
        
        # 保存失败记录
        if self.failed_requests:
            fail_path = os.path.join(self.output_dir, f"failed_requests_{timestamp}.json")
            with open(fail_path, 'w', encoding='utf-8') as f:
                json.dump(self.failed_requests, f, ensure_ascii=False, indent=2)
            print(f"失败记录已保存到: {fail_path}")
        
        # 统计 type 分布
        self._analyze_types()
    
    def _analyze_types(self):
        """分析 type 字段分布"""
        type_stats = {}
        for region in self.all_regions:
            t = region.get("type", "未知")
            level = region.get("level", -1)
            key = f"{t} (level={level})"
            type_stats[key] = type_stats.get(key, 0) + 1
        
        print(f"\n{'=' * 50}")
        print("type 字段统计:")
        for k, v in sorted(type_stats.items(), key=lambda x: -x[1]):
            print(f"  {k}: {v}")
        
        # 保存统计结果
        stats_path = os.path.join(self.output_dir, "type_statistics.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(type_stats, f, ensure_ascii=False, indent=2)
        print(f"统计结果已保存到: {stats_path}")


def main():
    """主函数"""
    fetcher = RegionsFetcher(
        year=None,  # 使用最新年份
        max_level=2,
        output_dir="data"
    )
    fetcher.crawl_all()


if __name__ == "__main__":
    main()
