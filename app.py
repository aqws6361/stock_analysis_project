import streamlit as st
import pandas as pd
import plotly.express as px
import config
import main  # 匯入我們的後端邏輯

# --- 頁面設定 ---
st.set_page_config(
    page_title="台股價值投資篩選器",
    page_icon="📈",
    layout="wide"
)

# --- 側邊欄：顯示目前的篩選策略 ---
st.sidebar.header("⚙️ 篩選策略參數")
st.sidebar.markdown(f"""
**1. 葛拉漢估值 (Graham Valuation)**
* 安全邊際: `{config.MARGIN_OF_SAFETY * 100:.0f}%`
* 策略: 買入價 < 內在價值 × 安全邊際

**2. 體質與品質 (Quality)**
* ROE (股東權益報酬率): > `{config.ROE_MIN * 100:.0f}%`
* 負債權益比: < `{config.DE_RATIO_MAX}`
* 流動比率: > `{config.CURRENT_RATIO_MIN}`
* 股息殖利率: > `{config.DIVIDEND_YIELD_MIN * 100:.0f}%`

**3. 成長性 (Growth)**
* 營收成長率: > `{config.REVENUE_GROWTH_MIN * 100:.0f}%`
""")

st.sidebar.info("資料來源: FinMind (清單) + Yahoo Finance (個股數據)")

# --- 主畫面 ---
st.title("📈 台股價值投資篩選器")
st.markdown("""
這個系統結合了 **巴菲特 (體質/護城河)** 與 **葛拉漢 (安全邊際)** 的投資哲學。
點擊下方按鈕開始掃描台股市場，尋找被低估的優質標的。
""")

# 建立一個容器來放按鈕，避免分析完後按鈕消失或跑版
col1, col2 = st.columns([1, 4])
with col1:
    start_btn = st.button("🚀 開始全市場掃描", type="primary", use_container_width=True)

if start_btn:
    # 顯示進度條
    progress_bar = st.progress(0, text="正在初始化 API...")


    # 定義回呼函式來更新進度條
    def update_progress(percent, message):
        # 確保百分比在 0.0 到 1.0 之間
        safe_percent = min(max(percent, 0.0), 1.0)
        progress_bar.progress(safe_percent, text=message)


    # --- 執行後端邏輯 ---
    try:
        with st.spinner('正在分析數千檔台股資料，請稍候... (這可能需要幾分鐘)'):
            # 呼叫 main.py 裡面的 run_analysis 函式
            df = main.run_analysis(progress_callback=update_progress)

        progress_bar.empty()  # 完成後隱藏進度條

        if df.empty:
            st.warning("本次掃描沒有發現符合所有嚴格條件的股票。可能是市場目前估值普遍偏高。")
        else:
            st.success(f"分析完成！共發現 {len(df)} 檔潛力股。")

            # --- 1. 互動式表格 ---
            st.subheader("📋 候選清單")

            # 複製一份資料來做格式化顯示 (百分比和小數)，不影響原始數值
            display_df = df.copy()

            # 針對各欄位進行字串格式化，讓顯示更好看
            if '潛在獲利' in display_df.columns:
                display_df['潛在獲利'] = display_df['潛在獲利'].apply(lambda x: f"{x:.2%}")
            if '最新ROE' in display_df.columns:
                display_df['最新ROE'] = display_df['最新ROE'].apply(lambda x: f"{x:.2%}")
            if '股息殖利率' in display_df.columns:
                display_df['股息殖利率'] = display_df['股息殖利率'].apply(lambda x: f"{x:.2%}")
            if '營收成長率' in display_df.columns:
                display_df['營收成長率'] = display_df['營收成長率'].apply(lambda x: f"{x:.2%}")

            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "目前股價": st.column_config.NumberColumn(format="$%.2f"),
                    "目標買價": st.column_config.NumberColumn(format="$%.2f", help="內在價值 * 安全邊際"),
                    "內在價值": st.column_config.NumberColumn(format="$%.2f", help="葛拉漢公式計算出的理論價值"),
                }
            )

            # --- 2. 視覺化分析 (散佈圖) ---
            st.subheader("📊 價值空間視覺化")
            st.markdown(
                "此圖表顯示**目前股價**與**內在價值**的距離。點越靠近右下角，代表「內在價值高」且「股價便宜」，CP值越高。")

            # 準備畫圖資料
            plot_data = df.reset_index()

            # 繪製散佈圖
            fig = px.scatter(
                plot_data,
                x="內在價值",
                y="目前股價",
                size="潛在獲利",  # 泡泡大小代表潛在獲利空間
                color="最新ROE",  # 顏色深淺代表 ROE
                hover_name="股票代號",
                hover_data=["目標買價", "負債權益比", "營收成長率"],
                text="股票代號",
                title="股價 vs 內在價值 (泡泡大小 = 潛在獲利空間)"
            )
            # 加一條 45度線 (股價=價值)
            max_val = max(plot_data['內在價值'].max(), plot_data['目前股價'].max())
            fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                          line=dict(color="Red", width=2, dash="dash"), name="合理價值線")

            st.plotly_chart(fig, use_container_width=True)

            # --- 3. 個股詳細分析卡片 ---
            st.subheader("🔍 為什麼被低估？ (個股詳情)")

            cols = st.columns(3)  # 排版：一行三個
            for i, (stock_id, row) in enumerate(df.iterrows()):
                with cols[i % 3]:
                    with st.expander(f"📈 {stock_id} 投資亮點", expanded=True):
                        st.metric("目前股價", f"{row['目前股價']:.2f}",
                                  delta=f"{row['潛在獲利']:.1%} 潛在空間")

                        st.markdown(f"""
                        * **葛拉漢內在價值**: `{row['內在價值']:.2f}`
                        * **安全邊際後目標價**: `{row['目標買價']:.2f}`
                        ---
                        * **體質 (ROE)**: `{row['最新ROE']:.1%}` (標準 > 15%)
                        * **成長 (營收)**: `{row['營收成長率']:.1%}` (標準 > 5%)
                        * **安全 (負債比)**: `{row['負債權益比']:.2f}` (標準 < 0.5)
                        """)

    except Exception as e:
        st.error(f"發生錯誤: {e}")