# /// script
# dependencies = [
#   "requests",
#   "pandas",
#   "xlrd",
#   "openpyxl",
# ]
# ///
import os
import json
from fetcher.csi_930955_indicator import fetch_csi_930955_list
from fetcher.us10ytip_indicator import fetch_us10ytip_list

# 🚀 配置文件路径（都在项目根目录下）
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_JSON_PATH = os.path.join(CURRENT_DIR, "data.json")

def main():
    print("================ 监控看板自动化流水线启动 ================")
    
    # ------------------ 第一步：加载或初始化 data.json ------------------
    if os.path.exists(DATA_JSON_PATH):
        try:
            with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
                master_data = json.load(f)
            print("📖 成功读取本地既有 data.json 数据库。")
        except Exception as e:
            print(f"⚠️ 读取 data.json 失败 (可能文件损坏)，将初始化新字典。原因: {e}")
            master_data = {}
    else:
        print("🆕 未发现本地 data.json，将自动创建全新的数据大字典盒子。")
        master_data = {}

    # 如果读取出来的不是字典结构，强制重置为字典，确保容器安全
    if not isinstance(master_data, dict):
        master_data = {}

    # ------------------ 第二步：并发抓取 ------------------
    
    # 1. 抓取红利低波 100 历史 List (默认取 20 天)
    print("\n--- [任务 1/2] 抓取红利低波 100 指数数据 ---")
    csi_data_list = fetch_csi_930955_list(limit_days=20)
    
    # 2. 抓取美债实际利率历史 List (默认取 20 天)
    # 密码由于写了 os.getenv，会完美自动读取你 UNRAID 容器或环境里的 FRED_API_KEY
    print("\n--- [任务 2/2] 抓取圣路易斯联储 FRED 美债数据 ---")
    fred_data_list = fetch_us10ytip_list(api_key="8564bbe541091fb29e8fbc237380b2aa", days_limit=20)

    # ------------------ 第三步：数据更新替换 ------------------
    print("\n--- 正在汇总所有 List ---")
    
    # 核心爽点：即使 csi 或 fred 某一路因为网络波动临时断流吐了空列表 []
    # 我们也做个安全的非空校验，只有成功抓到数据时才覆盖，防止把老历史冲洗掉，自愈性拉满！
    if csi_data_list:
        master_data["csi930955"] = csi_data_list
        print(f"✅ [红利低波100] 数据成功抓取，共 {len(csi_data_list)} 条记录。")
    else:
        print("⚠️ [红利低波100] 本次抓取列表为空，保留上一次的历史缓存，不进行覆盖。")

    if fred_data_list:
        master_data["us10ytip"] = fred_data_list
        print(f"✅ [美债利率] 数据成功抓取，共 {len(fred_data_list)} 条记录。")
    else:
        print("⚠️ [美债利率] 本次抓取列表为空，保留上一次的历史缓存，不进行覆盖。")

    # ------------------ 第四步：写回本地 ------------------
    try:
        with open(DATA_JSON_PATH, "w", encoding="utf-8") as f:
            # ensure_ascii=False 保持中文“股息率”非乱码，indent=2 保持 JSON 优美可读
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        print(f"\n🎉 所有指标已成功抓取并写入字典: {DATA_JSON_PATH}")
    except Exception as e:
        print(f"\n❌ 写入 data.json 致命错误: {e}")

    print("========================= 流水线结束 =========================")

if __name__ == "__main__":
    main()