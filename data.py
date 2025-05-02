import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import matplotlib.style as mplstyle
import time

class indicators():
    def __init__(self, data=None):
        self.data = data
        self.ma5 = None
        self.ma10 = None
        self.ma20 = None
        self.bollinger_bands = {"upper": None, "lower": None}
        self.macd = {'dif': None, 'dem': None, 'osc': None}

class Data():
    def __init__(self, stock_code=None):
        self.stock_code = stock_code
        self.data_daily = indicators()
        self.data_weekly = indicators()
        self.data_monthly = indicators()

    def load_data_csv(self):
        if self.stock_code is not None:
            self.data_daily.data = pd.read_csv(f"datas/d_hk_txt/data/daily/hk/hkex stocks/{self.stock_code}.txt")
            self.data_daily.data["<DATE>"] = pd.to_datetime(self.data_daily.data["<DATE>"], format="%Y%m%d")
            self.data_daily.data.sort_values(by=["<DATE>"], ascending=True, inplace=True)
            # print(self.data.head())
            self.__get_weekly_monthly_data()
            self.__get_moving_average('daily')
            self.__get_bollinger_bands('daily')
            self.__get_macd('daily')
            self.__get_moving_average('weekly')
            self.__get_bollinger_bands('weekly')
            self.__get_macd('weekly')
            self.__get_moving_average('monthly')
            self.__get_bollinger_bands('monthly')
            self.__get_macd('monthly')
    
    def __get_macd(self, type='daily'):
        if type == 'daily':
            if self.data_daily.data is None:
                return
            # 计算12日和26日指数移动平均线
            ema12 = self.data_daily.data['<CLOSE>'].ewm(span=12, adjust=False).mean()
            ema26 = self.data_daily.data['<CLOSE>'].ewm(span=26, adjust=False).mean()
            
            # 计算DIF线
            self.data_daily.macd['dif'] = ema12 - ema26
            
            # 计算DEA线
            self.data_daily.macd['dem'] = self.data_daily.macd['dif'].ewm(span=9, adjust=False).mean()
            
            # 计算MACD柱状图
            self.data_daily.macd['osc'] = (self.data_daily.macd['dif'] - self.data_daily.macd['dem'])
        elif type == 'weekly':
            if self.data_weekly.data is None:
                return
            # 计算12日和26日指数移动平均线
            ema12 = self.data_weekly.data['<CLOSE>'].ewm(span=12, adjust=False).mean()
            ema26 = self.data_weekly.data['<CLOSE>'].ewm(span=26, adjust=False).mean()
            
            # 计算DIF线
            self.data_weekly.macd['dif'] = ema12 - ema26
            
            # 计算DEA线
            self.data_weekly.macd['dem'] = self.data_weekly.macd['dif'].ewm(span=9, adjust=False).mean()
            
            # 计算MACD柱状图
            self.data_weekly.macd['osc'] = (self.data_weekly.macd['dif'] - self.data_weekly.macd['dem'])
        elif type == 'monthly':
            if self.data_monthly.data is None:
                return
            # 计算12日和26日指数移动平均线
            ema12 = self.data_monthly.data['<CLOSE>'].ewm(span=12, adjust=False).mean()
            ema26 = self.data_monthly.data['<CLOSE>'].ewm(span=26, adjust=False).mean()
            
            # 计算DIF线
            self.data_monthly.macd['dif'] = ema12 - ema26
            
            # 计算DEA线
            self.data_monthly.macd['dem'] = self.data_monthly.macd['dif'].ewm(span=9, adjust=False).mean()
            
            # 计算MACD柱状图
            self.data_monthly.macd['osc'] = (self.data_monthly.macd['dif'] - self.data_monthly.macd['dem'])

    def __get_bollinger_bands(self, type='daily'):
        if type == 'daily':
            if self.data_daily.data is None:
                return
            
            # 计算20日标准差
            std20 = self.data_daily.data['<CLOSE>'].rolling(window=20, closed='right').std()
            
            # 计算布林带上下轨
            self.data_daily.bollinger_bands['upper'] = self.data_daily.ma20 + (std20 * 2)
            self.data_daily.bollinger_bands['lower'] = self.data_daily.ma20 - (std20 * 2)
        elif type == 'weekly':
            if self.data_weekly.data is None:
                return
            
            # 计算20日标准差
            std20 = self.data_weekly.data['<CLOSE>'].rolling(window=20, closed='right').std()
            
            # 计算布林带上下轨
            self.data_weekly.bollinger_bands['upper'] = self.data_weekly.ma20 + (std20 * 2)
            self.data_weekly.bollinger_bands['lower'] = self.data_weekly.ma20 - (std20 * 2)
        elif type == 'monthly':
            if self.data_monthly.data is None:
                return
            
            # 计算20日标准差
            std20 = self.data_monthly.data['<CLOSE>'].rolling(window=20, closed='right').std()
            
            # 计算布林带上下轨
            self.data_monthly.bollinger_bands['upper'] = self.data_monthly.ma20 + (std20 * 2)
            self.data_monthly.bollinger_bands['lower'] = self.data_monthly.ma20 - (std20 * 2)

    def __get_moving_average(self, type='daily'):
        if type == 'daily':
            if self.data_daily.data is None:
                return
            
            # 计算移动平均线
            self.data_daily.ma5 = self.data_daily.data['<CLOSE>'].rolling(window=5, closed='right').mean()
            self.data_daily.ma10 = self.data_daily.data['<CLOSE>'].rolling(window=10, closed='right').mean()
            self.data_daily.ma20 = self.data_daily.data['<CLOSE>'].rolling(window=20, closed='right').mean()
        elif type == 'weekly':
            if self.data_weekly.data is None:
                return
            
            # 计算移动平均线
            self.data_weekly.ma5 = self.data_weekly.data['<CLOSE>'].rolling(window=5, closed='right').mean()
            self.data_weekly.ma10 = self.data_weekly.data['<CLOSE>'].rolling(window=10, closed='right').mean()
            self.data_weekly.ma20 = self.data_weekly.data['<CLOSE>'].rolling(window=20, closed='right').mean()
        elif type == 'monthly':
            if self.data_monthly.data is None:
                return
            
            # 计算移动平均线
            self.data_monthly.ma5 = self.data_monthly.data['<CLOSE>'].rolling(window=5, closed='right').mean()
            self.data_monthly.ma10 = self.data_monthly.data['<CLOSE>'].rolling(window=10, closed='right').mean()
            self.data_monthly.ma20 = self.data_monthly.data['<CLOSE>'].rolling(window=20, closed='right').mean()

    def __get_weekly_monthly_data(self):
        # start_time = time.time()
        
        if self.data_daily.data is None:
            return

        # 为数据添加 week 和 month 列
        self.data_daily.data['week'] = self.data_daily.data['<DATE>'].dt.isocalendar().week
        self.data_daily.data['year'] = self.data_daily.data['<DATE>'].dt.isocalendar().year
        self.data_daily.data['month'] = self.data_daily.data['<DATE>'].dt.month
        self.data_daily.data['year_month'] = self.data_daily.data['<DATE>'].dt.strftime('%Y-%m')

        # 按周分组汇总
        weekly_groups = self.data_daily.data.groupby(['year', 'week'])
        self.data_weekly.data = pd.DataFrame({
            '<DATE>': weekly_groups['<DATE>'].first(),
            '<OPEN>': weekly_groups['<OPEN>'].first(),
            '<CLOSE>': weekly_groups['<CLOSE>'].last(),
            '<HIGH>': weekly_groups['<HIGH>'].max(),
            '<LOW>': weekly_groups['<LOW>'].min(),
            '<VOL>': weekly_groups['<VOL>'].sum()
        }).reset_index(drop=True)

        # 按月分组汇总
        monthly_groups = self.data_daily.data.groupby('year_month')
        self.data_monthly.data = pd.DataFrame({
            '<DATE>': monthly_groups['<DATE>'].first(),
            '<OPEN>': monthly_groups['<OPEN>'].first(),
            '<CLOSE>': monthly_groups['<CLOSE>'].last(),
            '<HIGH>': monthly_groups['<HIGH>'].max(),
            '<LOW>': monthly_groups['<LOW>'].min(),
            '<VOL>': monthly_groups['<VOL>'].sum()
        }).reset_index(drop=True)