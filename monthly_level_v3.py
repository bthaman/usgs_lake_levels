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
