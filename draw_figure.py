import PIL.Image
import PIL.ImageTk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.collections import PatchCollection
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from data import Data
import time
import PIL

class Figures(tk.Frame):
    def __init__(self, master, stock_code=None):
        super().__init__(master)
        self.master = master
        self.stock_code = stock_code
        self.start_index = None
        self.end_index = None
        self.zoom_days = None
        self.y_max = None
        self.y_min = None
        self.value_line = None
        self.value_text = None
        self.data = Data()

        self.loading_mask = tk.Frame(self, background="gray")
        self.loading_text = ttk.Label(self.loading_mask, text="Loading...", background="gray", foreground='white', font=("Arial", 20), justify='center')
        # self.loading_mask.lift()
        self.loading_mask.place_forget()
        self.loading_text.place(relx=0.5, rely=0.5, anchor="center")
        self.show_ma_bollinger = tk.StringVar(value="")

        self.frame_Kline = tk.Canvas(self, bg="white")
        self.frame_Kline.place(relx=0, rely=0.05, relwidth=1, relheight=0.75, anchor="nw")
        self.day_line = {'frame_kline': None, 'frame_macd': None, 'frame_volume': None, 'frame_kdj': None, 'frame_rsi': None}
        self.moving_averages_info = [None, None, None]
        self.day_info = None

        self.frame_volume = tk.Canvas(self, bg="white")
        self.frame_macd = tk.Canvas(self, bg="white")
        self.frame_kdj = tk.Canvas(self, bg="white")
        self.frame_rsi = tk.Canvas(self, bg="white")
        self.frame_list = [self.frame_volume, self.frame_macd, self.frame_kdj, self.frame_rsi]
        self.frame_enabled = [tk.BooleanVar(value=False) for _ in range(len(self.frame_list))]
        self.__change_figure()
        
        try:
            self.cross_hair_button_icon = PIL.Image.open("icons/cross_hair.png")
            self.cross_hair_button_icon = self.cross_hair_button_icon.resize((25, 25))
            self.cross_hair_button_icon = PIL.ImageTk.PhotoImage(self.cross_hair_button_icon)
            self.cross_hair_button = tk.Button(self, image=self.cross_hair_button_icon,
                                            command=self.__press_cross_hair_button, fg="white",
                                                cursor="hand2", takefocus=0, relief=tk.RAISED)
        except:
            self.cross_hair_button = tk.Button(self, text='+', command=self.__press_cross_hair_button,
                                               fg="black", cursor="hand2", takefocus=0, relief=tk.RAISED)
        # self.cross_hair_button.configure(width=self.winfo_width()/20, height=self.winfo_height()/20)
        self.cross_hair_button.place(x=0, y=0, width=self.winfo_height()/20, height=self.winfo_height()/20, anchor="nw")
        self.cross_hair_button_flag = False
        self.scale_status = "D"
        self.day_button = tk.Button(self, text="D", command=lambda: self.__change_scale(s="D"),
                                    relief=tk.SUNKEN, cursor="hand2", takefocus=0, width=3)
        self.week_button = tk.Button(self, text="W", command=lambda: self.__change_scale(s="W"),
                                     relief=tk.RAISED, cursor="hand2", takefocus=0, width=3)
        self.month_button = tk.Button(self, text="M", command=lambda: self.__change_scale(s="M"),
                                      relief=tk.RAISED, cursor="hand2", takefocus=0, width=3)
        self.day_button.place(x=self.winfo_height()/20, y=0, width=self.winfo_height()/20, height=self.winfo_height()/20, anchor="nw")
        self.week_button.place(x=self.winfo_height()/20*2, y=0, width=self.winfo_height()/20, height=self.winfo_height()/20, anchor="nw")
        self.month_button.place(x=self.winfo_height()/20*3, y=0, width=self.winfo_height()/20, height=self.winfo_height()/20, anchor="nw")

        self.dragging = False
        self.drag_start_x = None
        
        self.__bind_events()
    def show_mask(self):
        self.loading_mask.place(relx=0, rely=0, relwidth=1, relheight=1, anchor="nw")
        self.loading_mask.lift()

    def hide_mask(self):
        self.loading_mask.place_forget()

    def new_data(self, stock_code):
        self.after(0, self.show_mask())
        self.stock_code = stock_code
        self.data.stock_code = stock_code
        self.data.load_data_csv()
        self.end_index = len(self.data.data_daily.data) - 1
        self.start_index = self.end_index - 30
        self.zoom_days = 30
        self.__refresh_figure()
        self.after(0, self.hide_mask())

    def __bind_events(self):
        self.frame_Kline.bind("<MouseWheel>", self.__scroll_event)
        self.frame_Kline.bind("<Button-1>", self.__click_event)
        self.frame_Kline.bind("<B1-Motion>", self.__drag_event)
        self.frame_Kline.bind("<ButtonRelease-1>", self.__release_event)
        self.frame_Kline.bind("<Motion>", self.__motion_event)
        self.frame_Kline.bind("<Configure>", self.__refresh_figure)
        self.bind("<Configure>", self.__refresh_frame)
        # self.frame_volume.bind("<Configure>", self.__refresh_figure)
        # self.frame_macd.bind("<Configure>", self.__refresh_figure)
        # self.frame_kdj.bind("<Configure>", self.__refresh_figure)
        # self.frame_rsi.bind("<Configure>", self.__refresh_figure)
        self.show_ma_bollinger.trace_add("write", self.__refresh_figure)
        for flag in self.frame_enabled:
            flag.trace_add("write", self.__change_figure)
        # self.cross_hair_button.bind("<Button-1>", self.__press_cross_hair_button)

    def __change_figure(self, *args):
        num_of_figures = np.sum([bool(i.get()) for i in self.frame_enabled])
        if num_of_figures == 0:
            self.frame_Kline.place(relx=0, rely=0.05, relwidth=1, relheight=0.95, anchor="nw")
            for frame in self.frame_list:
                frame.place_forget()
        elif num_of_figures == 1:
            self.frame_Kline.place(relx=0, rely=0.05, relwidth=1, relheight=0.75, anchor="nw")
            for i, frame in enumerate(self.frame_list):
                if self.frame_enabled[i].get():
                    frame.place(relx=0, rely=0.8, relwidth=1, relheight=0.2, anchor="nw")
                else:
                    frame.place_forget()
        elif num_of_figures == 2:
            self.frame_Kline.place(relx=0, rely=0.05, relwidth=1, relheight=0.55, anchor="nw")
            start_y = 0.6
            for i, frame in enumerate(self.frame_list):
                if self.frame_enabled[i].get():
                    frame.place(relx=0, rely=start_y, relwidth=1, relheight=0.2, anchor="nw")
                    start_y += 0.2
                else:
                    frame.place_forget()
        elif num_of_figures == 3:
            self.frame_Kline.place(relx=0, rely=0.05, relwidth=1, relheight=0.35, anchor="nw")
            start_y = 0.4
            for i, frame in enumerate(self.frame_list):
                if self.frame_enabled[i].get():
                    frame.place(relx=0, rely=start_y, relwidth=1, relheight=0.2, anchor="nw")
                    start_y += 0.2
                else:
                    frame.place_forget()
        self.after(10, self.__refresh_figure)

    def __change_scale(self, event=None, s='D'):
        if self.scale_status == s:
            return
        if s == 'D':
            self.day_button.config(relief=tk.SUNKEN)
            self.week_button.config(relief=tk.RAISED)
            self.month_button.config(relief=tk.RAISED)
        elif s == 'W':
            self.day_button.config(relief=tk.RAISED)
            self.week_button.config(relief=tk.SUNKEN)
            self.month_button.config(relief=tk.RAISED)
        elif s == 'M':
            self.day_button.config(relief=tk.RAISED)
            self.week_button.config(relief=tk.RAISED)
            self.month_button.config(relief=tk.SUNKEN)
        self.scale_status = s
        self.__refresh_figure()

    def __refresh_frame(self, event):
        self.cross_hair_button.place(x=0, y=0, width=self.winfo_height()/20, height=self.winfo_height()/20, anchor="nw")
        self.day_button.place(x=self.winfo_height()/20, y=0, width=self.winfo_height()/20, height=self.winfo_height()/20, anchor="nw")
        self.week_button.place(x=self.winfo_height()/20*2, y=0, width=self.winfo_height()/20, height=self.winfo_height()/20, anchor="nw")
        self.month_button.place(x=self.winfo_height()/20*3, y=0, width=self.winfo_height()/20, height=self.winfo_height()/20, anchor="nw")

    def __press_cross_hair_button(self, event=None):
        if self.cross_hair_button_flag:
            # self.cross_hair_button.configure(style="Custom.TButton")
            self.cross_hair_button.config(relief=tk.RAISED)
            # print("cross_hair_button Custom.TButton")
            self.cross_hair_button_flag = False
            if self.day_line['frame_kline'] is not None:
                self.frame_Kline.delete(self.day_line['frame_kline'])
                self.day_line['frame_kline'] = None
                # self.day_info.place_forget()
                if self.day_info is not None:
                    self.frame_Kline.delete(self.day_info)
                    self.day_info = None
            if self.day_line['frame_macd'] is not None:
                self.frame_macd.delete(self.day_line['frame_macd'])
                self.day_line['frame_macd'] = None
            if self.day_line['frame_volume'] is not None:
                self.frame_volume.delete(self.day_line['frame_volume'])
                self.day_line['frame_volume'] = None
            if self.day_line['frame_kdj'] is not None:
                self.frame_kdj.delete(self.day_line['frame_kdj'])
                self.day_line['frame_kdj'] = None
            if self.value_line is not None:
                self.frame_Kline.delete(self.value_line)
                self.value_line = None
            if self.value_text is not None:
                self.frame_Kline.delete(self.value_text)
                self.value_text = None
        else:
            # self.cross_hair_button.configure(style="Pressed.TButton")
            self.cross_hair_button.config(relief=tk.SUNKEN)
            # print("cross_hair_button Pressed.TButton")
            self.cross_hair_button_flag = True

    def __motion_event(self, event):
        if self.data.data_daily.data is None:
            return
        if self.day_line['frame_kline'] is not None:
            self.frame_Kline.delete(self.day_line['frame_kline'])
        if self.day_line['frame_macd'] is not None:
            self.frame_macd.delete(self.day_line['frame_macd'])
        if self.day_line['frame_volume'] is not None:
            self.frame_volume.delete(self.day_line['frame_volume'])
        if self.day_line['frame_kdj'] is not None:
            self.frame_kdj.delete(self.day_line['frame_kdj'])
        if self.day_line['frame_rsi'] is not None:
            self.frame_rsi.delete(self.day_line['frame_rsi'])
        if self.cross_hair_button_flag:
            # x axis
            start_date = self.data.data_daily.data['<DATE>'].iloc[round(self.start_index)]
            end_date = self.data.data_daily.data['<DATE>'].iloc[round(self.end_index)]
            if self.scale_status == "D":
                filtered_data = self.data.data_daily.data[(self.data.data_daily.data['<DATE>'] >= start_date-pd.Timedelta(days=1)) & 
                                                          (self.data.data_daily.data['<DATE>'] <= end_date+pd.Timedelta(days=1))]
            elif self.scale_status == "W":
                filtered_data = self.data.data_weekly.data[(self.data.data_weekly.data['<DATE>'] >= start_date-pd.Timedelta(days=7)) & 
                                                          (self.data.data_weekly.data['<DATE>'] <= end_date+pd.Timedelta(days=7))]
            elif self.scale_status == "M":
                filtered_data = self.data.data_monthly.data[(self.data.data_monthly.data['<DATE>'] >= start_date-pd.Timedelta(days=30)) & 
                                                          (self.data.data_monthly.data['<DATE>'] <= end_date+pd.Timedelta(days=30))]
            x = event.x / self.frame_Kline.winfo_width()
            if round(self.end_index) == filtered_data.index[-1]:
                x = x * filtered_data.shape[0]
            else:
                x *= filtered_data.shape[0] - 1
            x = round(x)
            try:
                day = filtered_data.iloc[x]['<DATE>']
                # show moving average
                for moving_average_info in self.moving_averages_info:
                    if moving_average_info is not None:
                        self.frame_Kline.delete(moving_average_info)
                if self.scale_status == "D":
                    self.moving_averages_info[0] = self.frame_Kline.create_text(
                        1, 0,
                        text=f"MA5: {self.data.data_daily.ma5[filtered_data.index[x]]:.2f},",
                        fill="red", anchor="nw", font=("Arial", 8)
                    )
                    self.moving_averages_info[1] = self.frame_Kline.create_text(
                        self.frame_Kline.bbox(self.moving_averages_info[0])[2]+1, 0,
                        text=f"MA10: {self.data.data_daily.ma10[filtered_data.index[x]]:.2f},",
                        fill="blue", anchor="nw", font=("Arial", 8)
                    )
                    self.moving_averages_info[2] = self.frame_Kline.create_text(
                        self.frame_Kline.bbox(self.moving_averages_info[1])[2]+1, 0,
                        text=f"MA20: {self.data.data_daily.ma20[filtered_data.index[x]]:.2f}",
                        fill="green", anchor="nw", font=("Arial", 8)
                    )
                elif self.scale_status == "W":
                    self.moving_averages_info[0] = self.frame_Kline.create_text(
                        1, 0,
                        text=f"MA5: {self.data.data_weekly.ma5[filtered_data.index[x]]:.2f},",
                        fill="red", anchor="nw", font=("Arial", 8)
                    )
                    self.moving_averages_info[1] = self.frame_Kline.create_text(
                        self.frame_Kline.bbox(self.moving_averages_info[0])[2]+1, 0,
                        text=f"MA10: {self.data.data_weekly.ma10[filtered_data.index[x]]:.2f},",
                        fill="blue", anchor="nw", font=("Arial", 8)
                    )
                    self.moving_averages_info[2] = self.frame_Kline.create_text(
                        self.frame_Kline.bbox(self.moving_averages_info[1])[2]+1, 0,
                        text=f"MA20: {self.data.data_weekly.ma20[filtered_data.index[x]]:.2f}",
                        fill="green", anchor="nw", font=("Arial", 8)
                    )
                elif self.scale_status == "M":
                    self.moving_averages_info[0] = self.frame_Kline.create_text(
                        1, 0,
                        text=f"MA5: {self.data.data_monthly.ma5[filtered_data.index[x]]:.2f},",
                        fill="red", anchor="nw", font=("Arial", 8)
                    )
                    self.moving_averages_info[1] = self.frame_Kline.create_text(
                        self.frame_Kline.bbox(self.moving_averages_info[0])[2]+1, 0,
                        text=f"MA10: {self.data.data_monthly.ma10[filtered_data.index[x]]:.2f},",
                        fill="blue", anchor="nw", font=("Arial", 8)
                    )
                    self.moving_averages_info[2] = self.frame_Kline.create_text(
                        self.frame_Kline.bbox(self.moving_averages_info[1])[2]+1, 0,
                        text=f"MA20: {self.data.data_monthly.ma20[filtered_data.index[x]]:.2f}",
                        fill="green", anchor="nw", font=("Arial", 8)
                    )
                if round(self.end_index) == filtered_data.index[-1]:
                    x = x / filtered_data.shape[0] * self.frame_Kline.winfo_width()
                else:
                    x = x / (filtered_data.shape[0] - 1) * self.frame_Kline.winfo_width()
                self.day_line['frame_kline'] = self.frame_Kline.create_line(
                    x, 0,
                    x, self.frame_Kline.winfo_height(),
                    fill="gray", width=1.5, dash=(2, 2)
                )
                self.day_line['frame_macd'] = self.frame_macd.create_line(
                    x, 0,
                    x, self.frame_macd.winfo_height(),
                    fill="gray", width=1.5, dash=(2, 2)
                )
                self.day_line['frame_volume'] = self.frame_volume.create_line(
                    x, 0,
                    x, self.frame_volume.winfo_height(),
                    fill="gray", width=1.5, dash=(2, 2)
                )
                self.day_line['frame_kdj'] = self.frame_kdj.create_line(
                    x, 0,
                    x, self.frame_kdj.winfo_height(),
                    fill="gray", width=1.5, dash=(2, 2)
                )
                self.day_line['frame_rsi'] = self.frame_rsi.create_line(
                    x, 0,
                    x, self.frame_rsi.winfo_height(),
                    fill="gray", width=1.5, dash=(2, 2)
                )
                if self.day_info is not None:
                    self.frame_Kline.delete(self.day_info)
                if self.scale_status == "D" or self.scale_status == "W":
                    if x > self.frame_Kline.winfo_width()/2:
                        self.day_info = self.frame_Kline.create_text(
                            x-5, self.frame_Kline.winfo_height(),
                            text=day.strftime("%Y-%m-%d"), fill="black", anchor="se", font=("Arial", 8)
                        )
                    else:
                        self.day_info = self.frame_Kline.create_text(
                            x+5, self.frame_Kline.winfo_height(),
                            text=day.strftime("%Y-%m-%d"), fill="black", anchor="sw", font=("Arial", 8)
                        )
                elif self.scale_status == "M":
                    if x > self.frame_Kline.winfo_width()/2:
                        self.day_info = self.frame_Kline.create_text(
                            x-5, self.frame_Kline.winfo_height(),
                            text=day.strftime("%Y-%m"), fill="black", anchor="se", font=("Arial", 8)
                        )
                    else:
                        self.day_info = self.frame_Kline.create_text(
                            x+5, self.frame_Kline.winfo_height(),
                            text=day.strftime("%Y-%m"), fill="black", anchor="sw", font=("Arial", 8)
                        )
            except:
                pass
            # y axis
            y = event.y
            y_value = (self.frame_Kline.winfo_height()-y) / self.frame_Kline.winfo_height() * (self.y_max - self.y_min) + self.y_min
            y_value = round(y_value, 2)
            self.frame_Kline.delete(self.value_line)
            self.frame_Kline.delete(self.value_text)
            self.value_line = self.frame_Kline.create_line(
                0, y,
                self.frame_Kline.winfo_width(), y,
                fill="gray", width=1.5, dash=(2, 2)
            )
            if y < self.frame_Kline.winfo_height()/2:
                self.value_text = self.frame_Kline.create_text(
                    5, y,
                    text=str(y_value), fill="black", anchor="nw", font=("Arial", 8)
                )
            else:
                self.value_text = self.frame_Kline.create_text(
                    5, y,
                    text=str(y_value), fill="black", anchor="sw", font=("Arial", 8)
                )

        

    def __click_event(self, event):
        if self.data.data_daily.data is None:
            return
        self.dragging = True
        self.drag_start_x = event.x
    
    def __drag_event(self, event):
        if self.dragging:
            dx = (event.x - self.drag_start_x) * self.zoom_days / self.frame_Kline.winfo_width()
            if dx < 0:
                self.end_index = min(self.end_index - dx, len(self.data.data_daily.data) - 1)
                self.start_index = self.end_index - self.zoom_days
            elif dx > 0:
                self.start_index = max(self.start_index - dx, 0)
                self.end_index = self.start_index + self.zoom_days
            else:
                return
            # print(self.end_index-self.start_index)
            self.__refresh_figure()
            self.drag_start_x = event.x
        self.__motion_event(event)
    
    def __release_event(self, event):
        self.dragging = False
        self.drag_start_x = None

    def __scroll_event(self, event):
        # """Scroll event to zoom in/out the figure."""
        if self.data.data_daily.data is None:
            return
        x = event.x / self.frame_Kline.winfo_width()
        center_index = self.start_index * (1-x) + self.end_index * (x)
        if event.delta < 0:
            if self.scale_status == "D":
                self.zoom_days = max(self.zoom_days * 1.1, self.zoom_days + 1)
            elif self.scale_status == "W":
                self.zoom_days = max(self.zoom_days * 1.1, self.zoom_days + 5)
            elif self.scale_status == "M":
                self.zoom_days = max(self.zoom_days * 1.1, self.zoom_days + 30)
        else:
            if self.scale_status == "D":
                self.zoom_days = max(min(self.zoom_days * 0.9, self.zoom_days-1), 4)
            elif self.scale_status == "W":
                self.zoom_days = max(min(self.zoom_days * 0.9, self.zoom_days-5), 20)
            elif self.scale_status == "M":
                self.zoom_days = max(min(self.zoom_days * 0.9, self.zoom_days-30), 120)
        self.end_index = min(center_index + self.zoom_days * (1-x), len(self.data.data_daily.data) - 1)
        self.start_index = max(self.end_index - self.zoom_days, 0)
        self.zoom_days = self.end_index - self.start_index
        self.__refresh_figure()
        return

    def __refresh_figure(self, *args):
        if self.data.data_daily.data is None:
            return

        # clear canvas
        self.frame_Kline.delete("all")
        self.frame_macd.delete("all")
        self.frame_volume.delete("all")
        self.frame_kdj.delete("all")
        self.frame_rsi.delete("all")

        start_date = self.data.data_daily.data['<DATE>'].iloc[round(self.start_index)]
        end_date = self.data.data_daily.data['<DATE>'].iloc[round(self.end_index)]

        match(self.scale_status):
            case "D":
                filtered_data = self.data.data_daily.data[(self.data.data_daily.data['<DATE>'] >= start_date -pd.Timedelta(days=1)) & (self.data.data_daily.data['<DATE>'] <= end_date+pd.Timedelta(days=1))]
                bollinger_bands = self.data.data_daily.bollinger_bands
                ma5 = self.data.data_daily.ma5
                ma10 = self.data.data_daily.ma10
                ma20 = self.data.data_daily.ma20
                macd = self.data.data_daily.macd
                kdj = self.data.data_daily.kdj
                rsi = self.data.data_daily.rsi
                length = filtered_data.shape[0] - 1
                if filtered_data.index[-1] == self.data.data_daily.data.index[-1]:
                    length += 1

            case "W":
                filtered_data = self.data.data_weekly.data[(self.data.data_weekly.data['<DATE>'] >= start_date - pd.Timedelta(days=7)) & (self.data.data_weekly.data['<DATE>'] <= end_date + pd.Timedelta(days=7))]
                bollinger_bands = self.data.data_weekly.bollinger_bands
                ma5 = self.data.data_weekly.ma5
                ma10 = self.data.data_weekly.ma10
                ma20 = self.data.data_weekly.ma20
                macd = self.data.data_weekly.macd
                kdj = self.data.data_weekly.kdj
                rsi = self.data.data_weekly.rsi
                length = filtered_data.shape[0] - 1
                if filtered_data.index[-1] == self.data.data_weekly.data.index[-1]:
                    length += 1

            case "M":
                filtered_data = self.data.data_monthly.data[(self.data.data_monthly.data['<DATE>'] >= start_date - pd.Timedelta(days=30)) & (self.data.data_monthly.data['<DATE>'] <= end_date + pd.Timedelta(days=30))]
                bollinger_bands = self.data.data_monthly.bollinger_bands
                ma5 = self.data.data_monthly.ma5
                ma10 = self.data.data_monthly.ma10
                ma20 = self.data.data_monthly.ma20
                macd = self.data.data_monthly.macd
                kdj = self.data.data_monthly.kdj
                rsi = self.data.data_monthly.rsi
                length = filtered_data.shape[0] - 1
                if filtered_data.index[-1] == self.data.data_monthly.data.index[-1]:
                    length += 1

        if filtered_data.empty:
            return
        
        # initialize canvas
        canvas_width = self.frame_Kline.winfo_width()
        canvas_height = self.frame_Kline.winfo_height()

        index_min = filtered_data.index[0]
        index_max = filtered_data.index[-1]
        width = 0.7 * canvas_width / length
        y_min = np.nanmin(filtered_data['<LOW>']*0.99)
        y_max = np.nanmax(filtered_data['<HIGH>']*1.01)
        self.y_min = y_min
        self.y_max = y_max
        osc_max = np.nanmax(abs(macd['osc'][index_min: index_max+1])) * 1.1
        dif_dem_max = max(np.nanmax(macd['dif'][index_min: index_max+1]), np.nanmax(macd['dem'][index_min: index_max+1]))
        dif_dem_min = min(np.nanmin(macd['dif'][index_min: index_max+1]), np.nanmin(macd['dem'][index_min: index_max+1]))
        dif_dem_max = dif_dem_max + (dif_dem_max - dif_dem_min) * 0.1
        dif_dem_min = dif_dem_min - (dif_dem_max - dif_dem_min) * 0.1
        vol_max = max(filtered_data['<VOL>']) * 1.1
        kdj_max = max(np.nanmax(kdj['k'][index_min: index_max+1]), np.nanmax(kdj['d'][index_min: index_max+1]), np.nanmax(kdj['j'][index_min: index_max+1]))
        kdj_min = min(np.nanmin(kdj['k'][index_min: index_max+1]), np.nanmin(kdj['d'][index_min: index_max+1]), np.nanmin(kdj['j'][index_min: index_max+1]))
        kdj_max = kdj_max + (kdj_max - kdj_min) * 0.1
        kdj_min = kdj_min - (kdj_max - kdj_min) * 0.1
        rsi_max = max(np.nanmax(rsi['6'][index_min: index_max+1]), np.nanmax(rsi['14'][index_min: index_max+1]))
        rsi_min = min(np.nanmin(rsi['6'][index_min: index_max+1]), np.nanmin(rsi['14'][index_min: index_max+1]))
        rsi_max = rsi_max + (rsi_max - rsi_min) * 0.1
        rsi_min = rsi_min - (rsi_max - rsi_min) * 0.1
        
        self.frame_macd.create_line(
            0, self.frame_macd.winfo_height()/2, self.frame_macd.winfo_width(), self.frame_macd.winfo_height()/2,
            fill="gray", width=1.5, dash=(2, 2)
        )
        self.frame_volume.create_line(
            0, self.frame_volume.winfo_height()/3, self.frame_volume.winfo_width(), self.frame_volume.winfo_height()/3,
            fill="gray", width=1.5, dash=(2, 2)
        )
        self.frame_volume.create_text(
            5, self.frame_volume.winfo_height()/3,
            text=f"{round(vol_max*0.667/1000000, 2)}M", fill="gray", anchor="nw", font=tkFont.Font(family="Arial", size=8, weight="bold")
        )
        self.frame_volume.create_line(
            0, self.frame_volume.winfo_height()/3*2, self.frame_volume.winfo_width(), self.frame_volume.winfo_height()/3*2,
            fill="gray", width=1.5, dash=(2, 2)
        )
        self.frame_volume.create_text(
            5, self.frame_volume.winfo_height()/3*2,
            text=f"{round(vol_max*0.333/1000000, 2)}M", fill="gray", anchor="nw", font=tkFont.Font(family="Arial", size=8, weight="bold")
        )
        # legend
        self.frame_rsi.create_text(
            self.frame_rsi.winfo_width()-5, 5,
            text=f"RSI(6)", fill="blue", anchor="ne", font=tkFont.Font(family="Arial", size=8, weight="bold")
        )
        self.frame_rsi.create_text(
            self.frame_rsi.winfo_width()-5, 25,
            text=f"RSI(14)", fill="purple", anchor="ne", font=tkFont.Font(family="Arial", size=8, weight="bold")
        )

        self.frame_kdj.create_text(
            self.frame_kdj.winfo_width()-5, 5,
            text=f"KDJ(K)", fill="blue", anchor="ne", font=tkFont.Font(family="Arial", size=8, weight="bold")
        )
        self.frame_kdj.create_text(
            self.frame_kdj.winfo_width()-5, 25,
            text=f"KDJ(D)", fill="purple", anchor="ne", font=tkFont.Font(family="Arial", size=8, weight="bold")
        )
        self.frame_kdj.create_text(
            self.frame_kdj.winfo_width()-5, 45,
            text=f"KDJ(J)", fill="green", anchor="ne", font=tkFont.Font(family="Arial", size=8, weight="bold")
        )

        for i, data in enumerate(filtered_data.iterrows()):
            # draw kline data
            date = data[1]['<DATE>']
            open_price = data[1]['<OPEN>']
            close_price = data[1]['<CLOSE>']
            high_price = data[1]['<HIGH>']
            low_price = data[1]['<LOW>']
            x = i / length * canvas_width
            y_open = (open_price - y_min) / (y_max - y_min) * canvas_height
            y_close = (close_price - y_min) / (y_max - y_min) * canvas_height
            y_high = (high_price - y_min) / (y_max - y_min) * canvas_height
            y_low = (low_price - y_min) / (y_max - y_min) * canvas_height
            y_open = canvas_height - y_open
            y_close = canvas_height - y_close
            y_high = canvas_height - y_high
            y_low = canvas_height - y_low
            color = "green" if close_price >= open_price else "red"
            # draw lines
            self.frame_Kline.create_line(
                x, y_high, x, y_low, fill=color, width=1.5
            )
            # draw rectangles
            self.frame_Kline.create_rectangle(
                x - width / 2, y_open, x + width / 2, y_close,
                fill=color, outline=color
            )
            
            # draw volume
            if self.frame_volume.winfo_width() > 1 and self.frame_volume.winfo_height() > 1 and vol_max > 0:
                volume = data[1]['<VOL>']
                self.frame_volume.create_rectangle(
                    x - width / 2, self.frame_volume.winfo_height(), x + width / 2, self.frame_volume.winfo_height() - volume / vol_max * self.frame_volume.winfo_height(),
                    fill='blue', outline='gray'
                )

            if data[0] == 0:
                continue
            # draw moving average lines
            if self.show_ma_bollinger.get() == "ma":
                if (not np.isnan(ma5[data[0]])) or  (not np.isnan(ma5[data[0]-1])) and (y_max > y_min):
                    self.frame_Kline.create_line(
                        x, canvas_height - (ma5[data[0]] - y_min) / (y_max - y_min) * canvas_height, 
                        (i-1) / length * canvas_width, canvas_height - (ma5[data[0]-1] - y_min) / (y_max - y_min) * canvas_height, 
                        fill='red', width=1
                    )
                if (not np.isnan(ma10[data[0]])) or  (not np.isnan(ma10[data[0]-1])) and (y_max > y_min):
                    self.frame_Kline.create_line(
                        x, canvas_height - (ma10[data[0]] - y_min) / (y_max - y_min) * canvas_height, 
                        (i-1) / length * canvas_width, canvas_height - (ma10[data[0]-1] - y_min) / (y_max - y_min) * canvas_height, 
                        fill='green', width=1
                    )
                if (not np.isnan(ma20[data[0]])) or  (not np.isnan(ma20[data[0]-1])) and (y_max > y_min):
                    self.frame_Kline.create_line(
                        x, canvas_height - (ma20[data[0]] - y_min) / (y_max - y_min) * canvas_height, 
                        (i-1) / length * canvas_width, canvas_height - (ma20[data[0]-1] - y_min) / (y_max - y_min) * canvas_height, 
                        fill='blue', width=1
                    )
            # draw bollinger bands
            if self.show_ma_bollinger.get() == "bollinger":
                if (not np.isnan(ma20[data[0]])) or  (not np.isnan(ma20[data[0]-1])) and (y_max > y_min):
                    self.frame_Kline.create_line(
                        x, canvas_height - (ma20[data[0]] - y_min) / (y_max - y_min) * canvas_height, 
                        (i-1) / length * canvas_width, canvas_height - (ma20[data[0]-1] - y_min) / (y_max - y_min) * canvas_height, 
                        fill='blue', width=1
                    )
                if (not np.isnan(bollinger_bands['upper'][data[0]])) or  (not np.isnan(bollinger_bands['upper'][data[0]-1])) and (y_max > y_min):
                    self.frame_Kline.create_line(
                        x, canvas_height - (bollinger_bands['upper'][data[0]] - y_min) / (y_max - y_min) * canvas_height, 
                        (i-1) / length * canvas_width, canvas_height - (bollinger_bands['upper'][data[0]-1] - y_min) / (y_max - y_min) * canvas_height, 
                        fill='orange', width=1
                    )
                if (not np.isnan(bollinger_bands['lower'][data[0]])) or  (not np.isnan(bollinger_bands['lower'][data[0]-1])) and (y_max > y_min):
                    self.frame_Kline.create_line(
                        x, canvas_height - (bollinger_bands['lower'][data[0]] - y_min) / (y_max - y_min) * canvas_height, 
                        (i-1) / length * canvas_width, canvas_height - (bollinger_bands['lower'][data[0]-1] - y_min) / (y_max - y_min) * canvas_height, 
                        fill='purple', width=1
                    )

            # draw macd
            if self.frame_macd.winfo_width() > 1 and self.frame_macd.winfo_height() > 1:
                osc = macd['osc'][data[0]]
                if osc_max > 0:
                    if osc > 0:
                        self.frame_macd.create_rectangle(
                            x - width / 2, self.frame_macd.winfo_height()/2, x + width / 2, self.frame_macd.winfo_height()/2 - osc / osc_max * self.frame_macd.winfo_height()/2,
                            fill='red', outline='red'
                        )
                    else:
                        self.frame_macd.create_rectangle(
                            x - width / 2, self.frame_macd.winfo_height()/2, x + width / 2, self.frame_macd.winfo_height()/2 - osc / osc_max * self.frame_macd.winfo_height()/2,
                            fill='green', outline='green'
                        )
                dif = macd['dif'][data[0]]
                dem = macd['dem'][data[0]]
                if (dif_dem_max - dif_dem_min) > 0:
                    if (not np.isnan(dif)) and (not np.isnan(macd['dif'][data[0]-1])):
                        self.frame_macd.create_line(
                            x, (1 - (dif - dif_dem_min) / (dif_dem_max - dif_dem_min)) * self.frame_macd.winfo_height(),
                            (i-1) / length * canvas_width, (1 - (macd['dif'][data[0]-1] - dif_dem_min) / (dif_dem_max - dif_dem_min)) * self.frame_macd.winfo_height(),
                            fill='blue', width=1
                        )
                    if (not np.isnan(dem)) and (not np.isnan(macd['dem'][data[0]-1])):
                        self.frame_macd.create_line(
                            x, (1 - (dem - dif_dem_min) / (dif_dem_max - dif_dem_min)) * self.frame_macd.winfo_height(),
                            (i-1) / length * canvas_width, (1 - (macd['dem'][data[0]-1] - dif_dem_min) / (dif_dem_max - dif_dem_min)) * self.frame_macd.winfo_height(),
                            fill='purple', width=1
                        )

            # draw kdj
            if self.frame_kdj.winfo_width() > 1 and self.frame_kdj.winfo_height() > 1:
                k = kdj['k'][data[0]]
                d = kdj['d'][data[0]]
                j = kdj['j'][data[0]]
                if (kdj_max - kdj_min) > 0:
                    if (not np.isnan(k)) and (not np.isnan(kdj['k'][data[0]-1])):
                        self.frame_kdj.create_line(
                            x, (1 - (k - kdj_min) / (kdj_max - kdj_min)) * self.frame_kdj.winfo_height(),
                            (i-1) / length * canvas_width, (1 - (kdj['k'][data[0]-1] - kdj_min) / (kdj_max - kdj_min)) * self.frame_kdj.winfo_height(),
                            fill='blue', width=1
                        )
                    if (not np.isnan(d)) and (not np.isnan(kdj['d'][data[0]-1])):
                        self.frame_kdj.create_line(
                            x, (1 - (d - kdj_min) / (kdj_max - kdj_min)) * self.frame_kdj.winfo_height(),
                            (i-1) / length * canvas_width, (1 - (kdj['d'][data[0]-1] - kdj_min) / (kdj_max - kdj_min)) * self.frame_kdj.winfo_height(),
                            fill='purple', width=1
                        )
                    if (not np.isnan(j)) and (not np.isnan(kdj['j'][data[0]-1])):
                        self.frame_kdj.create_line(
                            x, (1 - (j - kdj_min) / (kdj_max - kdj_min)) * self.frame_kdj.winfo_height(),
                            (i-1) / length * canvas_width, (1 - (kdj['j'][data[0]-1] - kdj_min) / (kdj_max - kdj_min)) * self.frame_kdj.winfo_height(),
                            fill='green', width=1
                        )

            # draw rsi
            if self.frame_rsi.winfo_width() > 1 and self.frame_rsi.winfo_height() > 1:
                rsi_6 = rsi['6'][data[0]]
                rsi_14 = rsi['14'][data[0]]
                if (rsi_max - rsi_min) > 0:
                    if (not np.isnan(rsi_6)) and (not np.isnan(rsi['6'][data[0]-1])):
                        self.frame_rsi.create_line(
                            x, (1 - (rsi_6 - rsi_min) / (rsi_max - rsi_min)) * self.frame_rsi.winfo_height(),
                            (i-1) / length * canvas_width, (1 - (rsi['6'][data[0]-1] - rsi_min) / (rsi_max - rsi_min)) * self.frame_rsi.winfo_height(),
                            fill='blue', width=1
                        )
                    if (not np.isnan(rsi_14)) and (not np.isnan(rsi['14'][data[0]-1])):
                        self.frame_rsi.create_line(
                            x, (1 - (rsi_14 - rsi_min) / (rsi_max - rsi_min)) * self.frame_rsi.winfo_height(),
                            (i-1) / length * canvas_width, (1 - (rsi['14'][data[0]-1] - rsi_min) / (rsi_max - rsi_min)) * self.frame_rsi.winfo_height(),
                            fill='purple', width=1
                        )
        