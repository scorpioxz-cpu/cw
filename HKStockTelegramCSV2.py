import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from datetime import datetime
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="MarketPulse", page_icon="📈", layout="wide")

TELEGRAM_BOT_TOKEN = "8090361272:AAF3SBBJY3j3IdrRQR9L7cf6RbIgdUgq0SU"
TELEGRAM_CHAT_ID = "6467269037"  # <--- Replace with your ID

# Custom CSS
st.markdown("""
    <style>
    .sub-header { font-size: 20px; font-weight: bold; margin-top: 20px; margin-bottom: 10px; color: #1E88E5; }
    </style>
""", unsafe_allow_html=True)


def send_telegram_msg(winners_df, losers_df):
    today_str = datetime.now().strftime("%Y-%m-%d")
    header = f"🔔 *MarketPulse HK Summary ({today_str})*\n\n"
    win_text = "*Top 5 Winners:*\n"
    for _, row in winners_df.head(5).iterrows():
        win_text += f"• {row['TICKER']} ({row['COMPANY']}): {row['% CHANGE']} (@ {row['PRICE']})\n"
    lose_text = "\n*Top 5 Losers:*\n"
    for _, row in losers_df.head(5).iterrows():
        lose_text += f"• {row['TICKER']} ({row['COMPANY']}): {row['% CHANGE']} (@ {row['PRICE']})\n"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": header + win_text + lose_text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
        return True
    except:
        return False


def style_stoch(val):
    try:
        v = float(val)
        if v > 70:
            return 'color: #d23f31; font-weight: bold;'
        elif v < 30:
            return 'color: #0f9d58; font-weight: bold;'
        return 'color: white;'
    except:
        return ''


@st.cache_data(ttl=3600)
def get_market_data():
    hk_tickers = [
        "0001.HK", "0002.HK", "0003.HK", "0005.HK", "0006.HK",
        "0012.HK", "0016.HK", "0017.HK", "0019.HK",
        "0027.HK", "0066.HK", "0083.HK", "0101.HK", "0135.HK",
        "0151.HK", "0168.HK", "0175.HK", "0268.HK", "0288.HK",
        "0386.HK", "0669.HK", "0688.HK", "0700.HK", "0762.HK",
        "0823.HK", "0857.HK", "0861.HK", "0883.HK", "0902.HK",
        "0939.HK", "0941.HK", "0960.HK", "0981.HK", "0992.HK",
        "0998.HK", "1000.HK", "1038.HK", "1044.HK", "1093.HK",
        "1109.HK", "1177.HK", "1186.HK", "1211.HK", "1299.HK",
        "1378.HK", "1398.HK", "1755.HK", "1810.HK", "1876.HK",
        "1900.HK", "1928.HK", "1997.HK", "2007.HK", "2018.HK",
        "2088.HK", "2100.HK", "2111.HK", "2202.HK", "2232.HK",
        "2313.HK", "2318.HK", "2319.HK", "2333.HK", "2382.HK",
        "2628.HK", "2688.HK", "2698.HK", "2888.HK", "2899.HK",
        "3308.HK", "3328.HK", "3333.HK", "3690.HK", "3692.HK",
        "3969.HK", "3988.HK", "6030.HK", "6060.HK", "6098.HK",
        "6185.HK", "6618.HK", "6623.HK", "6633.HK", "6686.HK",
        "6818.HK", "6837.HK", "6869.HK", "6969.HK", "7321.HK",
        "8060.HK", "8083.HK", "8100.HK", "8222.HK", "8233.HK",
        "8255.HK", "8300.HK", "8353.HK", "8601.HK",
    ]
    summary_data, technical_data = [], []

    for ticker in hk_tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            if len(hist) < 25: continue

            curr_close = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            pct_change = ((curr_close - prev_close) / prev_close) * 100
            company_name = stock.info.get('shortName', ticker).replace('H SHS', '').strip()

            summary_data.append({
                "TICKER": ticker, "COMPANY": company_name, "PRICE": round(curr_close, 2),
                "CHANGE_VAL": pct_change, "% CHANGE": f"{'+' if pct_change > 0 else ''}{pct_change:.2f}%"
            })

            # Technicals
            hist['EMA10'] = hist['Close'].ewm(span=10, adjust=False).mean()
            hist['EMA20'] = hist['Close'].ewm(span=20, adjust=False).mean()
            low14, high14 = hist['Low'].rolling(14).min(), hist['High'].rolling(14).max()
            hist['Stoch'] = 100 * ((hist['Close'] - low14) / (high14 - low14))

            recent = hist.tail(4)
            for i in range(1, 4):
                curr, prev = recent.iloc[-i], recent.iloc[-(i + 1)]
                ctype = None
                if prev['EMA10'] <= prev['EMA20'] and curr['EMA10'] > curr['EMA20']:
                    ctype = 'Bullish'
                elif prev['EMA10'] >= prev['EMA20'] and curr['EMA10'] < curr['EMA20']:
                    ctype = 'Bearish'

                if ctype:
                    technical_data.append({
                        "Ticker": ticker, "Company": company_name, "Price": round(curr_close, 2),
                        "EMA 10 / 20": f"{hist['EMA10'].iloc[-1]:.2f} / {hist['EMA20'].iloc[-1]:.2f}",
                        "Stoch": round(hist['Stoch'].iloc[-1]),
                        "Days Ago": f"{i - 1} days" if i - 1 > 0 else "Today", "Type": ctype
                    })
                    break
        except:
            continue
    return pd.DataFrame(summary_data), pd.DataFrame(technical_data)


