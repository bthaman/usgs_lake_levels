# %%
import pandas as pd

# %%
df = pd.read_csv('Travis.08154500.SANDBOX.csv')
df['Date'] = pd.to_datetime(df['Date'])
df= df.set_index('Date')
df

# %%
df_monthly = df[df.index < '2013-10-01']
df_monthly

# %%
df_daily = df[df.index >= '2013-10-01']
df_daily

# %%
df_monthly_resampled_filled = df_monthly.resample('M').mean().interpolate()
df_monthly_resampled_filled.to_csv('resampled_monthly_filled.csv')
df_monthly_resampled_filled

# %%
# df_daily_resampled_filled = df_daily.resample('D').interpolate(method='polynomial',order=3)  # need scipy for this
df_daily_resampled_filled = df_daily.resample('D').interpolate()
df_daily_resampled_filled.to_csv('resampled_daily_filled.csv')
df_daily_resampled_filled

# %%
# resample daily df to monthly
df_daily_to_monthly = df_daily_resampled_filled.resample('M').mean()
# put monthly and daily df's together
df_all = pd.concat([df_monthly_resampled_filled, df_daily_to_monthly])
df_all.to_csv('all_resampled.csv')
df_all
# %%
