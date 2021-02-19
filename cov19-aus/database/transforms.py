
import pandas as pd
import numpy as np

from scipy import signal
from scipy.fft import fft, ifft

# df = pd.read_sql("select * from wine_data", conn)
# df = df[['country', 'description', 'rating', 'price', 'province', 'title', 'variety', 'winery', 'color', 'varietyID']]

df = pd.read_csv("./database/COVID_Data_Hub.csv")
df = df.drop(columns="administrative_area_level_3")
df = df.drop(columns="administrative_area_level_1")

df = df.rename({'administrative_area_level_2': 'State'}, axis='columns')
df["region"] = df["State"].fillna("National")
df["state_abbrev"] = df["state_abbrev"].fillna("ALL")
df['date'] = pd.to_datetime(df['date'])
df['confirmed_per_capita'] = df['confirmed']/df['population']*1e6

# Removing data with less than 5 cases per 1M
df = df.loc[df['confirmed_per_capita'] >= 5]

# development time
start_date = df.groupby('region')['date'].min()
dev = []
for s in start_date.index:
    tmp = df.loc[df['region'] == s]['date'] - start_date[s]
    dev.append(tmp)
development = pd.concat(dev)
development = development.sort_index()
development = pd.DataFrame(development)
development = development.rename({'date': 'development'}, axis='columns')
development['development'] /= np.timedelta64(1, 'D')
df = pd.merge(df, development,left_index=True, right_index=True)

# Finding rate of change in confirmed cases
tmp = df[['date','region','confirmed']]
delta = []
for r in tmp.region.unique():
    index = tmp.loc[tmp['region'] == r].iloc[:-1].index
    confirmed_region_t0 = tmp.loc[tmp['region'] == r].iloc[:-1].reset_index()
    confirmed_region_t1 = tmp.loc[tmp['region'] == r].iloc[1:].reset_index()
    inc = (confirmed_region_t1['confirmed'] / confirmed_region_t0['confirmed']) - 1
    inc.index = index
    delta.append(inc)
delta = pd.concat(delta)
delta = delta.sort_index()
delta = pd.DataFrame(delta)
delta = delta.rename({'confirmed': '% increase'}, axis='columns')
df = pd.merge(df, delta,left_index=True, right_index=True)
df["log(% increase)"] = np.log(np.abs(df["% increase"])+1e-10)
df_reg = df.loc[df['% increase']!=0.0]

## Smoothing data
def lowpass_filter(data, cutoff, fs, order):
    normal_cutoff = cutoff / nyq
    # Get the filter coefficients
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    y = signal.filtfilt(b, a, data)
    return y.astype(np.float32)
fs = 1
cutoff = 0.017
nyq = 0.5 * fs
order = 3
log_inc_smooth = []
for r in df_reg['region'].unique():
    x = df_reg.loc[df_reg['region'] == r]['development'].values.reshape(-1, 1)
    y = df_reg.loc[df_reg['region'] == r]['log(% increase)'].values
    Y = lowpass_filter(y, cutoff, fs, order)

    index = df_reg.loc[df_reg['region'] == r].index
    log_inc_smooth.append(pd.Series(data=Y, index=index))

log_inc_smooth = pd.concat(log_inc_smooth)
log_inc_smooth = log_inc_smooth.sort_index()
log_inc_smooth = pd.DataFrame(log_inc_smooth)
log_inc_smooth = log_inc_smooth.rename({0: 'log_inc_smooth'}, axis='columns')
df_reg = pd.merge(df_reg, log_inc_smooth, left_index=True, right_index=True)

print(df_reg.isna().sum())




df_country = df.loc[df["administrative_area_level"] == 1]
# df_country = df_country.drop(
#     columns=["administrative_area_level", "administrative_area_level_1", "administrative_area_level_2", "id",
#              "state_abbrev"])

df_states = df.loc[df["administrative_area_level"] == 2]
# df_states = df_states.drop(columns=["administrative_area_level"])



