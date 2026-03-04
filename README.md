# 行政区划数据

[![GitHub stars](https://img.shields.io/github/stars/slightlee/regions_data?style=flat-square)](https://github.com/slightlee/regions_data/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/slightlee/regions_data?style=flat-square)](https://github.com/slightlee/regions_data/network/members)
[![GitHub license](https://img.shields.io/github/license/slightlee/regions_data?style=flat-square)](https://github.com/slightlee/regions_data/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/slightlee/regions_data/pulls)
[![Data Update](https://img.shields.io/badge/数据更新-2025--12--24-blue?style=flat-square)](https://dmfw.mca.gov.cn)

> 🗺️ 行政区划数据，包括省级、地级、县级、乡级四级行政区划数据。

## ✨ 特性

- 📊 **数据完整** - 覆盖全国 34 个省级、333 个地级、2,845 个县级、38,723 个乡级行政区划
- 🔄 **数据权威** - 数据来源于国家地名信息库，定期同步更新
- 🚀 **即开即用** - 提供 SQLite 数据库和 JSON 原始数据，支持多种使用场景
- 🌐 **在线预览** - 提供可搜索的级联选择器在线演示

## 📈 数据统计

| 级别 | 数量 | 示例 |
|------|------|------|
| 省级 | 34 | 北京市、广东省、香港特别行政区 |
| 地级 | 333 | 深圳市、杭州市、成都市 |
| 县级 | 2,845 | 南山区、西湖区、武侯区 |
| 乡级 | 38,723 | 南山街道、西溪街道、玉林街道 |
| **总计** | **42,935** | - |

## 数据来源

> [国家地名信息库](https://dmfw.mca.gov.cn)
>
> **第十六条** 国务院民政部门应当在每年1月通过**国家地名信息库**发布截至上一年度末全国各级行政区划建制的行政区划代码信息。
>
> 省、自治区、直辖市人民政府民政部门应当在每年1月和7月通过民政部门网站发布截至上个月末本地区乡级行政区划建制的行政区划代码信息。来源：[《行政区划代码》国家标准](https://www.mca.gov.cn/gdnps/pc/content.jsp?mtype=1&id=1662004999980005812)

## 数据说明

项目采用分层数据管理方式：

| 目录 | 说明 | 建议用途 | 命名规范 |
|------|------|------|------|
| `data/raw/` | 原始 JSON 数据 | 存放直接从接口获取的原始数据 | `regions_{timestamp}.json` |
| `data/processed/` | 清洗后的 JSON 数据 | 存放经过格式化、代码补全后的数据 | **与 raw 文件名保持一致** |
| `data/regions.db` | SQLite 数据库 | 最终产出的数据库文件，生产环境直接使用 | - |
| `data/archive/` | 历史归档数据 | 存放旧版本的备份数据 | - |

## 数据更新流程

1. **获取数据**: 运行 `python scripts/fetch_regions.py`，数据将保存至 `data/raw/`。
2. **清洗数据**: 运行 `python scripts/clean_regions_data.py`，它会自动读取 `data/raw/` 中最新的文件，并将处理结果保存至 `data/processed/`。
3. **导入数据库**: 运行 `python scripts/import_regions.py`，它会自动读取 `data/processed/` 中最新的文件，并更新 `data/regions.db`。

## 分支说明

| 分支 | 说明 |
|------|------|
| `main` | 当前版本，四级行政区划（省/地/县/乡镇） |
| `main-legacy` | 旧版本，五级行政区划（含村级），数据来源于国家统计局 |

## 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m uvicorn api.index:app --host 127.0.0.1 --port 8000 --reload

# 访问
http://127.0.0.1:8000/
```

## 在线预览

> 访问: https://regions-data.vercel.app/

### 预览效果

![效果图](./images/area.gif)

## 📜 更新日志

详见 [Releases](https://github.com/slightlee/regions_data/releases) 页面。

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.3 | 2026-3-4 | 同步国家地名信息库行政区划代码数据【官方数据截止日期为2025年12月31日】 |
| v1.0.2 | 2025-12-24 | 重构项目，数据来源切换至国家地名信息库，调整为四级行政区划 |
| v1.0.1 | - | 旧版本，五级行政区划（含村级），数据来源于国家统计局 |

## 📄 许可证

本项目采用 [MIT License](./LICENSE) 开源许可证。

## 🙏 致谢

- 数据来源：[国家地名信息库](https://dmfw.mca.gov.cn)
- 感谢所有贡献者的支持

## 📮 反馈与贡献

- 🐛 发现问题？请提交 [Issue](https://github.com/slightlee/regions_data/issues)
- 💡 有好想法？欢迎提交 [Pull Request](https://github.com/slightlee/regions_data/pulls)
- ⭐ 觉得有用？请给项目一个 Star 支持一下！

## ⭐ Star History

<a href="https://star-history.com/#slightlee/regions_data&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=slightlee/regions_data&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=slightlee/regions_data&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=slightlee/regions_data&type=Date" />
 </picture>
</a>
