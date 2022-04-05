"""
 gets an http request object, converts to StringIO in-memory file-like object.
 reads through the in-memory file to find the first row of table data, and uses
 pandas read_table to read it into a dataframe
"""

from lxml import html
import time
import os
import re
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import numpy as np
import warnings
warnings.filterwarnings("ignore", "(?s).*MATPLOTLIBDATA.*", category=UserWarning)
def fxn():
    warnings.warn("deprecated", DeprecationWarning)
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')


def get_download_file(dtbase):
    try:
        pattern = r'.*\.(tmp|crdownload|csv)$'
        # dtbase = date.today().strftime('%Y-%m-%d %H:%M:%S')
        lastfile = None
        lastfilecsv = None
        re_pattern = re.compile(pattern, re.IGNORECASE)
        for root, dirs, files in os.walk(get_download_path()):
            for basename in files:
                if re_pattern.match(basename):
                    file = os.path.join(root, basename)
                    dtmod = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(file)))
                    if dtmod > dtbase:
                        dtbase = dtmod
                        lastfile = file
        if lastfile:
            # print(lastfile)
            ext = os.path.splitext(lastfile)[1]
            lastfilecsv = lastfile.replace(ext, '.csv')
            os.rename(lastfile, lastfilecsv)
        return lastfilecsv
    except Exception as e:
        print('error in get_download_file: ' + str(e))
        return os.path.join(get_download_path(), 'MansfieldDam_lakelevel.csv')


def import_gage_data(site_num, full_level=0):
    try:
        url = 'https://hydromet.lcra.org/home/GaugeDataList/?siteNumber=####&siteType=lakelevel'
        # replace values in the url using regex. don't need regex, but using to illustrate
        url = re.sub(r'####', site_num, url)
        # print(url)
        header = 'Lake Travis Lake Levels'

        # selenium
        options = Options()
        options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        options.add_experimental_option('w3c', False)
        browser = webdriver.Chrome(chrome_options=options)
        browser.get(url)
        action = 'get_excel'
        if action == 'get_data':
            innerHTML = browser.execute_script("return document.body.innerHTML")
            print(innerHTML)
            htmlElem = html.document_fromstring(innerHTML)
            # data = htmlElem.xpath('//*[@id="RecordsDetails"]/table/tbody/tr[1]/td[2]/text()')
            data = htmlElem.xpath('//*[@id="RecordsDetails"]/table/tbody/tr/td/text()')
            print(data)
            # print(htmlElem)
        else:
            dtnow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # print(dtnow)
            excel_button = browser.find_element_by_id('Excel')
            time.sleep(3)
            excel_button.click()
            time.sleep(3)
            download_file = get_download_file(dtnow)
            print(download_file)
            if download_file:
                # create df from download file, then delete the file
                df = pd.read_csv(download_file)
                os.remove(download_file)
                # get df columns and data types in order, group by date, define series
                df.columns = ['DateTime', 'Lake Level (ft MSL)', 'Tail (ft MSL)']
                latest_timestamp = df.iloc[[0]]['DateTime'].values[0]
                print(latest_timestamp)
                df.DateTime = pd.to_datetime(df.DateTime)
                df = df.sort_values(by=['DateTime'])
                # get last lake level value
                latest_lake_level = df.iloc[[-1]]['Lake Level (ft MSL)'].values[0]
                latest_vals = latest_timestamp, latest_lake_level
                df['Date'] = df['DateTime'].apply(lambda x: x.strftime('%Y-%m-%d'))
                grouped = df['Lake Level (ft MSL)'].groupby(df['Date'])
                sgrp = grouped.mean()
                # sgrp.to_csv('extra.csv')
                # get the values of the key (date) (this is a numpy ndarray) and convert to datetime
                # get_values deprecated ---> sgrpi = np.array(sgrp.keys().get_values(), dtype='datetime64[D]')
                sgrpi = np.array(sgrp.keys().array, dtype='datetime64[D]')
                # get the series values (ndarray)
                sgrpv = sgrp.values
                # create lake full y-values
                yfull = np.zeros(sgrpv.shape[0]) + full_level
                # return a tuple
                return sgrpi, sgrpv, yfull, header, latest_vals
    except:
        raise


