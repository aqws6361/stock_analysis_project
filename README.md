📈 台股價值投資篩選器 (Value Investing Screener)

這是一個使用 Python、FinMind 和 Yahoo Finance (yfinance) 打造的後端分析專案，旨在找出符合巴菲特式價值投資原則的台股。系統結合了 Streamlit 前端介面，提供可視化的分析結果。

🏗️ 專案架構

本專案採用模組化結構，職責分明：

app.py: (推薦) Streamlit 前端網頁介面，提供互動式圖表與詳細分析卡片。

.env: (需自行建立) 用於存放您的 FinMind API 金鑰。

config.py: 讀取 .env 金鑰，並集中管理所有篩選條件 (安全邊際、ROE、成長率等)。

data_provider.py: 負責所有外部 API 請求 (FinMind, yfinance) 與資料清洗。

main.py: 後端核心邏輯，負責執行篩選運算。

requirements.txt: 專案依賴的 Python 套件。

.gitignore: 確保 .env (包含您的金鑰) 和其他緩存檔案不會被上傳到 GitHub。

💡 核心投資邏輯 (Investment Logic)

本系統採用「葛拉漢 (Benjamin Graham)」價值投資邏輯，結合「巴菲特」的護城河概念。

1. 內在價值 (Intrinsic Value)

概念： 「這家公司原本應該值多少錢？」

我們使用葛拉漢公式來計算理論價值：

內在價值 = √( 22.5 × EPS × BVPS )

EPS (每股盈餘)：代表賺錢能力。

BVPS (每股淨值)：代表擁有的資產。

22.5：葛拉漢經驗係數 (給予 15 倍本益比 x 1.5 倍股價淨值比)。

2. 目標買價 (Target Buy Price)

概念： 「為了怕我看走眼，我最高願意出多少錢？」

為了對抗未知風險，我們設定了 安全邊際 (Margin of Safety)（預設 30%）：

目標買價 = 內在價值 × 0.7

3. 決策視覺化

系統會在全台股中尋找符合以下情境的標的（請見下方結構圖）：

💰 內在價值 (Intrinsic Value)  --> $100 元 (理論價值)
      |
      |   🛑 安全邊際 (Buffer) --> 預留 30% 空間
      |
🎯 目標買價 (Target Buy Price) --> $70 元  (進場門檻)
      |
      |   ✅ 潛在獲利空間 (Upside)
      |
📉 目前股價 (Current Price)    --> $50 元  (市場報價 - 超值！)


🚀 快速開始 (Quick Start)

1. 環境設定

建議使用 Python 3.8 以上版本，並建立一個虛擬環境：

# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境 (Windows)
.\venv\Scripts\activate
# (macOS/Linux)
# source venv/bin/activate


2. 設定 API 金鑰 (重要！)

在專案的根目錄下，手動建立一個名為 .env 的檔案。
打開這個檔案，並貼上以下內容，將 "YOUR_TOKEN_HERE" 替換為您自己的 FinMind API Token：

FINMIND_API_TOKEN="YOUR_TOKEN_HERE"


.gitignore 檔案已設定會忽略此檔案，您的金鑰不會被上傳。

3. 安裝依賴套件

安裝 requirements.txt 中的所有套件：

pip install -r requirements.txt


4. 執行程式

方式一：啟動網頁介面 (推薦)
這會開啟瀏覽器，顯示互動式圖表與詳細分析。

streamlit run app.py


方式二：僅執行終端機模式
這會在命令列直接印出篩選後的表格。

python main.py
