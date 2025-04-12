import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class DrawFigure:
    def __init__(self, frame_figure):
        self.frame_figure = frame_figure
        self.fig = None
        self.start_index = None
        self.end_index = None
        self.data = None
        self.__bind_events()
    
    def __bind_events(self):
        # 滚轮事件
        self.frame_figure.bind("<MouseWheel>", self.__scroll_event)

    def __scroll_event(self, event):
        """Scroll event to zoom in/out the figure."""
        if event.delta > 0:
            self.start_index = max(0, self.start_index - 1)
            self.end_index = min(len(self.data), self.end_index + 1)
        else:
            self.start_index = min(len(self.data), self.start_index + 1)
            self.end_index = max(0, self.end_index - 1)
        self.Draw()

    def load_data_csv(self, company_name):
        """Load data into the figure."""
        """Date","Price","Open","High","Low","Vol.","Change %"""
        self.data = pd.read_csv(company_name + " Stock Price History.csv")
        self.start_index = 0
        self.end_index = len(self.data)

    def Draw(self):
        """Draw the figure."""
        if self.fig is not None:
            plt.close(self.fig)

        self.fig = plt.Figure(figsize=(25, 28), dpi=100, facecolor="white")
        self.fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.175, hspace=0.4, wspace=0.4)
        self.frame_figure.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_figure)
        self.frame_figure.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        ax = self.fig.add_subplot(111)
        ax.set_title("Stock Price")
        # ax.set_xlabel("Date")
        # ax.set_ylabel("Price")

        x = pd.to_datetime(self.data["Date"][self.start_index:self.end_index])
        y = self.data["Price"][self.start_index:self.end_index]
        ax.plot(x, y, label="Price", color="blue")

        # Set x-axis limits
        ax.set_xlim(x.min(), x.max())

        # Rotate x-axis labels
        ax.tick_params(axis='x', rotation=45)

        # Add grid
        ax.grid()

        # Add legend
        ax.legend()

        # Draw the figure
        self.frame_figure.canvas.draw()