# --- EXECUTION ---
st.title("📈 MarketPulse: HK Stock Summary")
summary_df, tech_df = get_market_data()

if not summary_df.empty:
    winners = summary_df.sort_values(by="CHANGE_VAL", ascending=False).head(10)
    losers = summary_df.sort_values(by="CHANGE_VAL", ascending=True).head(10)

    # --- AUTO-GENERATING CSV FOR DOWNLOAD ---
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Sidebar for data exports
    st.sidebar.header("📥 Data Exports")
    st.sidebar.write(f"Data for {today_date}")


    # Function to convert DF to CSV
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')


    st.sidebar.download_button(
        label="Download Winners CSV",
        data=convert_df(winners),
        file_name=f"HK_Winners_{today_date}.csv",
        mime="text/csv",
    )

    st.sidebar.download_button(
        label="Download Losers CSV",
        data=convert_df(losers),
        file_name=f"HK_Losers_{today_date}.csv",
        mime="text/csv",
    )

    # --- TELEGRAM AUTO-SEND ---
    if 'last_send_date' not in st.session_state:
        st.session_state.last_send_date = None

    if st.session_state.last_send_date != today_date:
        if TELEGRAM_CHAT_ID != "YOUR_CHAT_ID_HERE":
            if send_telegram_msg(winners, losers):
                st.session_state.last_send_date = today_date
                st.toast("Telegram Summary Sent!")

    # --- UI TABS ---
    tab1, tab2 = st.tabs(["📊 Market Summary", "🔍 Technical Filtering"])

    with tab1:
        st.markdown('<div class="sub-header">Top 10 Market Winners 🚀</div>', unsafe_allow_html=True)
        st.dataframe(winners[["TICKER", "COMPANY", "PRICE", "% CHANGE"]], use_container_width=True, hide_index=True)
        st.markdown('<div class="sub-header">Top 10 Market Losers 🔻</div>', unsafe_allow_html=True)
        st.dataframe(losers[["TICKER", "COMPANY", "PRICE", "% CHANGE"]], use_container_width=True, hide_index=True)

    with tab2:
        if not tech_df.empty:
            for t_type, icon in [('Bullish', '📈'), ('Bearish', '📉')]:
                st.markdown(f'<div class="sub-header">{icon} {t_type} Crossovers</div>', unsafe_allow_html=True)
                sub = tech_df[tech_df['Type'] == t_type].drop(columns=['Type'])
                if not sub.empty:
                    st.dataframe(sub.style.map(style_stoch, subset=['Stoch']), use_container_width=True,
                                 hide_index=True)
        else:
            st.info("No EMA crossovers found in the last 3 days.")