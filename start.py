import numpy as np
import pandas as pd


def manual_data(start: str, end: str, src: str) -> pd.DataFrame:
    """Get data from """
    data_df = pd.read_csv(src, index_col=0)#, parse_dates=["Time"])

    freq='15min'
    intervals_per_hour = 4

    # temp bandaid to deal with substation data
    # data_df.index = pd.to_datetime(data_df.index, utc=True)#, format='mixed')

    # NOTE we'll adopt NEM time such that timestamps indicate the end of a 5 min interval
    # Starting with 15 min data we'll set the time index to start at the beninning of this 
    # period and then trim off the first 5 min after ffill()
    tmp = pd.date_range(start=pd.to_datetime("2021-7-1 00:00").tz_localize("UTC"), 
                        end=pd.to_datetime("2023-06-30 23:45").tz_localize("UTC"), 
                        freq=freq)
    data_df.index = tmp

    # data_df = data_df.resample("5min").ffill()#.reset_index()

    # data_df.rename(columns={data_df.columns[0]: "network_load"}, inplace=True)

    new_df = data_df.loc[start:end][1:]

    # new_df.reset_index(inplace=True)

    # temp bandaid to deal with substation data
    # new_df = new_df.rename(columns={data_df.index.name:'settlementdate'})
    # new_df = new_df.rename(columns={'index':'settlementdate'})
    return new_df, intervals_per_hour

zs_df, intervals_per_hour = manual_data("2022-1-1 00:00", "2022-2-1 00:00",
    src = "data/evoenergy-zone-substation-report-2021-23.csv")


for day in range(1,2):
    current_day_zs_df = zs_df['Belconnen'][zs_df.index.dayofyear == day]
    # current_day_zs_df.index = current_day_zs_df.index.strftime('%H:%M')
    # current_day_zs_df.index = current_day_zs_df.index.time
    # time_interval = current_day_zs_df.index[1] - current_day_zs_df.index[0]
    print(current_day_zs_df)
    # print(repr(current_day_zs_df.index))

    demand_growth = 0.05 # as a growth rate

    current_hw_MWh_per_day = 10 # will be temperature dependent
    current_hw_MW = current_hw_MWh_per_day/24
        
    curent_day_zs_sans_hw = current_day_zs_df - current_hw_MW

    future_zs_sans_hw = curent_day_zs_sans_hw*(1+demand_growth)

    forecast_hw_heatpump_MWh = 100
    forecast_hw_resist_MWh = 10
    timed_hw_start = 9
    timed_hw_end = 16
    time_mask = (current_day_zs_df.index.hour >= timed_hw_start) & \
            (current_day_zs_df.index.hour < timed_hw_end)
    timed_hw_df = pd.Series(index=current_day_zs_df.index, data = 0)
    # timed_hw_df[timed_hw_df.index.hour > timed_hw_start & timed_hw_df.index.hour < timed_hw_end] == 1
    # print(timed_hw_df.between_time(timed_hw_start,timed_hw_end))
    timed_hw_df[time_mask] = 1
    forecast_hw_MW = (forecast_hw_heatpump_MWh + forecast_hw_resist_MWh) / \
                        (np.sum(timed_hw_df)/intervals_per_hour)
    timed_hw_df[time_mask] = forecast_hw_MW
    print(timed_hw_df)

    future_zs_with_hw = future_zs_sans_hw + timed_hw_df

    print(future_zs_with_hw)


