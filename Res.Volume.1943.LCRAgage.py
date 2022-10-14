"""
chromedriver.exe interfaces with Chrome. The driver must be in the
same directory as this .py file. 
It's specific to the Chrome version: get the correct
driver at https://chromedriver.chromium.org/downloads
2/10/2022   - Downloaded and installed the driver for Chrome 98
4/7/2022    - Downloaded and installed the driver for Chrome 100
6/3/2022    - Downloaded and installed the driver v. 102.0.5005.61 for Chrome 102
8/7/2022    - Downloaded and installed v. 104
10/14/2022  - Downloaded and installed v. 106.0.5249.61
"""

import lcra_gage_selenium as lcra
import pandas as pd
import numpy as np
import logger_handler
import datetime
import os
from os.path import join


logger_debug = logger_handler.setup_logger(name='lcrgage_debug', log_file=join(os.getcwd(),'lcrgage_debug.log'))
logger_exception = logger_handler.setup_logger(name='lcrgage_exception', log_file=join(os.getcwd(),'lcrgage_error.log'))
    
def plot_travis_volume_since_1943(days_before_today=365):
    try:
        df = pd.read_csv('Travis.08154500.1943-2018.csv', encoding='ISO-8859-1')
        logger_debug.info(join(os.getcwd(), 'Travis.08154500.1943-2018.csv') + ' read into DataFrame')
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        date2 = datetime.date(year=2050, month=12, day=31)
        # get the difference in days between today and the last day in the csv read above (1/5/2018)
        dt_today = datetime.date.today()
        dt_last = datetime.date(year=2018, month=5, day=23)
        # read elevation since 1/22/2018 and append to df
        x, y, full, header, latest_vals = lcra.import_gage_data(site_num='3963', full_level=681.0)
        logger_debug.info('gage data downloaded: header =' + header)
        # make a df
        df_new = pd.DataFrame({'Date': x, 'Level_ft': y}).set_index('Date')
        # df = df.append(df_new, ignore_index=True)
        df = df.append(df_new, ignore_index=False)
        # remove duplicate index rows
        df = df[~df.index.duplicated(keep='last')]
        # remove blank rows
        df = df.dropna(axis=0)
        # overwrite the source csv with updated data
        df.to_csv('Travis.08154500.1943-2018.csv')
        df = df.reset_index()
        # filter by date
        #   get start date
        date1 = dt_today - datetime.timedelta(days=days_before_today)
        logger_debug.info(str(date1) + ' to ' + str(dt_today))
        df = df[(df['Date'] >= pd.Timestamp(date1)) & (df['Date'] <= pd.Timestamp(date2))]
        # round to 2 decimals to match up with the stage-area-volume table
        df.Level_ft = df.Level_ft.round(2)
        x = df['Date'].values
        level_ft = df['Level_ft'].values
        header = 'Lake Travis (hydromet.lcra.org)'
        # read stage-storage
        df2 = pd.read_csv('stage.vol.travis.2dec.csv', encoding='ISO-8859-1')
        # chain together: merging the df's, setting the index to Date, and sorting by Date
        df3 = pd.merge(df, df2, left_on='Level_ft', right_on='ELEVATION').set_index('Date').sort_index()
        df3.to_csv('travis.csv', index=True)
        # pull out volume array and convert to % full
        pct_full = df3.VOL_ACFT.values / 1123478 * 100
        # make horizontal line at 100%
        pct100 = np.zeros(pct_full.shape[0]) + 100.0
        lcra.subplots(x, pct_full, header, 1, 1, latest_vals=None, full=pct100, show_axis_labels=True,
                    ylabel='Percent Full (%)')
        lcra.plot()

        level100 = np.zeros(level_ft.shape[0]) + 681.0
        lcra.subplots(x, level_ft, header, 1, 1, latest_vals=latest_vals, full=level100, show_axis_labels=True,
                    ylabel='Level (ft)')
        lcra.plot()
    except:
        logger_exception.exception('Error in plot_travis_volume_since_1943')
        raise


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        plot_travis_volume_since_1943(days_before_today=int(float(sys.argv[1])))
    else:
        try:
            dt_today = datetime.date.today()
            dt_first = datetime.date(year=1943, month=2, day=1)
            max_days = (dt_today - dt_first).days
            str_max_days = '\nEnter number of days to plot (max={:,.0f}): '.format(max_days)
            numdays = int(float(input(str_max_days)))
            if numdays < 1:
                raise ValueError('You entered {}. Number must be positive.'.format(numdays))
            plot_travis_volume_since_1943(days_before_today=numdays)
        except Exception as e:
            message = 'An error occurred. Error Type: {0}.\n\nError Args:\n{1}'.format(e.__class__.__name__, '\n'.join(e.args))
            print('\n' + message + '\n')
            # using 'input' keeps the command window open so the user can view the error
            input('press enter to exit...')
