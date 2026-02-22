#Part 1: Fetch data from yahoo finance and clean data
import yfinance as yf
import pandas as pd
import numpy as np

#ticker of 3 companies in the UK (HSBC, BP, Astra Zeneca) and 2 companies in the US (JPMorgan Chase, Apple) for diversification.
#Benchmark: S&P 500 and FTSE 100

tickers = ['AAPL', 'JPM', 'HSBA.L','AZN.L', 'BP.L', '^GSPC', '^FTSE']

#take data of 5 most recent years
df = yf.download (tickers, period ='3y', interval = '1d')['Close']

#insert column title
df.columns = ['Apple_US','JPMorgan_US','HSBC_UK','AstraZeneca_UK','BP_UK','S&P_500','FTSE_100']

#Check for missing value
print("Total number of missing values: ")
print(df.isnull().sum())

#Fill missing cells with price of previous day
df = df.ffill().dropna()

#Check for prices of 5 latest days
df.tail()

#Part 2: Performance table

#Daily returns
daily_ret = df.pct_change().dropna()

#Cumulative returns
cumulative_ret = (1 + daily_ret).cumprod()



#Compound annual growth rate
num_years = (df.index[-1] - df.index[0]).days/365
total_ret = (cumulative_ret.iloc[-1] - 1)
annual_ret = ((cumulative_ret.iloc[-1]) ** (1/num_years) - 1)


#Volatility: standard deviation
annual_vol = daily_ret.std() * np.sqrt(252)

#Take 10 year US treasury bond as riskfree rate
tnx_10_closest_day = yf.Ticker ("^TNX").history (period = '10d')
rfr = tnx_10_closest_day['Close'].iloc[-1]/100


#Sharpe ratio
sharpe_ratio = (annual_ret - rfr)/annual_vol



#Maximum drawdown
peak = cumulative_ret.cummax()
max_drawdown = (cumulative_ret/peak - 1).min()

#Calmar ratio

calmar_ratio = (annual_ret/abs(max_drawdown))

#Calculate performance table and sort

perf_tab = pd.DataFrame ({'Total return ': total_ret, 'Annual return': annual_ret, 'Annual volatility': annual_vol,
                          'Sharpe ratio': sharpe_ratio,
                          'Max drawdown ': max_drawdown,
                          'Calmar ratio':calmar_ratio})
perf_tab = perf_tab.round (2)
print(perf_tab.sort_values(by = 'Sharpe ratio',ascending = False))

#Part 3: Data visualisation
#Cumulative returns diagram
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('ggplot')
plt.figure(figsize=(10,5))

for column in cumulative_ret.columns:
  plt.plot(cumulative_ret.index,cumulative_ret[column], label = column)

plt.title('Cumulative Returns', fontsize = 10)
plt.xlabel('Date', fontsize = 10)
plt.ylabel('Growth', fontsize = 10)
plt.legend(loc='upper left', fontsize = 8)
plt.tick_params(axis='both', labelsize=8)
plt.savefig('cumulative_returns.png')
plt.show()

#Maximum drawdown diagram for BP_UK
plt.figure (figsize = (10,5))

target_stock = cumulative_ret.columns[4]
dd_to_plot = (cumulative_ret[target_stock] / cumulative_ret[target_stock].cummax() - 1)

plt.fill_between(dd_to_plot.index, dd_to_plot * 100, 0, color='red', alpha=0.3)
plt.plot(dd_to_plot.index, dd_to_plot * 100, color='red', linewidth=1)
plt.title(f'Drawdown of {target_stock}', color='darkred', fontsize=10)
plt.ylabel('Drawdown percentage (%)')
plt.axhline(0, color='black', linestyle='-', linewidth=1)
plt.tick_params(axis='both', labelsize=8)
plt.savefig('max_drawdown.png')
plt.show()

#Return distribution

plt.figure(figsize=(10, 5))
sns.histplot(daily_ret[target_stock], kde=True, bins=50, color='royalblue')
plt.axvline(daily_ret[target_stock].mean(), color='orange', linestyle='--', label='Mean Return')
plt.axvline(0, color='red', linestyle='-', linewidth=1)
plt.title(f'Daily return distribution of {target_stock}', fontsize=10)
plt.xlabel('Daily returns',fontsize = 8)
plt.ylabel('Frequency', fontsize = 8)
plt.tick_params(axis='both', labelsize = 10)
plt.legend(loc='upper left', fontsize = 10)
plt.savefig('daily_return_dist.png')
plt.show()