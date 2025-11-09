import os
from dotenv import load_dotenv

# 讀取 .env 檔案中的環境變數
load_dotenv()

# --- FinMind API 金鑰 ---
FINMIND_API_TOKEN = os.getenv("FINMIND_API_TOKEN")

# --- [優化 3] 葛拉漢 (Graham) 估值法 ---
# 我們不再使用固定的 PE_MAX 和 PB_MAX
# PE_MAX = 15       # (已停用)
# PB_MAX = 1.5      # (已停用)

# 我們改用「安全邊際」 (Margin of Safety)
# 意思是，我們希望股價低於其內在價值的 70% (即 30% 的安全邊際)
MARGIN_OF_SAFETY = 0.7
# ------------------------------------


# --- [保留] 體質、品質、成長篩選條件 ---

# 1. 體質 (Profitability)
ROE_MIN = 0.15    # 股東權益報酬率 (ROE) 高於 15% (即 0.15)
# ------------------------------------

# 2. 品質 (Quality) - [優化 1]
DE_RATIO_MAX = 0.5       # 負債權益比低於 0.5 (50%)
CURRENT_RATIO_MIN = 1.5  # 流動比率高於 1.5
DIVIDEND_YIELD_MIN = 0.02 # 股息殖利率高於 2% (0.02)
# ------------------------------------

# 3. 成長 (Growth) - [優化 2]
REVENUE_GROWTH_MIN = 0.05 # 年營收成長率高於 5% (0.05)
# ------------------------------------