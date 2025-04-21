import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.collections import PatchCollection
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

class DrawFigure:
    def __init__(self, frame_figure):
        self.frame_figure = frame_figure
        self.start_index = None
        self.end_index = None
        self.data = None
        
        # 创建一次Figure对象
        self.fig = plt.Figure(figsize=(25, 28), dpi=100, facecolor="white")
        self.fig.subplots_adjust(left=0.075, right=0.975, top=0.95, bottom=0.175, hspace=0.4, wspace=0.4)
        self.frame_figure.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_figure)
        self.frame_figure.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Stock Price")
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.grid()

        # 存储用于重绘的对象
        self.line = None
        self.patches = []

        self.dragging = False
        self.drag_start_x = None
        
        self.__bind_events()
    
    def __bind_events(self):
        # 滚轮事件
        self.frame_figure.canvas.get_tk_widget().bind("<MouseWheel>", self.__scroll_event)
        self.frame_figure.canvas.get_tk_widget().bind("<Button-1>", self.__click_event)
        self.frame_figure.canvas.get_tk_widget().bind("<B1-Motion>", self.__drag_event)
        self.frame_figure.canvas.get_tk_widget().bind("<ButtonRelease-1>", self.__release_event)
        self.frame_figure.canvas.get_tk_widget().bind("<Motion>", self.__motion_event)

    def __motion_event(self, event):
        if self.data is None or len(self.data) == 0:
            return
        
        x = (event.x - 0.075 * self.frame_figure.winfo_width()) / (0.9 * self.frame_figure.winfo_width())

        x_index = int(self.end_index - x * (self.end_index - self.start_index + 1))
        if x_index < 0 or x_index >= len(self.data):
            return
        
        # print(self.data['Date'][x_index], self.data['Price'][x_index],
        #       self.data['Open'][x_index],
        #       self.data['High'][x_index], self.data['Low'][x_index])

    def __click_event(self, event):
        self.dragging = True
        self.drag_start_x = event.x
    
    def __drag_event(self, event):
        if self.dragging:
            dx = (event.x - self.drag_start_x) / (0.9 * self.frame_figure.winfo_width())
            move_index = dx * (self.end_index - self.start_index)
            next_start_index = self.start_index + move_index
            next_end_index = self.end_index + move_index
            if next_start_index >= 0 and \
                next_start_index < len(self.data) and \
                next_end_index > 0 and \
                next_end_index <= len(self.data):
                self.start_index = next_start_index
                self.end_index = next_end_index
                self.Draw()
                self.drag_start_x = event.x
        
    
    def __release_event(self, event):
        self.dragging = False
        self.drag_start_x = None
        self.Draw()

    def __scroll_event(self, event):
        """Scroll event to zoom in/out the figure."""
        # get real mouse position
        x = event.x
        y = event.y
        # get relative position
        x = (x - 0.075 * self.frame_figure.winfo_width()) / (0.9 * self.frame_figure.winfo_width())
        y = (y - 0.05 * self.frame_figure.winfo_height()) / (0.8 * self.frame_figure.winfo_height())
        # print(x, y)

        if event.delta < 0:
            if self.start_index <= (1-x):
                self.end_index = min(len(self.data), self.end_index + (1-self.start_index))
                self.start_index = 0.0
            elif (len(self.data) - self.end_index) <= x:
                self.start_index = max(0, self.start_index - (1-(len(self.data) - self.end_index)))
                self.end_index = float(len(self.data))
            else:
                self.start_index = max(0, self.start_index - 1 + x)
                self.end_index = min(len(self.data), self.end_index + x)
        else:
            self.start_index = min(len(self.data), self.start_index + 1 - x, self.end_index-2)
            self.end_index = max(0, self.end_index - x, self.start_index+2)
        # print(self.start_index, self.end_index)
        self.Draw()

    def load_data_csv(self, company_name):
        """Load data into the figure."""
        """Date","Price","Open","High","Low","Vol.","Change %"""
        self.data = pd.read_csv(company_name + " Stock Price History.csv")
        self.start_index = 0.0
        self.end_index = float(len(self.data))

    def Draw(self):
        """Draw using more efficient methods."""
        if self.data is None:
            return
                
        self.ax.clear()
        
        # 设置基本属性
        self.ax.set_title("Stock Price")
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.grid()
        
        # 计算数据范围
        start_index = int(self.start_index)
        end_index = max(start_index + 2, int(self.end_index))
        
        # 提取需要显示的数据
        data_slice = self.data.iloc[start_index:end_index]
        dates = pd.to_datetime(data_slice["Date"])
        
        # 使用更高效的方式绘制K线图 - 批量处理而不是逐条绘制
        if len(data_slice) <= 200:  # 小于200个数据点时绘制K线
            # 准备K线数据
            opens = data_slice["Open"]
            closes = data_slice["Price"]
            highs = data_slice["High"]
            lows = data_slice["Low"]
            
            # 计算颜色
            colors = ["green" if close >= open else "red" for open, close in zip(opens, closes)]
            
            # 批量绘制线图部分
            self.ax.vlines(dates, lows, highs, colors=colors, linewidth=1)
            
            # 将日期转换为matplotlib可处理的浮点数
            dates_num = mdates.date2num(dates)
            
            # 计算矩形参数 - 使用数值型日期
            width = 0.7  # 以天为单位的宽度
            
            green_rects = []
            red_rects = []
            
            for i, (date_num, open_val, close_val, color) in enumerate(zip(dates_num, opens, closes, colors)):
                # 确定矩形位置和大小
                bottom = min(open_val, close_val)
                height = abs(close_val - open_val)
                
                # 创建矩形
                rect = mpatches.Rectangle(
                    (date_num - width/2, bottom), width, height
                )
                
                # 根据颜色分类
                if color == "green":
                    green_rects.append(rect)
                else:
                    red_rects.append(rect)
            
            # 分颜色批量添加矩形
            if green_rects:
                self.ax.add_collection(PatchCollection(green_rects, facecolor="green", edgecolor="black", linewidth=0.5))
            if red_rects:
                self.ax.add_collection(PatchCollection(red_rects, facecolor="red", edgecolor="black", linewidth=0.5))
        else:
            # 数据点太多时，只绘制线图
            self.ax.plot(dates, data_slice["Price"], label="Price", color="blue")
        
        # 设置坐标轴范围
        if len(dates) > 0:
            self.ax.set_xlim(dates.min() - pd.Timedelta(days=1), dates.max() + pd.Timedelta(days=1))
        self.ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        
        # 更新画布
        self.frame_figure.canvas.draw()