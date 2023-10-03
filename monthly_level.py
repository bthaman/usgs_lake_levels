# %%
import pandas as pd

# %%
df = pd.read_csv('Travis.08154500.1943-2018.csv')
df
# %%
s = df.groupby(pd.PeriodIndex(df['Date'], freq='M'))['Level_ft'].mean()
s
dfm = pd.DataFrame(s)
dfm.to_csv('monthly_avg.csv')
dfm
# %%
dfmr = dfm.resample('M').mean()
dfmr
# %%
dfmr['Level_ft'] = dfmr['Level_ft'].interpolate()
dfmr.to_csv('monthly_avg_filledna.csv')
dfmr
# %%
count = len(dfmr[dfmr['Level_ft'] < 628.52].index)
count
# %%
count = (dfmr['Level_ft'] < 628.52).sum(axis=0)
count
# %%
pct = count / dfmr['Level_ft'].size
pct

# %%
count = (s<628.52).sum(axis=0)
count
# %%
s.size
# %%
pct = count/s.size
pct
# %%
import numpy as np
# %%
np.percentile(s, .06)
# %%
