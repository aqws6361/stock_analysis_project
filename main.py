import pandas as pd
import time
import math
import sys
from tqdm import tqdm
import config  # 引入設定檔
import data_provider  # 引入資料獲取模組


def calculate_graham_value(eps: float, bvps: float) -> float | None:
    """
    計算葛拉漢 (Graham) 內在價值。
    公式: IV = sqrt(22.5 * EPS * BVPS)
    """
    if eps > 0 and bvps > 0:
        try:
            intrinsic_value = math.sqrt(22.5 * eps * bvps)
            return intrinsic_value
        except Exception:
            return None
    return None


def run_analysis(progress_callback=None) -> pd.DataFrame:
    """
    執行完整的篩選邏輯，並回傳 DataFrame。
    progress_callback: 一個函式，用來更新前端的進度條 (選填)
    """
    # 1. 獲取所有股票清單
    all_stocks = data_provider.get_all_stock_list()
    if all_stocks.empty:
        return pd.DataFrame()

    undervalued_stocks = []
    total_stocks = all_stocks.shape[0]
    processed_count = 0

    # 2. 迭代清單
    # 如果是終端機執行，使用 tqdm；如果是網頁呼叫，我們就不顯示 tqdm
    iterator = tqdm(all_stocks.iterrows(), total=total_stocks) if progress_callback is None else all_stocks.iterrows()

    for index, row in iterator:
        stock_id = row['stock_id']
        stock_type = row['type']

        # 更新進度
        processed_count += 1
        if progress_callback:
            # 更新網頁進度條 (0.0 ~ 1.0)
            progress_callback(processed_count / total_stocks, f"正在分析: {stock_id}...")

        data = data_provider.get_stock_fundamentals(stock_id, stock_type)

        if data is None:
            continue

        # --- 葛拉漢估值法 ---
        intrinsic_value = calculate_graham_value(data['EPS'], data['BVPS'])

        if intrinsic_value is None:
            continue

        buy_price_target = intrinsic_value * config.MARGIN_OF_SAFETY

        # --- 套用所有篩選條件 ---
        if (
                (data['目前股價'] < buy_price_target) and
                (data['最新ROE'] > config.ROE_MIN) and
                (data['負債權益比'] < config.DE_RATIO_MAX) and
                (data['流動比率'] > config.CURRENT_RATIO_MIN) and
                (data['股息殖利率'] > config.DIVIDEND_YIELD_MIN) and
                (data['營收成長率'] > config.REVENUE_GROWTH_MIN)
        ):
            # 補上詳細資訊
            data['內在價值'] = intrinsic_value
            data['目標買價'] = buy_price_target
            # 計算潛在獲利空間 (Upside)
            data['潛在獲利'] = (intrinsic_value - data['目前股價']) / data['目前股價']

            undervalued_stocks.append(data)

        # 稍微休息避免鎖 IP
        if processed_count % 50 == 0:
            time.sleep(0.5)
        else:
            time.sleep(0.05)

    if not undervalued_stocks:
        return pd.DataFrame()

    final_df = pd.DataFrame(undervalued_stocks)

    # 整理欄位順序
    columns_order = [
        '目前股價', '目標買價', '內在價值', '潛在獲利',
        '最新ROE', '營收成長率', '股息殖利率',
        '負債權益比', '流動比率', 'EPS', 'BVPS'
    ]

    final_df = final_df.set_index('股票代號')[columns_order]
    return final_df


def main():
    """
    終端機使用的進入點
    """
    print("--- 開始篩選巴菲特/葛拉漢價值型股票 (終端機模式) ---")
    df = run_analysis()

    if df.empty:
        print("本次篩選沒有找到符合條件的股票。")
    else:
        print("\n--- 分析完成！符合價值投資條件的股票 ---")
        print(df.to_markdown(floatfmt=".2f"))


if __name__ == "__main__":
    main()