import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px  # Import is present, but not being used. Clean up if not needed.

# Configuration
PAGE_TITLE = "Stock Analyzer"
PAGE_ICON = "📈"
LOADING_TEXT = "Analyzing Stocks..."

# --- Basic App Setup ---
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    menu_items=None,  # Hides the top-right menu button
)

# --- Session State Initialization ---
def initialize_session_state():
    if 'view_universe_rankings' not in st.session_state:
        st.session_state.view_universe_rankings = False
    if 'analyze_button_clicked' not in st.session_state:
        st.session_state.analyze_button_clicked = False

initialize_session_state()

# --- CSS Styling ---
def inject_custom_css():
    st.markdown(f"""
        <style>
            /* General Body and Background */
            body {{
                background: var(--bg-color);
                color: var(--text-color);
                font-family: 'Inter', sans-serif;
                transition: all 0.3s ease-in-out;
            }}

            /* Hide Header and Footer */
            header, footer {{visibility: hidden;}}

            /* Color Scheme (Light Mode) */
            @media (prefers-color-scheme: light) {{
                :root {{
                    --bg-color: #f4f4f7;
                    --text-color: #222;
                    --card-bg: rgba(255, 255, 255, 0.8);
                    --border-color: #ddd;
                    --primary-color: #0078FF;
                    --secondary-color: #0056B3;
                    --hover-bg: rgba(0, 120, 255, 0.1);
                    --shadow-color: rgba(0, 0, 0, 0.1);
                }}
            }}

            /* Color Scheme (Dark Mode) */
            @media (prefers-color-scheme: dark) {{
                :root {{
                    --bg-color: #0F172A;
                    --text-color: #E5E7EB;
                    --card-bg: rgba(30, 41, 59, 0.9);
                    --border-color: #1E293B;
                    --primary-color: #64FFDA;
                    --secondary-color: #4ECDC4;
                    --hover-bg: rgba(100, 255, 218, 0.1);
                    --shadow-color: rgba(0, 0, 0, 0.5);
                }}
            }}

            /* Centered Content */
            .center-div {{
                display: flex;
                text-align: center;
                justify-content: center;
                width: 100%;
            }}

            /* Loading Animation */
            .loading-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 200px;
                text-align: center;
                background: var(--card-bg);
                border-radius: 12px;
                box-shadow: 0 6px 16px var(--shadow-color);
                margin: 20px 0;
            }}
            .loading-text {{
                color: var(--primary-color);
                font-size: 1.2rem;
                margin-top: 20px;
            }}

            /* Responsive Adjustments */
            @media (max-width: 768px) {{
                /* Example adjustment for smaller screens */
                h1 {{
                    font-size: 2em;  /* Reduce title size on smaller screens */
                }}
            }}
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- Title and Subtitle ---
def display_header():
    st.markdown(f"""
        <h1 style='text-align: center;'>{PAGE_ICON} {PAGE_TITLE}</h1>
        <div style="text-align: center; font-size: 1.2rem; color: #c0c0c0;">
            Comprehensive momentum analysis with interactive visualizations.
        </div>
    """, unsafe_allow_html=True)

display_header()

# --- Stock Lists ---
STOCK_UNIVERSE = {
    "Nifty Midcap 50 Stocks": [
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
    ],
    "Nifty 50 Stocks": [
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
    ],
    "Nifty Smallcap 50 Stocks": [
        "360ONE.NS", "AARTIIND.NS", "ABREL.NS", "ARE&M.NS", "ANGELONE.NS", "APARINDS.NS", "ATUL.NS",
        "BSOFT.NS", "BLUESTARCO.NS", "BRIGADE.NS", "CESC.NS", "CASTROLIND.NS", "CDSL.NS", "CAMS.NS",
        "CROMPTON.NS", "CYIENT.NS", "FINCABLES.NS", "GLENMARK.NS", "GESHIP.NS", "GSPL.NS", "HFCL.NS",
        "HINDCOPPER.NS", "IIFL.NS", "INDIAMART.NS", "IEX.NS", "KPIL.NS", "KARURVYSYA.NS", "LAURUSLABS.NS",
        "MGL.NS", "MANAPPURAM.NS", "MCX.NS", "NATCOPHARM.NS", "NBCC.NS", "NCC.NS", "NH.NS", "NATIONALUM.NS",
        "NAVINFLUOR.NS", "PNBHOUSING.NS", "PVRINOX.NS", "PEL.NS", "PPLPHARMA.NS", "RBLBANK.NS", "RADICO.NS",
        "RKFORGE.NS", "REDINGTON.NS", "SONATSOFTW.NS", "TEJASNET.NS", "RAMCOCEM.NS", "ZEEL.NS", "ZENSARTECH.NS"
    ],
    "Nifty Auto Stocks": [
        "APOLLOTYRE.NS", "ASHOKLEY.NS", "BAJAJ-AUTO.NS", "BALKRISIND.NS", "BHARATFORG.NS",
        "BOSCHLTD.NS", "EICHERMOT.NS", "EXIDEIND.NS", "HEROMOTOCO.NS", "MRF.NS",
        "M&M.NS", "MARUTI.NS", "MOTHERSON.NS", "TVSMOTOR.NS", "TATAMOTORS.NS"
    ],
    "Nifty Bank Stocks": [
        "AUBANK.NS", "AXISBANK.NS", "BANKBARODA.NS", "CANBK.NS", "FEDERALBNK.NS",
        "HDFCBANK.NS", "ICICIBANK.NS", "IDFCFIRSTB.NS", "INDUSINDBK.NS", "KOTAKBANK.NS",
        "PNB.NS", "SBIN.NS"
    ]
}

# --- Sidebar ---
def create_sidebar():
    with st.sidebar:
        stock_universe_name = st.radio(
            "Select Stock Universe",
            list(STOCK_UNIVERSE.keys())
        )
        selected_stocks = STOCK_UNIVERSE[stock_universe_name]
        st.info(f"You have selected the {stock_universe_name} stock list.")

        if st.button("Stock Universes Ranks", key="universe_ranks_sidebar"):
            st.session_state.view_universe_rankings = True
            st.rerun()
    return stock_universe_name, selected_stocks

stock_universe_name, selected_stocks = create_sidebar()

# --- Main UI ---
def create_main_ui():
    col1, col2 = st.columns([0.75, 1])

    with col2:
        st.markdown('<div class="center-div">', unsafe_allow_html=True)
        if st.button("Analyze Stocks", key="analyze_stocks_main"):
            st.session_state.analyze_button_clicked = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

create_main_ui()

# --- Data Download ---
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

# --- Calculate Returns ---
def calculate_returns(df, period):
    if len(df) >= period:
        close_prices = df['Close'].values
        end_price = close_prices[-1]
        start_price = close_prices[-period]
        return ((end_price - start_price) / start_price).item()
    else:
        return np.nan

# --- Analyze Universe ---
def analyze_universe(universe_name, universe_symbols):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=400)
    results = []

    for ticker in universe_symbols:
        df = download_stock_data(ticker, start_date, end_date)
        if df.empty:
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
            "Momentum Score": momentum_score,
            "12-Month Return (%)": return_12M * 100 if pd.notna(return_12M) else np.nan,
            "6-Month Return (%)": return_6M * 100 if pd.notna(return_6M) else np.nan,
            "3-Month Return (%)": return_3M * 100 if pd.notna(return_3M) else np.nan,
            "Annualized Volatility": weekly_volatility

        })

    results_df = pd.DataFrame(results)
    avg_momentum_score = results_df["Momentum Score"].mean() if not results_df.empty else np.nan
    return results_df, avg_momentum_score

# --- Main Function ---
def main():
    universe_list = list(STOCK_UNIVERSE.items())

    # Handle universe rankings view
    if st.session_state.get('view_universe_rankings', False):
        st.subheader("Stock Universes Ranking by Average Momentum Score")

        universe_results = []
        progress_container = st.empty()
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            for idx, (name, symbols) in enumerate(universe_list):
                with progress_container:
                    status_text.text(f"🔄 Analyzing {name}...")
                    _, avg_momentum = analyze_universe(name, symbols)
                    universe_results.append({
                        "Stock Universe": name,
                        "Average Momentum Score": avg_momentum
                    })
                    progress = (idx + 1) / len(universe_list)
                    progress_bar.progress(progress)

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            progress_container.empty()

            # Display results
            if universe_results:
                universe_df = pd.DataFrame(universe_results)
                universe_df.sort_values(by="Average Momentum Score", ascending=False, inplace=True)

                st.dataframe(
                    universe_df.style
                    .format({'Average Momentum Score': '{:.4f}'})
                    .background_gradient(subset=['Average Momentum Score']),
                    height=400
                )

                # Display metrics
                st.subheader("Summary")
                col1, col2 = st.columns(2)
                with col1:
                    best_universe = universe_df.iloc[0]
                    st.metric(
                        "Highest Momentum Universe",
                        best_universe["Stock Universe"],
                        f"{best_universe['Average Momentum Score']:.4f}"
                    )
                with col2:
                    worst_universe = universe_df.iloc[-1]
                    st.metric(
                        "Lowest Momentum Universe",
                        worst_universe["Stock Universe"],
                        f"{worst_universe['Average Momentum Score']:.4f}"
                    )

            # Reset the view state
            st.session_state.view_universe_rankings = False

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.session_state.view_universe_rankings = False
        finally:
            st.session_state.analyze_button_clicked = False

    if st.session_state.get('analyze_button_clicked', False):
        st.subheader(f"Momentum Analysis for {stock_universe_name}")

        # Placeholder for analysis results
        analysis_placeholder = st.empty()

        try:
            # Show loading container
            with analysis_placeholder:
                st.markdown(f"""
                    <div class="loading-container">
                        <div class="lds-ripple"><div></div><div></div></div>
                        <p class="loading-text">{LOADING_TEXT}</p>
                    </div>
                """, unsafe_allow_html=True)

            # Perform analysis and display results
            results_df, _ = analyze_universe(stock_universe_name, selected_stocks)

            # Clear loading container
            analysis_placeholder.empty()

            if not results_df.empty:
                # Sort by Momentum Score
                results_df.sort_values(by="Momentum Score", ascending=False, inplace=True)

                # Format and display the dataframe
                styled_df = results_df.style.format({
                    "12-Month Return (%)": "{:.2f}%",
                    "6-Month Return (%)": "{:.2f}%",
                    "3-Month Return (%)": "{:.2f}%",
                    "Annualized Volatility": "{:.4f}",
                    "Momentum Score": "{:.4f}"
                }).background_gradient(subset=['Momentum Score'])

                st.dataframe(styled_df, use_container_width=True)
            else:
                st.warning("No data available for the selected stock universe.")

        except Exception as e:
            analysis_placeholder.empty()
            st.error(f"An error occurred: {str(e)}")
        finally:
            st.session_state.analyze_button_clicked = False

if __name__ == '__main__':
    main()
