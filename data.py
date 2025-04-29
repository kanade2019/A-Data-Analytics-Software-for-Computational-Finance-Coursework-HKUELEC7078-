import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import matplotlib.style as mplstyle

class Data():
    def __init__(self, stock_code=None):
        self.stock_code = stock_code
        self.data = None
        # mplstyle.use('fast')
        self.kline = plt.Figure(figsize=(10, 6))
        self.kline_ax = self.kline.add_subplot(111)
        self.kline_ax.set_position([0,0,1,1])
        self.kline_ax.grid()
        # self.kline_ax.xaxis.set_visible(False)
        # self.kline_ax.yaxis.set_visible(False)
        self.data_weekly = None
        self.data_monthly = None

    def load_data_csv(self):
        if self.stock_code is not None:
            self.data = pd.read_csv(f"datas/d_hk_txt/data/daily/hk/hkex stocks/{self.stock_code}.txt")
            self.data["<DATE>"] = pd.to_datetime(self.data["<DATE>"], format="%Y%m%d")
            self.data.sort_values(by=["<DATE>"], ascending=True, inplace=True)
            # self.__get_weekly_monthly_data()
            # self.__get_monthly_data()
        # self.__draw_kline()
        
    def __get_weekly_monthly_data(self):
        last_week = None
        last_month = None
        self.data_weekly = pd.DataFrame(columns=["<DATE>", "<OPEN>", "<CLOSE>", "<HIGH>", "<LOW>", "<VOL>"])
        self.data_monthly = pd.DataFrame(columns=["<DATE>", "<OPEN>", "<CLOSE>", "<HIGH>", "<LOW>", "<VOL>"])
        for index, row in self.data.iterrows():
            week = row["<DATE>"].isocalendar()[1]
            month = row["<DATE>"].month
            if last_week == week:
                self.data_weekly.iloc[-1, 2] = row["<CLOSE>"]
                self.data_weekly.iloc[-1, 3] = max(self.data_weekly.iloc[-1, 3], row["<HIGH>"])
                self.data_weekly.iloc[-1, 4] = min(self.data_weekly.iloc[-1, 4], row["<LOW>"])
                self.data_weekly.iloc[-1, 5] += row["<VOL>"]
            else:
                self.data_weekly = self.data_weekly.append({
                    "<DATE>": row["<DATE>"],
                    "<OPEN>": row["<OPEN>"],
                    "<CLOSE>": row["<CLOSE>"],
                    "<HIGH>": row["<HIGH>"],
                    "<LOW>": row["<LOW>"],
                    "<VOL>": row["<VOL>"]
                }, ignore_index=True)
                last_week = week
            if last_month == month:
                self.data_monthly.iloc[-1, 2] = row["<CLOSE>"]
                self.data_monthly.iloc[-1, 3] = max(self.data_monthly.iloc[-1, 3], row["<HIGH>"])
                self.data_monthly.iloc[-1, 4] = min(self.data_monthly.iloc[-1, 4], row["<LOW>"])
                self.data_monthly.iloc[-1, 5] += row["<VOL>"]
            else:
                self.data_monthly = self.data_monthly.append({
                    "<DATE>": row["<DATE>"],
                    "<OPEN>": row["<OPEN>"],
                    "<CLOSE>": row["<CLOSE>"],
                    "<HIGH>": row["<HIGH>"],
                    "<LOW>": row["<LOW>"],
                    "<VOL>": row["<VOL>"]
                }, ignore_index=True)
                last_month = month

    # def __draw_kline(self):
    #     if self.data is None:
    #         return
    #     self.kline_ax.clear()
        
    #     opens = self.data["<OPEN>"]
    #     closes = self.data["<CLOSE>"]
    #     highs = self.data["<HIGH>"]
    #     lows = self.data["<LOW>"]
    #     dates = self.data["<DATE>"]
    #     dates_num = mdates.date2num(dates)

    #     colors = ["green" if close >= open else "red" for open, close in zip(opens, closes)]
    #     self.kline_ax.vlines(dates, lows, highs, colors=colors, linewidth=1)

    #     width = 0.7

    #     for i, (date_num, open_val, close_val, color) in enumerate(zip(dates_num, opens, closes, colors)):
    #         bottom = min(open_val, close_val)
    #         height = abs(close_val - open_val)
            
    #         rect = plt.Rectangle(
    #             (date_num - width/2, bottom), width, height,
    #             color=color
    #         )

    #         self.kline_ax.add_patch(rect)
    #     self.kline_ax.grid()