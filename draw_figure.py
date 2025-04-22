import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.collections import PatchCollection
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from data import Data

class Figures(tk.Frame):
    def __init__(self, master, stock_code=None):
        super().__init__(master)
        self.master = master
        self.stock_code = stock_code
        self.start_index = None
        self.end_index = None
        self.data = Data()

        self.loading_mask = tk.Frame(self, background="gray")
        self.loading_text = ttk.Label(self.loading_mask, text="Loading...", background="gray", foreground='white', font=("Arial", 20), justify='center')
        # self.loading_mask.lift()
        self.loading_mask.place_forget()
        self.loading_text.place(relx=0.5, rely=0.5, anchor="center")
        
        self.frame_Kline = FigureCanvasTkAgg(self.data.kline, master=self)
        self.frame_Kline.get_tk_widget().place(relx=0, rely=0, relwidth=1, relheight=1, anchor="nw")
        self.frame_Kline.draw()

        # self.fig = plt.Figure(figsize=(25, 28), dpi=100, facecolor="white")
        # self.fig.subplots_adjust(left=0.075, right=0.975, top=0.95, bottom=0.175, hspace=0.4, wspace=0.4)
        # self.frame_Kline.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_Kline)
        # self.frame_Kline.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # self.ax = self.fig.add_subplot(111)
        # self.ax.set_title("Stock Price")
        # self.ax.tick_params(axis='x', rotation=45)
        # self.ax.grid()

        # # 存储用于重绘的对象
        # self.line = None
        # self.patches = []

        # self.dragging = False
        # self.drag_start_x = None
        
        self.__bind_events()
    def show_mask(self):
        self.loading_mask.place(relx=0, rely=0, relwidth=1, relheight=1, anchor="nw")
        self.loading_mask.lift()

    def hide_mask(self):
        self.loading_mask.place_forget()

    def new_data(self):
        if self.stock_code is None:
            return
        if self.frame_Kline is not None:
            self.frame_Kline.get_tk_widget().delete('ALL')
        self.end_index = self.data.data['<DATE>'].max()
        self.start_index = self.end_index - pd.Timedelta(days=30)
        
        
        # draw matplotlib figure in canvas
        # self.frame_Kline = FigureCanvasTkAgg(self.data.kline, master=self)
        # self.frame_Kline.figure = self.data.kline
        self.frame_Kline.get_tk_widget().place(relx=0, rely=0, relwidth=1, relheight=1, anchor="nw")
        self.__refresh_figure()
        self.loading_mask.place_forget()

    def __bind_events(self):
        self.frame_Kline.get_tk_widget().bind("<MouseWheel>", self.__scroll_event)
        # self.frame_Kline.canvas.get_tk_widget().bind("<Button-1>", self.__click_event)
        # self.frame_Kline.canvas.get_tk_widget().bind("<B1-Motion>", self.__drag_event)
        # self.frame_Kline.canvas.get_tk_widget().bind("<ButtonRelease-1>", self.__release_event)
        # self.frame_Kline.canvas.get_tk_widget().bind("<Motion>", self.__motion_event)

    # def __motion_event(self, event):
    #     if self.data is None or len(self.data) == 0:
    #         return
        
    #     x = (event.x - 0.075 * self.frame_Kline.winfo_width()) / (0.9 * self.frame_Kline.winfo_width())

    #     x_index = int(self.end_index - x * (self.end_index - self.start_index + 1))
    #     if x_index < 0 or x_index >= len(self.data):
    #         return
        
        # print(self.data['Date'][x_index], self.data['Price'][x_index],
        #       self.data['Open'][x_index],
        #       self.data['High'][x_index], self.data['Low'][x_index])

    # def __click_event(self, event):
    #     self.dragging = True
    #     self.drag_start_x = event.x
    
    # def __drag_event(self, event):
    #     if self.dragging:
    #         dx = (event.x - self.drag_start_x) / (0.9 * self.frame_Kline.winfo_width())
    #         move_index = dx * (self.end_index - self.start_index)
    #         next_start_index = self.start_index + move_index
    #         next_end_index = self.end_index + move_index
    #         if next_start_index >= 0 and \
    #             next_start_index < len(self.data) and \
    #             next_end_index > 0 and \
    #             next_end_index <= len(self.data):
    #             self.start_index = next_start_index
    #             self.end_index = next_end_index
    #             self.Draw()
    #             self.drag_start_x = event.x
        
    
    # def __release_event(self, event):
    #     self.dragging = False
    #     self.drag_start_x = None
    #     self.Draw()

    def __scroll_event(self, event):
        """Scroll event to zoom in/out the figure."""
        if self.data.data is None:
            return
        x = event.x / self.frame_Kline.winfo_width()
        center_day = self.start_index + pd.Timedelta(days=x * (self.end_index - self.start_index).days)
        
        # get real mouse position
        # x = event.x / self.frame_Kline.winfo_width()
        # print(x, y)

        if event.delta < 0:
            self.start_index = min(self.start_index + pd.Timedelta(days=1), self.end_index - pd.Timedelta(days=1))
            self.end_index = max(self.start_index + pd.Timedelta(days=1), self.end_index - pd.Timedelta(days=1))
        else:
            self.start_index = max(self.start_index - pd.Timedelta(days=1), self.data.data['<DATE>'].min())
            self.end_index = min(self.end_index - pd.Timedelta(days=1), self.data.data['<DATE>'].max())
        self.__refresh_figure()

    def __refresh_figure(self):
        minmax  = [self.data.data[(self.data.data['<DATE>'] >= self.start_index) & (self.data.data['<DATE>'] <= self.end_index)]['<LOW>'].min(), 
                    self.data.data[(self.data.data['<DATE>'] >= self.start_index) & (self.data.data['<DATE>'] <= self.end_index)]['<HIGH>'].max()]
        self.data.kline_ax.set_xlim(self.start_index-pd.Timedelta(days=1), self.end_index+pd.Timedelta(days=1))
        self.data.kline_ax.set_ylim(minmax[0] - 0.1*(minmax[1] - minmax[0]), minmax[1] + 0.1*(minmax[1] - minmax[0]))
        
        self.frame_Kline.draw()
    # def load_data_csv(self, ticker_code):
    #     """Load data into the figure."""
    #     """Date","Price","Open","High","Low","Vol.","Change %"""
    #     self.data = pd.read_csv(f"datas/d_hk_txt/data/daily/hk/hkex stocks/{ticker_code}.txt")
    #     self.start_index = 0.0
    #     self.end_index = float(len(self.data))

    # def Draw(self):
    #     """Draw using more efficient methods."""
    #     if self.data is None:
    #         return
                
    #     self.ax.clear()
        
    #     # 设置基本属性
    #     # self.ax.set_title("Stock Price")
    #     self.ax.tick_params(axis='x', rotation=45)
    #     self.ax.grid()
        
    #     # 计算数据范围
    #     start_index = int(self.start_index)
    #     end_index = max(start_index + 2, int(self.end_index))
        
    #     # 提取需要显示的数据
    #     data_slice = self.data.iloc[start_index:end_index]
    #     dates = pd.to_datetime(data_slice["<DATE>"])
        
    #     # 使用更高效的方式绘制K线图 - 批量处理而不是逐条绘制
    #     # 准备K线数据
    #     opens = data_slice["<OPEN>"]
    #     closes = data_slice["<CLOSE>"]
    #     highs = data_slice["<HIGH>"]
    #     lows = data_slice["<LOW>"]
        
    #     # 计算颜色
    #     colors = ["green" if close >= open else "red" for open, close in zip(opens, closes)]
        
    #     # 批量绘制线图部分
    #     self.ax.vlines(dates, lows, highs, colors=colors, linewidth=1)
        
    #     # 将日期转换为matplotlib可处理的浮点数
    #     dates_num = mdates.date2num(dates)
        
    #     # 计算矩形参数 - 使用数值型日期
    #     width = 0.7  # 以天为单位的宽度
        
    #     green_rects = []
    #     red_rects = []
        
    #     for i, (date_num, open_val, close_val, color) in enumerate(zip(dates_num, opens, closes, colors)):
    #         # 确定矩形位置和大小
    #         bottom = min(open_val, close_val)
    #         height = abs(close_val - open_val)
            
    #         # 创建矩形
    #         rect = mpatches.Rectangle(
    #             (date_num - width/2, bottom), width, height
    #         )
            
    #         # 根据颜色分类
    #         if color == "green":
    #             green_rects.append(rect)
    #         else:
    #             red_rects.append(rect)
        
    #     # 分颜色批量添加矩形
    #     if green_rects:
    #         self.ax.add_collection(PatchCollection(green_rects, facecolor="green", edgecolor="black", linewidth=0.5))
    #     if red_rects:
    #         self.ax.add_collection(PatchCollection(red_rects, facecolor="red", edgecolor="black", linewidth=0.5))
        
    #     # 设置坐标轴范围
    #     if len(dates) > 0:
    #         self.ax.set_xlim(dates.min() - pd.Timedelta(days=1), dates.max() + pd.Timedelta(days=1))
    #     self.ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        
    #     # 更新画布
    #     self.frame_Kline.canvas.draw()