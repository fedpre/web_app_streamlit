import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import yfinance as yf

# Format the header of the web app
st.title('S&P 500 App')
st.write("""" 
    This app retrieves the list of the **S&P 500** (from Wikipedia) and its corresponding **stock closing price** (year-to-date)!
    * **Python libraries:** base64, pandas, streamlit, matplotlib, yfinance
    * **Data source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('User Input Features')

# Web scraping of S&P 500 data
@st.cache
def load_data(url, selected_table):
    html = pd.read_html(url, header = 0)
    df = html[selected_table] # Select the first table
    return df

df = load_data('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', 0)
sector = df.groupby('GICS Sector')


# Sidebar - Sector selection
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Sidebar - Symbol selection
sorted_symbol_unique = sorted(df['Symbol'].unique())
selected_symbol = st.sidebar.multiselect('Symbol', sorted_symbol_unique, sorted_symbol_unique)

# Filtering data
df_selected_sector_symbol = df[(df['GICS Sector']).isin(selected_sector) & (df['Symbol'].isin(selected_symbol))]

st.header('Display Companies in Selected Sector')
st.write('Data Dimension: ' + str(df_selected_sector_symbol.shape[0]) + ' rows and ' + str(df_selected_sector_symbol.shape[1]) + ' columns.')
st.dataframe(df_selected_sector_symbol)

# Download S&P500 data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()# strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="SP500.csv">Download CSV File</a>'
    return href
st.markdown(filedownload(df_selected_sector_symbol), unsafe_allow_html=True)

# https://pypi.org/project/yfinance/
data = yf.download(
    tickers = list(df_selected_sector_symbol[:10].Symbol),
    period = "ytd",
    interval = "1d",
    group_by = 'ticker',
    auto_adjust=True,
    prepost=True,
    threads=True, 
    proxy=None
)

# Plot closing price of Query Symbol
def price_plot(symbol):
    df = pd.DataFrame(data[symbol].Close)
    df['Date'] = df.index
    plt.fill_between(df.Date, df.Close, color="skyblue", alpha=0.3)
    plt.plot(df.Date, df.Close, color="skyblue", alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('closing Price', fontweight='bold')
    st.set_option('deprecation.showPyplotGlobalUse', False)
    return st.pyplot()

num_company = st.sidebar.slider('Number of companies', 1, 10)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for i in list(df_selected_sector_symbol.Symbol)[:num_company]:
        price_plot(i)
   

# Can I make a sidebar that allows me to choose just one company to show the graph?