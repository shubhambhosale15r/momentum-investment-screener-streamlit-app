import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
import plotly.express as px
import time

# Set page config FIRST (removes menu and footer)
st.set_page_config(
    page_title="Stock Analyzer",
    page_icon="📈",
    layout="wide",
    menu_items=None  # Hides the top-right menu button
)

# Custom CSS to hide header and footer
st.markdown("""
    <style>
        /* Hide Streamlit's header and footer */
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Set dark background for the app */
        .stApp {
            background: linear-gradient(135deg, #141E30, #243B55);
            color: #e0e0e0;
        }

        /* Title styling */
        h1 {
            color: #1E90FF;
            text-align: center;
            font-size: 3rem;
            font-weight: bold;
        }

        /* Button styling */
        .stButton button {
            background-color: #1E90FF;
            color: #ffffff;
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 1.2rem;
            transition: background-color 0.3s ease;
            border: none;
        }

        .stButton button:hover {
            background-color: #1C86EE;
        }

        /* DataFrame styling */
        .stDataFrame {
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        }

        /* Progress bar styling */
        .stProgress > div > div {
            background-color: #1E90FF;
        }

        /* Metric box styling */
        .metric-box {
            background: #2C2C2C;
            border-radius: 10px;
            padding: 20px;
            margin: 10px;
            text-align: center;
        }

        /* Sidebar styling */
        .css-1d391kg { 
            background-color: #1e1e1e; 
            color: #e0e0e0;
        }
        /* Hiding the made with streamlit  */
        .st-emotion-cache-1v0mbdj {display: none;}
    </style>
""", unsafe_allow_html=True)


# Title and subtitle
st.title("📈 Stock Analyzer")
st.markdown("""
    <div style="text-align: center; font-size: 1.2rem; color: #c0c0c0;">
        Comprehensive momentum analysis with interactive visualizations.
    </div>
""", unsafe_allow_html=True)

# Fixed lists of stocks (user cannot edit these)
nifty_midcap_50_symbols = [
    "ACC.NS", "APLAPOLLO.NS", "AUBANK.NS", "ABCAPITAL.NS", "ALKEM.NS",
    "ASHOKLEY.NS", "ASTRAL.NS", "AUROPHARMA.NS", "BHARATFORG.NS", "CGPOWER.NS",
    "COLPAL.NS", "CONCOR.NS", "CUMMINSIND.NS", "DIXON.NS", "FEDERALBNK.NS",
    "GMRAIRPORT.NS", "GODREJPROP.NS", "HDFCAMC.NS", "HINDPETRO.NS", "IDFCFIRSTB.NS",
    "INDHOTEL.NS", "INDUSTOWER.NS", "KPITTECH.NS", "LTF.NS", "LUPIN.NS", "MRF.NS",
    "MARICO.NS", "MAXHEALTH.NS", "MPHASIS.NS", "MUTHOOTFIN.NS", "NMDC.NS",
    "OBEROIRLTY.NS", "OFSS.NS", "POLICYBZR.NS", "PIIND.NS", "PERSISTENT.NS",
    "PETRONET.NS", "PHOENIXLTD.NS", "POLYCAB.NS", "SBICARD.NS", "SRF.NS", "SAIL.NS",
    "SUNDARMFIN.NS", "SUPREMEIND.NS", "SUZLON.NS", "TATACOMM.NS", "UPL.NS", "IDEA.NS",
    "VOLTAS.NS", "YESBANK.NS"
]

nifty_50_stocks = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BPCL.NS",
    "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
    "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
    "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
    "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
    "TECHM.NS", "TITAN.NS", "TRENT.NS", "ULTRACEMCO.NS", "WIPRO.NS"
]

# Sidebar: Allow user to choose the stock universe (read-only)
stock_universe = st.sidebar.radio(
    "Select Stock Universe",
    ("Nifty Midcap 50 Stocks", "Nifty 50 Stocks")
)

if stock_universe == "Nifty Midcap 50 Stocks":
    selected_stocks = nifty_midcap_50_symbols
    st.sidebar.info("You have selected the Nifty Midcap 50 stock list.")
else:
    selected_stocks = nifty_50_stocks
    st.sidebar.info("You have selected the Nifty 50 stock list.")

