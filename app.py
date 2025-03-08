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
        /* Professional Dark Theme with Enhanced Alignment */
        header {visibility: hidden;}
        footer {visibility: hidden;}

        .stApp {
            background: linear-gradient(135deg, #0a192f, #172a45);
            color: #ccd6f6;
            font-family: 'Inter', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 3rem !important;
        }

        h1 {
            color: #64ffda;
            text-align: center;
            font-size: 2.8rem;
            font-weight: 700;
            margin: 1rem 0 2rem 0;
            letter-spacing: -0.5px;
        }

        .stButton button {
            background: linear-gradient(135deg, #64ffda 0%, #4ecdc4 100%);
            color: #0a192f !important;
            border-radius: 8px;
            padding: 12px 28px;
            font-size: 1.1rem;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: none;
            display: block;
            margin: 1.5rem auto;
            width: fit-content;
            box-shadow: 0 4px 12px rgba(100, 255, 218, 0.2);
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(100, 255, 218, 0.3);
        }

        .stDataFrame {
            border-radius: 12px;
            border: 1px solid #233554 !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
            margin: 2rem 0;
        }

        .metric-box {
            background: #112240;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid #233554;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .css-1d391kg { 
            background-color: #0a192f !important;
            border-right: 1px solid #233554 !important;
        }

        /* Unified Container Styling */
        .stContainer {
            padding: 2rem;
            margin: 2rem 0;
            background: #112240;
            border-radius: 12px;
            border: 1px solid #233554;
        }

        /* Improved Typography Hierarchy */
        h2 {
            color: #8892b0;
            font-size: 1.5rem;
            margin: 1.5rem 0;
            font-weight: 500;
        }

        h3 {
            color: #64ffda;
            font-size: 1.2rem;
            margin: 1rem 0;
        }

        /* Enhanced Responsive Design */
        @media (max-width: 768px) {
            .stApp {
                padding: 1.5rem !important;
            }

            h1 {
                font-size: 2.2rem;
                margin: 0.5rem 0 1.5rem 0;
            }

            .stButton button {
                width: 100%;
                max-width: none;
            }
        }

        /* Consistent Spacing */
        .stMarkdown, .stDataFrame, .stPlotlyChart {
            margin: 1.5rem 0 !important;
        }

        /* Professional Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            background: #0a192f;
        }

        ::-webkit-scrollbar-thumb {
            background: #64ffda;
            border-radius: 4px;
        }

        /* Hidden Elements */
        .st-emotion-cache-16txtl3, 
        [data-testid="stDecoration"], 
        .stDeployButton,
        .viewerBadge_link__qRIco,
        .styles_viewerBadge__1yB5_ {
            display: none !important;
        }
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
nifty_smallcap_50_symbols=[
    "360ONE.NS", "AARTIIND.NS", "ABREL.NS", "ARE&M.NS", "ANGELONE.NS", "APARINDS.NS", "ATUL.NS",
    "BSOFT.NS", "BLUESTARCO.NS", "BRIGADE.NS", "CESC.NS", "CASTROLIND.NS", "CDSL.NS", "CAMS.NS",
    "CROMPTON.NS", "CYIENT.NS", "FINCABLES.NS", "GLENMARK.NS", "GESHIP.NS", "GSPL.NS", "HFCL.NS",
    "HINDCOPPER.NS", "IIFL.NS", "INDIAMART.NS", "IEX.NS", "KPIL.NS", "KARURVYSYA.NS", "LAURUSLABS.NS",
    "MGL.NS", "MANAPPURAM.NS", "MCX.NS", "NATCOPHARM.NS", "NBCC.NS", "NCC.NS", "NH.NS", "NATIONALUM.NS",
    "NAVINFLUOR.NS", "PNBHOUSING.NS", "PVRINOX.NS", "PEL.NS", "PPLPHARMA.NS", "RBLBANK.NS", "RADICO.NS",
    "RKFORGE.NS", "REDINGTON.NS", "SONATSOFTW.NS", "TEJASNET.NS", "RAMCOCEM.NS", "ZEEL.NS", "ZENSARTECH.NS"
]
nifty_auto_symbols = [
    "APOLLOTYRE.NS",
    "ASHOKLEY.NS",
    "BAJAJ-AUTO.NS",
    "BALKRISIND.NS",
    "BHARATFORG.NS",
    "BOSCHLTD.NS",
    "EICHERMOT.NS",
    "EXIDEIND.NS",
    "HEROMOTOCO.NS",
    "MRF.NS",
    "M&M.NS",
    "MARUTI.NS",
    "MOTHERSON.NS",
    "TVSMOTOR.NS",
    "TATAMOTORS.NS"
]
nifty_bank_symbols = [
    "AUBANK.NS",
    "AXISBANK.NS",
    "BANKBARODA.NS",
    "CANBK.NS",
    "FEDERALBNK.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "IDFCFIRSTB.NS",
    "INDUSINDBK.NS",
    "KOTAKBANK.NS",
    "PNB.NS",
    "SBIN.NS"
]
# Sidebar: Allow user to choose the stock universe (read-only)
stock_universe = st.sidebar.radio(
    "Select Stock Universe",
    ("Nifty Midcap 50 Stocks", "Nifty 50 Stocks","Nifty Smallcap 50 Stocks","Nifty Nifty Auto Stocks","Nifty Bank Stocks")
)

if stock_universe == "Nifty Midcap 50 Stocks":
    selected_stocks = nifty_midcap_50_symbols
    st.sidebar.info("You have selected the Nifty Midcap 50 stock list.")
elif stock_universe == "Nifty Smallcap 50 Stocks":
    selected_stocks = nifty_smallcap_50_symbols
    st.sidebar.info("You have selected the Nifty Smallcap 50 stock list.")
elif stock_universe == "Nifty Nifty Auto Stocks":
    selected_stocks = nifty_auto_symbols
    st.sidebar.info("You have selected the Nifty Bank stock list.")
elif stock_universe == "Nifty Bank Stocks":
    selected_stocks = nifty_bank_symbols
    st.sidebar.info("You have selected the Nifty Bank stock list.")
else:
    selected_stocks = nifty_50_stocks
    st.sidebar.info("You have selected the Nifty 50 Stocks stock list.")


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
                st.subheader(f"Analysis Results for {stock_universe}")
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
