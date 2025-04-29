import PIL.Image
import PIL.ImageTk
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
        
        self.frame_Kline = tk.Canvas(self, bg="white")
        self.frame_Kline.place(relx=0, rely=0.05, relwidth=1, relheight=0.9, anchor="nw")
        self.day_line = None

        self.day_info = tk.Label(self, text="", bg="white", font=("Arial", 8), justify='center')
        self.day_info.place_forget()

        self.cross_hair_button_icon = PIL.Image.open("icons/cross_hair.png")
        self.cross_hair_button_icon = self.cross_hair_button_icon.resize((25, 25))
        self.cross_hair_button_icon = PIL.ImageTk.PhotoImage(self.cross_hair_button_icon)
        self.cross_hair_button = tk.Button(self, image=self.cross_hair_button_icon,
                                           command=self.__press_cross_hair_button, fg="white",
                                            cursor="hand2", takefocus=0, relief=tk.RAISED)
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

        self.dragging = False
        self.drag_start_x = None
        
        self.__bind_events()
    def show_mask(self):
        self.loading_mask.place(relx=0, rely=0, relwidth=1, relheight=1, anchor="nw")
        self.loading_mask.lift()

    def hide_mask(self):
        self.loading_mask.place_forget()

    def new_data(self, stock_code):
        self.show_mask()
        self.stock_code = stock_code
        self.data.stock_code = stock_code
        self.data.load_data_csv()
        self.end_index = self.data.data['<DATE>'].max()
        self.start_index = self.end_index - pd.Timedelta(days=30)
        self.zoom_days = 30
        self.__refresh_figure()
        self.hide_mask()

    def __bind_events(self):
        self.frame_Kline.bind("<MouseWheel>", self.__scroll_event)
        self.frame_Kline.bind("<Button-1>", self.__click_event)
        self.frame_Kline.bind("<B1-Motion>", self.__drag_event)
        self.frame_Kline.bind("<ButtonRelease-1>", self.__release_event)
        self.frame_Kline.bind("<Motion>", self.__motion_event)
        self.frame_Kline.bind("<Configure>", self.__refresh_figure)
        self.bind("<Configure>", self.__refresh_frame)
        # self.cross_hair_button.bind("<Button-1>", self.__press_cross_hair_button)

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
            if self.day_line is not None:
                self.frame_Kline.delete(self.day_line)
                self.day_line = None
                self.day_info.place_forget()
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
        if self.data.data is None:
            return
        if self.day_line is not None:
            self.frame_Kline.delete(self.day_line)
        if self.cross_hair_button_flag:
            # x axis
            self.day_info.place_forget()
            x = event.x / self.frame_Kline.winfo_width()
            x *= self.zoom_days + 2
            x = round(x) - 1
            day = self.start_index + pd.Timedelta(days=x)
            x = (x+1) / (self.zoom_days + 2) * self.frame_Kline.winfo_width()
            self.day_line = self.frame_Kline.create_line(
                x, 0,
                x, self.frame_Kline.winfo_height(),
                fill="gray", width=1.5, dash=(2, 2)
            )
            self.day_info.config(text=day.strftime("%Y-%m-%d"))
            # print(self.day_info.winfo_x())
            if x - self.day_info.winfo_width()/2 < 0:
                self.day_info.place(x=self.day_info.winfo_width()/2, y=self.winfo_height(), anchor="s")
            elif x+self.day_info.winfo_width()/2 > self.frame_Kline.winfo_width():
                self.day_info.place(x=self.frame_Kline.winfo_width()-self.day_info.winfo_width()/2, y=self.winfo_height(), anchor="s")
            else:
                self.day_info.place(x=x, y=self.winfo_height(), anchor="s")
            
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
        if self.data.data is None:
            return
        self.dragging = True
        self.drag_start_x = event.x
    
    def __drag_event(self, event):
        if self.dragging:
            dx = (event.x - self.drag_start_x) * self.zoom_days / self.frame_Kline.winfo_width()
            if dx < 0:
                self.end_index = min(self.end_index - pd.Timedelta(days=dx), self.data.data['<DATE>'].max())
                self.start_index = self.end_index - pd.Timedelta(days=self.zoom_days)
            elif dx > 0:
                self.start_index = max(self.start_index - pd.Timedelta(days=dx), self.data.data['<DATE>'].min())
                self.end_index = self.start_index + pd.Timedelta(days=self.zoom_days)
            else:
                return
            self.__refresh_figure()
            self.drag_start_x = event.x
        self.__motion_event(event)
    
    def __release_event(self, event):
        self.dragging = False
        self.drag_start_x = None

    def __scroll_event(self, event):
        # """Scroll event to zoom in/out the figure."""
        if self.data.data is None:
            return
        x = event.x / self.frame_Kline.winfo_width()
        center_day = self.start_index + pd.Timedelta(days=x * (2 + (self.end_index - self.start_index).days))

        if event.delta < 0:
            self.start_index = min(center_day - pd.Timedelta(days=1.1 * (center_day - self.start_index).days),
                                   self.start_index-pd.Timedelta(days=1))
            self.end_index = max(center_day + pd.Timedelta(days=1.1 * (self.end_index - center_day).days),
                                   self.end_index+pd.Timedelta(days=1))
        else:
            if self.zoom_days < 4:
                return
            self.start_index = center_day - pd.Timedelta(days=max(0.9 * (center_day - self.start_index).days, 2))
            self.end_index = center_day + pd.Timedelta(days=max(0.9 * (self.end_index - center_day).days, 2))
        self.start_index = max(self.start_index, self.data.data['<DATE>'].min())
        self.end_index = min(self.end_index, self.data.data['<DATE>'].max())
        self.zoom_days = (self.end_index - self.start_index).days
        # if self.zoom_days < 3:
        #     self.zoom_days = 3
        #     self.start_index = self.end_index - pd.Timedelta(days=self.zoom_days)
        self.__refresh_figure()
        return

    def __refresh_figure(self, event=None):
        # print(self.winfo_width(), self.winfo_height())
        if self.data.data is None:
            return
        self.frame_Kline.delete("all")
        filtered_data = self.data.data[(self.data.data['<DATE>'] >= self.start_index.normalize()-pd.Timedelta(days=1)) & (self.data.data['<DATE>'] <= self.end_index.normalize()+pd.Timedelta(days=1))]
        if filtered_data.empty:
            return
        
        canvas_width = self.frame_Kline.winfo_width()
        canvas_height = self.frame_Kline.winfo_height()

        len_of_dates = self.zoom_days + 2
        y_min = min(filtered_data['<LOW>']*0.99)
        y_max = max(filtered_data['<HIGH>']*1.01)
        self.y_min = y_min
        self.y_max = y_max
        # print(filtered_data['<DATE>'].min(), filtered_data['<DATE>'].max())
        # print(self.start_index, self.end_index)

        for i, data in enumerate(filtered_data.iterrows()):
            date = data[1]['<DATE>']
            open_price = data[1]['<OPEN>']
            close_price = data[1]['<CLOSE>']
            high_price = data[1]['<HIGH>']
            low_price = data[1]['<LOW>']
            x = ((date - self.start_index.normalize()).days+1) / len_of_dates * canvas_width
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
            width = 0.7 * canvas_width / len_of_dates
            self.frame_Kline.create_rectangle(
                x - width / 2, y_open, x + width / 2, y_close,
                fill=color, outline=color
            )