def subplots(x, y, header, count, subplot_num, latest_vals=None, full=None, show_axis_labels=True,
             ylabel='Avg. Daily Elev. (ft)'):
    try:
        plt.figure(1)
        plt.subplot(count, 1, subplot_num)
        plt.plot(x, y, color='b', linestyle='-', linewidth=1.0, alpha=1.0, label=None)  # label='Elev (ft)'
        current_val = y[-1]
        start_val = y[0]
        ts = pd.to_datetime(x[0])
        dt_tm = datetime.datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second)
        ts2 = pd.to_datetime(x[-1])
        dt_tm2 = datetime.datetime(ts2.year, ts2.month, ts2.day, ts2.hour, ts2.minute, ts2.second)
        # str_annotation_start = '{:.1f}%\n{:%m/%d/%Y}'.format(start_val, dt_tm)
        if current_val > 200:
            str_annotation_current = 'Avg. today: {:.2f} ft.\nLast Reading:\n{}: {:.2f} ft.'.format(current_val,
                                                                                latest_vals[0], latest_vals[1])
        else:
            str_annotation_current = '{:.2f}%\n{:%m/%d/%Y}'.format(current_val, dt_tm2)
        # plt.annotate(str_annotation_start, xy=(x[0], start_val), xytext=(0.15, 0.5), textcoords='axes fraction',
        #              arrowprops=dict(arrowstyle='fancy', facecolor='gray'), bbox=dict(boxstyle="round", fc="w"))
        plt.annotate(str_annotation_current, xy=(x[-1], current_val-0.0), xytext=(0.75, 0.1), textcoords='axes fraction',
                    arrowprops=dict(arrowstyle='fancy', facecolor='lightgray'), rotation=0,
                    bbox=dict(boxstyle="round", fc="w"))
        ax = plt.gca()
        ax.autoscale(enable=True, axis='both', tight=True)
        ymax = plt.ylim()[1]
        ymin = plt.ylim()[0]
        plt.ylim(ymax=ymax+0.5, ymin=ymin-0.5)
        # don't know why, but plt.fill_between, with the way i'm calling it,
        #     causes ylim to change from a bad value to a good. if i call it twice, the 2nd call picks up the good value.
        plt.fill_between(x, y, y2=plt.ylim()[0], facecolor='b', alpha=0.0)
        plt.fill_between(x, y, y2=plt.ylim()[0], facecolor='b', alpha=0.3, label='conservation pool')
        if full is not None:
            plt.plot(x, full, color='b', linestyle='--', linewidth=1.0)
            if full.min() > 0:
                plt.fill_between(x, y, full, where=y > full, interpolate=True, facecolor='b', alpha=0.5, label='flood pool')
                plt.fill_between(x, y, full, where=y < full, interpolate=True, facecolor='lightcoral', alpha=0.5)
                plt.legend(loc='best', fontsize='x-small')
        plt.grid(b=True, which='both')
        if show_axis_labels:
            plt.xlabel('Date', fontsize='medium')
            plt.ylabel(ylabel, fontsize='small')
        plt.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')  # this changes the date format when hovering over the plot
        plt.figure(1).autofmt_xdate()  # this can have unintended behavior if the date ranges don't match
        plt.xticks(fontsize='small')
        plt.yticks(fontsize='small')
        plt.title(header, fontsize='medium', position=(0.5, 1.0))
    except:
        raise


def plot():
    try:
        # plt.show(block=False)
        plt.show()
    except:
        raise


if __name__ == "__main__":
    import_gage_data('3963', 1)
