# %%
import pandas as pd

# %%
df = pd.read_csv('Travis.08154500.1943-2018.csv')
df['Date'] = pd.to_datetime(df['Date'])
df= df.set_index('Date')
df

# %%
dfm = df.resample('M').mean()
dfm.to_csv('resampled_monthly.csv')
dfm

# %%
dfm = dfm.interpolate()
dfm.to_csv('resampled_monthly_filled.csv')
dfm

# %%
count = (dfm['Level_ft'] < 652.25).sum(axis=0)
count

# %%
pct = (count / dfm['Level_ft'].size) * 100
pct
# %%
