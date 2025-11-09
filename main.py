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
    # 確保 EPS 和 BVPS 都為正數 (負數無法開根號，也代表公司虧損或淨值為負)
    if eps > 0 and bvps > 0:
        try:
            intrinsic_value = math.sqrt(22.5 * eps * bvps)
            return intrinsic_value
        except Exception:
            return None
    return None


def main():
    """
    主執行程式 - 結合葛拉漢估值、品質、體質與成長篩選
    """
    print("--- 開始篩選巴菲特/葛拉漢價值型股票 (使用 Yahoo Finance) ---")

    # 1. 獲取所有股票清單
    all_stocks = data_provider.get_all_stock_list()
    if all_stocks.empty:
        print("程式結束。")
        return

    # 2. 迭代清單，檢查基本面
    print(f"\n--- 2. 正在從 Yahoo Finance 檢查 {len(all_stocks)} 檔股票的基本面 ---")
    undervalued_stocks = []
    processed_stocks = 0

    # 使用 tqdm 顯示進度條
    for index, row in tqdm(all_stocks.iterrows(), total=all_stocks.shape[0]):
        stock_id = row['stock_id']
        stock_type = row['type']  # 'twse' or 'tpex'

        data = data_provider.get_stock_fundamentals(stock_id, stock_type)
        processed_stocks += 1

        if data is None:
            # time.sleep(0.05) # 資料不齊全，快速跳過
            continue

        # --- [優化 3] 葛拉漢估值法 ---
        intrinsic_value = calculate_graham_value(data['EPS'], data['BVPS'])

        if intrinsic_value is None:
            continue  # EPS 或 BVPS 為負，跳過

        # 計算納入安全邊際後的「目標買價」
        buy_price_target = intrinsic_value * config.MARGIN_OF_SAFETY

        # --- 套用所有篩選條件 (估值 + 體質 + 品質 + 成長) ---
        if (
                # [優化 3] 估值：目前股價 < 目標買價
                (data['目前股價'] < buy_price_target) and

                # [體質] ROE > 15%
                (data['最新ROE'] > config.ROE_MIN) and

                # [優化 1 - 品質] 負債權益比 < 50% (修復：加入 DE_RATIO_MAX 檢查)
                (data['負債權益比'] < config.DE_RATIO_MAX) and

                # [優化 1 - 品質] 流動比率 > 1.5
                (data['流動比率'] > config.CURRENT_RATIO_MIN) and

                # [優化 1 - 品質] 股息殖利率 > 2%
                (data['股息殖利率'] > config.DIVIDEND_YIELD_MIN) and

                # [優化 2 - 成長] 營收成長率 > 5%
                (data['營收成長率'] > config.REVENUE_GROWTH_MIN)
        ):
            print(f"\n*** {data['股票代號']} 符合所有條件! ***")

            # 將計算結果加入 dict
            data['內在價值'] = intrinsic_value
            data['目標買價'] = buy_price_target

            undervalued_stocks.append(data)

        # 休息一下，避免 API 鎖定
        # 即使資料不符，也休息一下
        if processed_stocks % 50 == 0:  # 每處理 50 筆休息久一點
            time.sleep(0.5)
        else:
            time.sleep(0.05)

    # 3. 顯示最終結果
    print("\n--- 3. 分析完成！符合價值投資條件的股票 ---")
    if not undervalued_stocks:
        print("本次篩選沒有找到同時符合所有條件的股票。")
    else:
        final_df = pd.DataFrame(undervalued_stocks)

        # 設定輸出欄位順序
        columns_order = [
            '目前股價',
            '目標買價',
            '內在價值',
            '最新ROE',
            '營收成長率',
            '股息殖利率',
            '負債權益比',
            '流動比率',
            'EPS',
            'BVPS'
        ]

        # 僅保留我們需要的欄位，並設定以「股票代號」為索引
        final_df = final_df.set_index('股票代號')[columns_order]

        # 使用 tabulate 格式化輸出
        print(final_df.to_markdown(
            headers={
                '目前股價': '目前股價',
                '目標買價': f"目標買價 ({config.MARGIN_OF_SAFETY * 100:.0f}%)",
                '內在價值': '葛拉漢 IV',
                '最新ROE': 'ROE (%)',
                '營收成長率': '營收成長 (%)',
                '股息殖利率': '股息率 (%)',
                '負債權益比': '負債權益比',
                '流動比率': '流動比率',
                'EPS': 'EPS',
                'BVPS': 'BVPS'
            },
            floatfmt=(
                ".2f",  # 目前股價
                ".2f",  # 目標買價
                ".2f",  # 內在價值
                ".2%",  # ROE
                ".2%",  # 營收成長率
                ".2%",  # 股息殖利率
                ".2f",  # 負債權益比
                ".2f",  # 流動比率
                ".2f",  # EPS
                ".2f"  # BVPS
            )
        ))


if __name__ == "__main__":
    main()