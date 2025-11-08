import pandas as pd
import time
from tqdm import tqdm

# 匯入自己的模組
import data_provider
import config


def main():
    """
    主執行程式
    """
    print("--- 開始篩選巴菲特價值型股票 (使用 Yahoo Finance) ---")

    # 1. 獲取所有股票清單
    # (邏輯已移至 data_provider.py)
    all_stocks = data_provider.get_all_stock_list()
    if all_stocks.empty:
        print("程式結束。")
        return

    # 2. 迭代清單，檢查基本面
    print(f"\n--- 2. 正在從 Yahoo Finance 檢查 {len(all_stocks)} 檔股票的基本面 ---")
    undervalued_stocks = []

    # 使用 tqdm 顯示進度條
    for index, row in tqdm(all_stocks.iterrows(), total=all_stocks.shape[0]):
        stock_id = row['stock_id']
        stock_type = row['type']  # 'twse' or 'tpex'

        # (邏輯已移至 data_provider.py)
        data = data_provider.get_stock_fundamentals(stock_id, stock_type)

        if data is None:
            time.sleep(0.05)  # 休息一下，避免 API 鎖定
            continue

        # 應用巴菲特篩選條件
        # (常數已移至 config.py)
        if (
                (data['本益比'] < config.PE_MAX) and (data['本益比'] > 0) and
                (data['股價淨值比'] < config.PB_MAX) and (data['股價淨值比'] > 0) and
                (data['最新ROE'] > config.ROE_MIN)
        ):
            print(f"\n*** {data['股票代號']} 符合所有條件! ***")
            undervalued_stocks.append(data)

        # 休息一下，避免 API 鎖定
        time.sleep(0.05)

    # 3. 顯示最終結果
    print("\n--- 3. 分析完成！符合巴菲特價值投資條件的股票 ---")
    if not undervalued_stocks:
        print("本次篩選沒有找到同時符合所有條件的股票。")
    else:
        final_df = pd.DataFrame(undervalued_stocks)
        final_df.set_index('股票代號', inplace=True)

        # 使用 tabulate 格式化輸出
        print(final_df.to_markdown(
            floatfmt=(".0f", ".2f", ".2f", ".2%"),
            headers=['股票代號', '本益比', '股價淨值比', '最新ROE']
        ))


if __name__ == "__main__":
    main()
