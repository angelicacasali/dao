import streamlit as st
import pandas as pd
import yfinance as yf

# Define the indexes and their tickers
indexes = {
    "Dow Jones": ["AAPL", "MSFT", "GOOGL"],  # Replace with actual tickers
    "Nasdaq 100": ["AAPL", "MSFT", "GOOGL"],
    "S&P 500": ["AAPL", "MSFT", "GOOGL"],
    "Euro Stoxx 50": ["AAPL", "MSFT", "GOOGL"],
    "CAC 40": ["AAPL", "MSFT", "GOOGL"],
    "FTSE 100": ["AAPL", "MSFT", "GOOGL"],
    "IBEX 35": ["AAPL", "MSFT", "GOOGL"],
    "DAX": ["AAPL", "MSFT", "GOOGL"]
}

# Function to get stock info
def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "P/E Ratio": info.get('forwardPE'),
        "Dividend Yield": info.get('dividendYield') * 100 if info.get('dividendYield') else None,
        "Market Cap": info.get('marketCap'),
        "52 Week High": info.get('fiftyTwoWeekHigh'),
        "52 Week Low": info.get('fiftyTwoWeekLow'),
        "Last Price": stock.history(period='1d')['Close'][-1]
    }

# Function to calculate additional metrics
def calculate_additional_metrics(data):
    def calculate_catch_up(row):
        try:
            last_price = row['Last Price']
            week_low = row['52 Week Low']
            week_high = row['52 Week High']
            if last_price is not None and week_low is not None and week_high is not None and (last_price - week_low) != 0:
                return ((week_high - week_low) / (last_price - week_low)) * 100
            else:
                return None
        except Exception as e:
            print(f"Error calculating Catch-Up for row {row.name}: {e}")
            return None

    data['Catch-Up'] = data.apply(calculate_catch_up, axis=1)
    data['Peak-to-Valley'] = data.apply(lambda row: (row.max() - row.min()) / row.max(), axis=1)
    return data

# Function to rank shares
def rank_shares(data, criteria):
    ranked_data = data.sort_values(by=criteria, ascending=False)
    return ranked_data

# Function to filter shares
def filter_shares(data, index=None, country=None, sector=None):
    # Dummy filter implementation
    filtered_data = data
    return filtered_data

# DAO calculations
def calculate_dao(data):
    highest_dao1 = ((data['P/E Ratio'] * data['Catch-Up']) / data['Dividend Yield']).max()
    data['DAO_1'] = (1 - (data['P/E Ratio'] * data['Catch-Up'] / data['Dividend Yield']) / highest_dao1) * 100
    data['DAO_2'] = data['P/E Ratio'] * data['Catch-Up'] * data['Market Cap']
    return data

# Streamlit app
st.title('Share Analysis')

# Sidebar for user inputs
st.sidebar.header('Filter Options')
selected_index = st.sidebar.selectbox('Select Index', options=list(indexes.keys()))
selected_criteria = st.sidebar.selectbox('Select Criteria', options=['P/E Ratio', 'Market Cap', 'Dividend Yield', 'Catch-Up', 'Peak-to-Valley'])

# Get stock data
tickers = indexes[selected_index]
stock_info = {ticker: get_stock_info(ticker) for ticker in tickers}
info_df = pd.DataFrame(stock_info).T

# Filter shares
filtered_shares = filter_shares(info_df, index=selected_index)

# Calculate additional metrics
filtered_shares = calculate_additional_metrics(filtered_shares)

# Calculate DAO metrics
filtered_shares = calculate_dao(filtered_shares)

# Rank shares
ranked_shares = rank_shares(filtered_shares, selected_criteria)

# Display top and low ten shares
st.subheader('Top 10 Shares')
st.dataframe(ranked_shares.head(10))

st.subheader('Low 10 Shares')
st.dataframe(ranked_shares.tail(10))

# Display full list with sorting
st.subheader('All Shares (Sortable)')
st.dataframe(ranked_shares)
