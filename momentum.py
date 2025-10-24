MOMENTUM_DAYS = 10
signal_name = f'roc_{MOMENTUM_DAYS}d'
df = clean.sort_index(level=['Date', 'Ticker'])

df[signal_name] = df.groupby(level='Ticker')['open'].pct_change(MOMENTUM_DAYS) * 100

df['future_return'] = df.groupby(level='Ticker')['open'].pct_change(REBAL).shift(-REBAL)
df.dropna(inplace=True)
daily_returns = []
trade_dates = []

# Group by the 'Date' to iterate through each trading day
for date, daily_data in df.groupby(level='Date'):
    
    # a. Rank stocks for this day based on our momentum signal
    ranked_data = daily_data.sort_values(by=signal_name, ascending=False)
    
    # b. Determine how many stocks to buy
    num_stocks_to_buy = int(len(ranked_data) * (PORTFOLIO_PERCENTILE / 100.0))
    
    # Skip this day if the portfolio would be empty
    if num_stocks_to_buy == 0:
        continue
        
    # c. Select the top N% of stocks (our "winners" portfolio)
    winners_portfolio = ranked_data.head(num_stocks_to_buy)
    
    # d. Calculate the portfolio's return for the NEXT day
    # This is the equal-weighted average of the future returns of our selected stocks.
    portfolio_return = winners_portfolio['future_return'].mean()
    
    # f. Store the results for this day
    daily_returns.append(portfolio_return)
    trade_dates.append(date)

# Create a results DataFrame from the daily returns
results_df = pd.DataFrame({
    'Strategy': daily_returns,
}, index=pd.Index(trade_dates, name='Date'))

# Calculate cumulative returns (the growth of $1)
strategy_cumulative = (1 + results_df['Strategy']).cumprod()

# Calculate annualized returns (assuming 252 trading days a year)
annualized_strategy_return = (1 + results_df['Strategy'].mean())**252 - 1

print("--- Strategy Performance ---")
print(f"Total Cumulative Return: {strategy_cumulative.iloc[-1]:.2%}")
print(f"Annualized Return: {annualized_strategy_return:.2%}")

# Plot the equity curves
plt.style.use('seaborn-v0_8-whitegrid')
plt.figure(figsize=(14, 8))
strategy_cumulative.plot(label=f'Top {PORTFOLIO_PERCENTILE}% Momentum Strategy', legend=True, linewidth=2)
plt.title('Momentum Strategy')
plt.xlabel('Date')
plt.ylabel('Cumulative Returns (Growth of $1)')
plt.show()