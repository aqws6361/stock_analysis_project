import pandas as pd
from finmind.data import DataLoader
from datetime import datetime, timedelta

# ----------------------------------------------------------------------
# 1. 設定您的 API Token
# ----------------------------------------------------------------------
api_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNS0xMS0wOCAwOTowODozMiIsInVzZXJfaWQiOiJhZGFtaHUiLCJpcCI6IjYxLjIyMy42My4zNCJ9.FLedzCZOXMomGv0oBr6VZ86BwIMDRWnxAQuQLq9KEmE"

if api_token == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRlIjoiMjAyNS0xMS0wOCAwOTowODozMiIsInVzZXJfaWQiOiJhZGFtaHUiLCJpcCI6IjYxLjIyMy42My4zNCJ9.FLedzCZOXMomGv0oBr6VZ86BwIMDRWnxAQuQLq9KEmE":
    print("錯誤：請先設定您的 FinMind API Token！")

dl = DataLoader()
dl.login_by_token(api_token)

print("FinMind 登入成功，開始抓取數據...")

# ----------------------------------------------------------------------
# 2. 抓取所需數據 (批次處理)
# ----------------------------------------------------------------------

# --- A. 取得估值數據 (P/E, P/B) ---
# 我們抓取一個最近的交易日數據 (例如昨天)
# FinMind 的數據可能會有 1-2 天的延遲，所以我們抓 3 天前的數據比較保險
try:
    target_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')

    print(f"抓取 {target_date} 的估值數據...")

    # 抓取當天的本益比 (P/E)
    df_per = dl.taiwan_stock_per(date=target_date)
    # 篩選我們需要的欄位
    df_per = df_per[['stock_id', 'PER']]

    # 抓取當天的股價淨值比 (P/B)
    df_pbr = dl.taiwan_stock_pbr(date=target_date)
    # 篩選我們需要的欄位
    df_pbr = df_pbr[['stock_id', 'PBR']]

    # --- B. 取得財務報表數據 (ROE, 負債權益比) ---
    # 財報是季度資料，我們抓取最近一季的數據
    # 假設現在是 2025-11-06，我們抓取 2025 年 Q2 或 Q3 的財報
    # 這裡我們抓取 '2025-Q2' 作為範例
    print("抓取 2025-Q2 的財務報表數據...")
    df_finance = dl.taiwan_stock_financial_statement(
        start_date='2025-06-01',  # FinMind 會自動抓取該季度的數據
        end_date='2025-06-30'
    )

    # 篩選我們需要的關鍵欄位
    # 'ROE_A' = 股東權益報酬率 (單季)
    # 'DebtEquityRatio' = 負債權益比 (注意：FinMind 單位是 %)
    finance_cols = ['stock_id', 'ROE_A', 'DebtEquityRatio']

    # 檢查欄位是否存在
    if all(col in df_finance.columns for col in finance_cols):
        df_finance_filtered = df_finance[finance_cols].copy()
    else:
        print("錯誤：財務報表欄位不齊全。")
        # 處理可能的欄位名稱變動或缺失
        # ...
        df_finance_filtered = pd.DataFrame(columns=finance_cols)  # 建立空表

    # ----------------------------------------------------------------------
    # 3. 合併所有數據
    # ----------------------------------------------------------------------
    print("開始合併數據...")

    # 基礎：合併 P/E 和 P/B
    df_merged = pd.merge(df_per, df_pbr, on='stock_id', how='inner')

    # 再合併財務數據
    df_final = pd.merge(df_merged, df_finance_filtered, on='stock_id', how='inner')

    # 數據清洗：移除空值 (NaN)
    df_final = df_final.dropna()

    # ----------------------------------------------------------------------
    # 4. 套用我們的「巴菲特濾網」
    # ----------------------------------------------------------------------
    print("開始篩選股票...")

    # 條件 1：價值低估
    filter_pe = df_final['PER'] < 15
    filter_pb = df_final['PBR'] < 1.5

    # 條件 2：獲利能力
    # FinMind 的 ROE_A 是單季，巴菲特通常看全年 (TTM)。
    # 為了簡化範例，我們假設單季 ROE > 4% (換算成年化約 > 16%)
    filter_roe = df_final['ROE_A'] > 4.0

    # 條件 3：財務健康
    # FinMind 的 DebtEquityRatio 是 負債/權益 (單位%)
    # 我們設定 < 100% (即 負債 < 權益)，巴菲特偏好更低，例如 < 50%
    filter_de_ratio = df_final['DebtEquityRatio'] < 50.0

    # 套用所有濾網
    df_result = df_final[
        filter_pe &
        filter_pb &
        filter_roe &
        filter_de_ratio
        ]

    # ----------------------------------------------------------------------
    # 5. 顯示結果
    # ----------------------------------------------------------------------
    print("\n========== 價值投資篩選結果 ==========")
    if df_result.empty:
        print("找不到符合所有條件的股票。")
        print("您可以試著放寬篩選條件 (例如 P/E < 20 或 P/B < 2)。")
    else:
        # 為了方便閱讀，我們重新命名一下欄位
        df_result = df_result.rename(columns={
            'stock_id': '股票代碼',
            'PER': '本益比 (P/E)',
            'PBR': '股價淨值比 (P/B)',
            'ROE_A': '單季 ROE (%)',
            'DebtEquityRatio': '負債權益比 (%)'
        })
        print(df_result.to_string(index=False))

except Exception as e:
    print(f"發生錯誤: {e}")
    print("請檢查：")
    print("1. 您的 FinMind API Token 是否正確？")
    print("2. 您的網路連線是否正常？")
    print("3. 是否達到了 API 的請求上限？")