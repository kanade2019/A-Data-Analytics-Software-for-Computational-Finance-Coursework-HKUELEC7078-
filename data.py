import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import matplotlib.style as mplstyle
import time

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
            self.__get_weekly_monthly_data()
            # self.__get_monthly_data()
        # self.__draw_kline()
        
    def __get_weekly_monthly_data(self):
        # start_time = time.time()
        
        if self.data is None:
            return

        # 为数据添加 week 和 month 列
        self.data['week'] = self.data['<DATE>'].dt.isocalendar().week
        self.data['year'] = self.data['<DATE>'].dt.isocalendar().year
        self.data['month'] = self.data['<DATE>'].dt.month
        self.data['year_month'] = self.data['<DATE>'].dt.strftime('%Y-%m')

        # 按周分组汇总
        weekly_groups = self.data.groupby(['year', 'week'])
        self.data_weekly = pd.DataFrame({
            '<DATE>': weekly_groups['<DATE>'].first(),
            '<OPEN>': weekly_groups['<OPEN>'].first(),
            '<CLOSE>': weekly_groups['<CLOSE>'].last(),
            '<HIGH>': weekly_groups['<HIGH>'].max(),
            '<LOW>': weekly_groups['<LOW>'].min(),
            '<VOL>': weekly_groups['<VOL>'].sum()
        }).reset_index(drop=True)

        # 按月分组汇总
        monthly_groups = self.data.groupby('year_month')
        self.data_monthly = pd.DataFrame({
            '<DATE>': monthly_groups['<DATE>'].first(),
            '<OPEN>': monthly_groups['<OPEN>'].first(),
            '<CLOSE>': monthly_groups['<CLOSE>'].last(),
            '<HIGH>': monthly_groups['<HIGH>'].max(),
            '<LOW>': monthly_groups['<LOW>'].min(),
            '<VOL>': monthly_groups['<VOL>'].sum()
        }).reset_index(drop=True)
        
        # print(f"Weekly/Monthly data processing time: {time.time() - start_time:.2f} seconds")
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