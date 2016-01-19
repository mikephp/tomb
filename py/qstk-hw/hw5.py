#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def get_close_price(dt_start, dt_end, ls_symbols):
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    c_dataobj = da.DataAccess('Yahoo')
    ls_keys = ['close']
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    # Filling the data for NAN
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        # d_data[s_key] = d_data[s_key].fillna(1.0)  # never exec.?

    na_price = d_data['close'].values
    df_price = pd.DataFrame(
        na_price, index=ldt_timestamps, columns=ls_symbols)
    return df_price


def test_data():
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)
    df_price = get_close_price(
        dt_start, dt_end, ['AAPL', 'GOOG', 'IBM', 'MSFT', 'VZ'])
    return df_price


def bollinger_band(df_price, lookback=20, times=1, plot=False):
    rmean_df = pd.rolling_mean(df_price, 20)
    rstd_df = pd.rolling_std(df_price, 20)
    ratio = (df_price - rmean_df) / (times * rstd_df)
    higher = rmean_df + times * rstd_df
    lower = rmean_df - times * rstd_df
    if plot:
        for sym in df_price.columns:
            plt.clf()
            fig, (ax1, ax2) = plt.subplots(2, 1)
            ax1.plot(df_price[sym])
            ax1.plot(lower[sym], color='#a0a0a0')
            ax1.plot(higher[sym], color='#a0a0a0')
            ax1.fill_between(np.arange(len(lower)), lower[
                             sym], higher[sym], facecolor='#e0e0e0', alpha=0.5)
            ax1.set_ylabel('Adjusted Close')

            ax2.plot(ratio[sym])
            ymin, ymax = ax2.get_ylim()
            ax2.axvspan(0, len(lower) - 1, ymin=(-1.0 - ymin) / (ymax - ymin),
                        ymax=(1.0 - ymin) / (ymax - ymin), facecolor='#e0e0e0', alpha=0.5)
            ax2.set_ylabel('Bollinger Feature')

            def plot_peak(ax, ro):
                sz = ro.shape[0]
                peaks = []
                for (idx, r) in enumerate(ro):
                    peak = False
                    if r >= 1.0:
                        if (idx > 0 and r > ro[idx - 1]) and \
                                (idx < (sz - 1) and r > ro[idx + 1]):
                            peak = True
                    if r <= -1.0:
                        if (idx > 0 and r < ro[idx - 1]) and \
                                (idx < (sz - 1) and r < ro[idx + 1]):
                            peak = True
                    if peak:
                        # local peak
                        peaks.append((idx, r))
                # get global peaks.
                for (i, p) in enumerate(peaks):
                    ax.axvline(p[0], color='g')
            plot_peak(ax1, ratio[sym])
            plot_peak(ax2, ratio[sym])
            plt.savefig('hw5-%s.pdf' % (sym), format='pdf')
    return (higher, lower, ratio)

if __name__ == '__main__':
    df_price = test_data()
    (h, l, r) = bollinger_band(df_price, times=1, plot=True)
    print r[80:120]
