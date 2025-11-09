import pandas as pd
from FinMind.data import FinMindApi
import yfinance as yf
import sys
import config  # 讀取 API 金鑰

# 初始化 FinMind API (只用它來獲取股票清單)
api = FinMindApi()

# 檢查 config 中是否有 token
if not config.FINMIND_API_TOKEN:
    print("[錯誤] 找不到 FinMind API 金鑰，請檢查您的 .env 檔案是否已設定 FINMIND_API_TOKEN。", file=sys.stderr)
    sys.exit(1)  # 終止程式

api.login_by_token(api_token=config.FINMIND_API_TOKEN)


def get_all_stock_list() -> pd.DataFrame:
    """
    使用 FinMind (唯一可用的 API) 獲取所有台股清單 (上市 + 上櫃)。
    """
    print("--- 1. 正在從 FinMind 獲取所有台股清單 (TaiwanStockInfo) ---")
    try:
        df_twse = api.get_data(dataset="TaiwanStockInfo", data_id="")
        if df_twse is None or df_twse.empty:
            print("  [錯誤] 無法從 FinMind 獲取股票清單。", file=sys.stderr)
            return pd.DataFrame()

        # 篩選出 '上市' (TWSE) 和 '上櫃' (OTC)
        twse_stocks = df_twse[
            (df_twse['industry_category'] != 'None') &
            (df_twse['stock_id'] != '') &
            (df_twse['type'].isin(['twse', 'tpex'])) &  # twse=上市, tpex=上櫃
            (df_twse['stock_id'].str.len() == 4)  # <-- [優化] 只保留 4 位數的股票代號 (過濾權證)
            ].drop_duplicates(subset=['stock_id']).copy()  # <-- [修復] 移除重複的股票代號

        print(f"  [成功] 獲取 {len(twse_stocks)} 筆上市/上櫃股票清單 (已過濾權證)。")
        return twse_stocks

    except Exception as e:
        print(f"  [錯誤] 獲取股票清單失敗: {e}", file=sys.stderr)
        return pd.DataFrame()


def get_stock_fundamentals(stock_id: str, stock_type: str) -> dict | None:
    """
    使用 yfinance 獲取單一股票的基本面資料。
    """
    # Yahoo Finance 的 Ticker 格式:
    # 上市 (twse) -> 2330.TW
    # 上櫃 (tpex) -> 6488.TWO
    suffix = ".TW" if stock_type == 'twse' else ".TWO"
    ticker_id = f"{stock_id}{suffix}"

    try:
        ticker = yf.Ticker(ticker_id)
        info = ticker.info

        # --- [優化 3] 獲取葛拉漢 (Graham) 估值法所需指標 ---
        eps = info.get('trailingEps')  # 每股盈餘 (EPS)
        bvps = info.get('bookValue')  # 每股淨值 (Book Value Per Share)
        price = info.get('currentPrice')  # 目前股價
        # ----------------------------------------

        # --- 獲取「體質」指標 ---
        # pe = info.get('trailingPE')  # (已停用)
        # pb = info.get('priceToBook') # (已停用)
        roe = info.get('returnOnEquity')

        # --- [優化 1] 獲取「品質」指標 ---
        de_ratio = info.get('debtToEquity')  # 負債權益比 (D/E Ratio)
        current_ratio = info.get('currentRatio')  # 流動比率
        dividend_yield = info.get('dividendYield')  # 股息殖利率

        # --- [優化 2] 獲取「成長」指標 ---
        revenue_growth = info.get('revenueGrowth')  # 營收成長率
        # ----------------------------------------

        # [修改] 檢查所有指標是否存在
        # P/E 和 P/B 已被葛拉漢模型取代，故移除
        if (
                # 葛拉漢
                eps is None or bvps is None or price is None or
                # 體質
                roe is None or
                # 品質
                current_ratio is None or dividend_yield is None or
                # 成長
                revenue_growth is None
                # 註: de_ratio (負債權益比) 允許為 None (代表 0 或無負債)
        ):
            return None  # 缺少任一關鍵指標，跳過

        # [優化 1] 處理 D/E Ratio
        # yfinance 的 'debtToEquity' 是百分比 (e.g., 55.8)，且 None 代表 0
        de_ratio_float = (de_ratio / 100.0) if de_ratio is not None else 0.0

        return {
            '股票代號': stock_id,
            # 葛拉漢
            'EPS': eps,
            'BVPS': bvps,
            '目前股價': price,
            # 體質
            '最新ROE': roe,
            # 品質
            '負債權益比': de_ratio_float,
            '流動比率': current_ratio,
            '股息殖利率': dividend_yield,
            # 成長
            '營收成長率': revenue_growth
        }

    except Exception as e:
        # 很多股票 (如金融股) 在 yfinance 上的 info 欄位不完整，會拋出錯誤
        # print(f"  > [錯誤] 獲取 {ticker_id} 資料失敗: {e}", file=sys.stderr)
        return None