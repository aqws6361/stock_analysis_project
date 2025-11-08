# 台股價值投資篩選器 (Value Investing Screener)

這是一個使用 **Python、FinMind** 和 **Yahoo Finance (yfinance)** 打造的後端分析專案，旨在找出符合巴菲特式價值投資原則的台股。

---

## 📁 專案架構

本專案已重構為模組化結構，易於維護：

.env # (需自行建立) 用於存放您的 FinMind API 金鑰

config.py # 讀取 .env 金鑰，並集中管理所有篩選條件 (P/E, P/B, ROE)

data_provider.py # 負責所有外部 API 請求 (FinMind, yfinance)

main.py # 專案的主執行檔，負責執行篩選邏輯並印出結果

requirements.txt # 專案依賴的 Python 套件

.gitignore # 確保 .env (包含您的金鑰) 和其他緩存檔案不會被上傳到 GitHub


---

## 🚀 快速開始 (Quick Start)

### 1. 環境設定

建議使用 **Python 3.8** 以上版本，並建立一個虛擬環境：

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境 (Windows)
.\venv\Scripts\activate

# (macOS/Linux)
# source venv/bin/activate
2. 設定 API 金鑰 (重要！)
在專案的根目錄下，手動建立一個名為 .env 的檔案。
打開這個檔案，並貼上以下內容：

bash
複製程式碼
FINMIND_API_TOKEN="YOUR_TOKEN_HERE"
請將 "YOUR_TOKEN_HERE" 替換為您自己的 FinMind API Token。

.gitignore 檔案已設定會忽略此檔案，您的金鑰不會被上傳。

3. 安裝依賴套件
安裝 requirements.txt 中的所有套件 (包含 python-dotenv)：

bash
複製程式碼
pip install -r requirements.txt
4. 執行程式
一切就緒後，直接執行主程式：

bash
複製程式碼
python main.py
程式將會自動：

讀取 .env 金鑰

透過 data_provider.py 取得資料

在 main.py 中執行篩選邏輯並印出結果

---