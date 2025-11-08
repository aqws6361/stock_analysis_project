import pandas as pd
from FinMind.data import FinMindApi
import yfinance as yf
import sys
import config  # 匯入設定檔

# --- 初始化 API 客戶端 ---
try:
    # 讀取 config.py 中載入的 Token
    finmind_api = FinMindApi()
    finmind_api.login_by_token(api_token=config.FINMIND_API_TOKEN)
except Exception as e:
    print(f"  [錯誤] FinMind API 初始化失敗: {e}", file=sys.stderr)
    sys.exit(1)


# -------------------------


def get_all_stock_list() -> pd.DataFrame:
    """
    使用 FinMind (唯一可用的 API) 獲取所有台股清單 (上市 + 上櫃)。
    """
    print("--- 1. 正在從 FinMind 獲取所有台股清單 (TaiwanStockInfo) ---")
    try:
        # 使用我們在模組層級初始化的 api 物件
        df_twse = finmind_api.get_data(dataset="TaiwanStockInfo", data_id="")
        if df_twse is None or df_twse.empty:
            print("  [錯誤] 無法從 FinMind 獲取股票清單。", file=sys.stderr)
            return pd.DataFrame()

        # 篩選出 '上市' (TWSE) 和 '上櫃' (OTC)
        twse_stocks = df_twse[
            (df_twse['industry_category'] != 'None') &
            (df_twse['stock_id'] != '') &
            (df_twse['type'].isin(['twse', 'tpex'])) &  # twse=上市, tpex=上櫃
            (df_twse['stock_id'].str.len() == 4)  # [優化] 只保留 4 位數的股票代號 (過濾權證)
            ]

        print(f"  [成功] 獲取 {len(twse_stocks)} 筆上市/上櫃股票清單 (已過濾權證)。")
        return twse_stocks

    except Exception as e:
        print(f"  [錯誤] 獲取股票清單失敗: {e}", file=sys.stderr)
        return pd.DataFrame()


def get_stock_fundamentals(stock_id: str, stock_type: str) -> dict | None:
    """
    使用 yfinance 獲取單一股票的基本面資料 (P/E, P/B, ROE)。
    """
    # Yahoo Finance 的 Ticker 格式:
    # 上市 (twse) -> 2330.TW
    # 上櫃 (tpex) -> 6488.TWO
    suffix = ".TW" if stock_type == 'twse' else ".TWO"
    ticker_id = f"{stock_id}{suffix}"

    try:
        ticker = yf.Ticker(ticker_id)
        info = ticker.info

        # --- 獲取 Yahoo Finance 上的關鍵指標 ---
        pe = info.get('trailingPE')
        pb = info.get('priceToBook')
        roe = info.get('returnOnEquity')
        # ----------------------------------------

        if not all([pe, pb, roe]):
            return None  # 缺少任一關鍵指標，跳過

        return {
            '股票代號': stock_id,
            '本益比': pe,
            '股價淨值比': pb,
            '最新ROE': roe
        }

    except Exception as e:
        # print(f"  > [錯誤] 獲取 {ticker_id} 資料失敗: {e}", file=sys.stderr)
        return None