# Cache data to optimize downloads
@st.cache_data(show_spinner=False)
def download_stock_data(ticker, start_date, end_date, retries=3):
    for _ in range(retries):
        try:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
            if df.empty:
                raise ValueError(f"No data returned for {ticker}")
            df['Date'] = df.index
            df.reset_index(drop=True, inplace=True)
            return df
        except Exception as e:
            print(f"Retrying {ticker}: {e}")
    print(f"Failed to download data for {ticker} after {retries} retries")
    return pd.DataFrame()

# Calculate returns for a given period
def calculate_returns(df, period):
    if len(df) >= period:
        close_prices = df['Close'].values
        end_price = close_prices[-1]
        start_price = close_prices[-period]
        return ((end_price - start_price) / start_price).item()
    else:
        return np.nan

# Main application function
def main():
    if st.button("Analyze Stocks"):
        with st.spinner("Analyzing stocks... Please wait."):
            end_date = datetime.today().date()
            start_date = end_date - timedelta(days=400)
            results = []

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Process each ticker with a progress bar
            for i, ticker in enumerate(tqdm(selected_stocks, desc="Processing Tickers", leave=False)):
                df = download_stock_data(ticker, start_date, end_date)
                if df.empty:
                    st.warning(f"No data for {ticker}, skipping...")
                    continue

                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
                df = df[~df.index.duplicated()]
                num_trading_days = len(df)

                # Resample to weekly data and compute weekly returns
                df_weekly = df.resample('W').last()
                df_weekly['Weekly Return'] = df_weekly['Close'].pct_change()
                weekly_volatility = df_weekly['Weekly Return'].dropna().std() * np.sqrt(52)

                # Calculate returns
                return_12M = calculate_returns(df, 252)
                return_6M = calculate_returns(df, 126)
                return_3M = calculate_returns(df, 63)

                # Compute momentum score
                if (weekly_volatility != 0 and pd.notna(return_12M) and pd.notna(return_6M) and pd.notna(return_3M)):
                    momentum_score = ((0.6 * return_12M) + (0.3 * return_6M) + (0.1 * return_3M)) / weekly_volatility
                else:
                    momentum_score = np.nan

                results.append({
                    "Ticker": ticker,
                    "Trading Days": num_trading_days,
                    "12-Month Return (%)": return_12M * 100 if pd.notna(return_12M) else np.nan,
                    "6-Month Return (%)": return_6M * 100 if pd.notna(return_6M) else np.nan,
                    "3-Month Return (%)": return_3M * 100 if pd.notna(return_3M) else np.nan,
                    "Annualized Volatility": weekly_volatility,
                    "Momentum Score": momentum_score
                })

                progress_bar.progress(int(((i + 1) / len(selected_stocks)) * 100))
                status_text.text(f"Processing {ticker} ({i + 1}/{len(selected_stocks)})")

            results_df = pd.DataFrame(results)
            results_df.sort_values(by="Momentum Score", ascending=False, inplace=True)
            pd.set_option('display.float_format', '{:.2f}'.format)

            st.success("Analysis complete.")

            # Create tabs for organized output
            tab1, tab2, tab3 = st.tabs(["Data Table", "Visualizations", "Key Metrics"])

            with tab1:
                st.subheader("Analysis Results")
                st.dataframe(results_df[["Ticker", "Momentum Score", "12-Month Return (%)",
                                         "6-Month Return (%)", "3-Month Return (%)", "Annualized Volatility"]],
                             height=500)

            with tab2:
                st.subheader("Visualizations")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("*Momentum Score Distribution*")
                    fig1 = px.histogram(results_df, x="Momentum Score", nbins=20, color_discrete_sequence=["#1E90FF"])
                    st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    st.markdown("*12-Month Return vs Volatility*")
                    fig2 = px.scatter(results_df, x="Annualized Volatility", y="12-Month Return (%)",
                                      hover_data=["Ticker"], color="Momentum Score", color_continuous_scale="Viridis")
                    st.plotly_chart(fig2, use_container_width=True)

            with tab3:
                st.subheader("Key Metrics")
                if not results_df.empty:
                    best = results_df.iloc[0]
                    worst = results_df.iloc[-1]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(label=f"Best Momentum: {best['Ticker']}", value=f"{best['Momentum Score']:.2f}",
                                  delta=f"{best['12-Month Return (%)']:.2f}%")
                    with col2:
                        st.metric(label=f"Worst Momentum: {worst['Ticker']}", value=f"{worst['Momentum Score']:.2f}",
                                  delta=f"{worst['12-Month Return (%)']:.2f}%")
                else:
                    st.write("No data available.")

if __name__ == '__main__':
    main()
