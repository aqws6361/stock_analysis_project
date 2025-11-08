import os
from dotenv import load_dotenv
import sys

# 1. 載入 .env 檔案中的環境變數
load_dotenv()

# 2. 讀取 FinMind API Token
FINMIND_API_TOKEN = os.getenv("FINMIND_API_TOKEN")

if not FINMIND_API_TOKEN:
    print("  [錯誤] 找不到 FINMIND_API_TOKEN。", file=sys.stderr)
    print("  請確認您已經建立了 .env 檔案，並在其中加入了 FINMIND_API_TOKEN=\"您的Token\"。", file=sys.stderr)
    sys.exit(1) # 程式中斷

# --- 設定篩選條件 (巴菲特指標) ---
PE_MAX = 15       # 本益比低於 15
PB_MAX = 1.5      # 股價淨值比低於 1.5
ROE_MIN = 0.15    # 股東權益報酬率 (ROE) 高於 15% (即 0.15)
# ------------------------------------