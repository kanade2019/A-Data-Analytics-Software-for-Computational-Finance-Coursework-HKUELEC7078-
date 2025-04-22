import tkinter as tk
import pandas as pd
from Stock_info import StockInfo
import tkinter.ttk as ttk
from draw_figure import Figures
from Single_info import SingleInfo
import math
import time
from data import Data
import threading

class Main_Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Computational Finance")
        self.geometry("800x600")
        self.configure(bg="white")

        self.frame_left = ttk.Frame(self)
        self.frame_left.place(relx=0.025, rely=0.05, relwidth=0.3, relheight=0.9, anchor="nw")
        self.frame_table = StockInfo(self.frame_left)
        self.frame_table.place(relx=0, rely=0, relwidth=1, relheight=0.75, anchor="nw")
        self.frame_info = SingleInfo(self.frame_left)
        # self.frame_info.place(relx=0, rely=0.5, relwidth=1, relheight=0.25, anchor="nw")
        self.frame_info.place_forget()
        self.frame_info.hidden = True
        self.frame_indicators = ttk.Frame(self.frame_left)
        self.frame_indicators.place(relx=0, rely=0.75, relwidth=1, relheight=0.25, anchor="nw")

        self.frame_right = Figures(self)
        self.frame_right.place(relx=0.35, rely=0.05, relwidth=0.625, relheight=0.9, anchor="nw")

        self.__bind_events()

    def __bind_events(self):
        self.frame_info.close_button.bind("<Button-1>", self.__close_single_info)
        self.frame_table.treeview.bind("<ButtonRelease-1>", self.__select_company)
        self.frame_table.treeview.bind("<KeyRelease>", self.__select_company)
        return

    def __close_single_info(self, event):
        """开始关闭动画"""
        # 防止重复触发
        if hasattr(self, '_animation_in_progress') and self._animation_in_progress:
            return
            
        # 标记动画开始
        self._animation_in_progress = True
        
        # 开始动画 (封装所有参数)
        self._animate_frame_transition(
            frames=[self.frame_table, self.frame_info],
            start_heights=[0.5, 0.25],
            end_heights=[0.75, 0],
            start_y=[0, 0.5],
            end_y=[0, 0.75],
            duration=100,  # 毫秒
            easing="quad_out"
        )

        self.frame_info.hidden = True  # 隐藏信息面板
        self.frame_info.place_forget()
        self._animation_in_progress = False  # 动画完成后重置标志
        return

    def _animate_frame_transition(self, frames, start_heights, end_heights, start_y, end_y,
                                  duration=300, easing="quad_out", on_complete=None):
        """
        通用动画函数，避免存储大量状态变量
        
        参数:
            frames: 要动画的框架列表
            start_heights/end_heights: 起始和结束高度列表
            duration: 动画持续时间(毫秒)
            easing: 缓动函数类型
            on_complete: 动画完成时的回调函数
        """
        # 本地变量，不存储在类中
        steps = int(duration / 16)  # ~60fps
        step = 0
        
        def _easing_function(t, type="quad_out"):
            """内部缓动函数"""
            if type == "quad_out":
                return 1 - (1 - t) * (1 - t)
            # 可以添加更多缓动类型...
            return t
        
        # 内部动画步骤函数
        def _animation_step():
            nonlocal step
            
            if step <= steps:
                # 计算进度
                progress = step / steps
                eased = _easing_function(progress, easing)
                
                # 更新所有框架
                for i, frame in enumerate(frames):
                    # 计算当前高度
                    height = start_heights[i] + eased * (end_heights[i] - start_heights[i])
                    y_offset = start_y[i] + eased * (end_y[i] - start_y[i])
                    
                    # 更新布局
                    if height > 0.001:  # 避免极小值导致布局问题
                        frame.place(relx=0, rely=y_offset, relwidth=1, relheight=height, anchor="nw")
                        y_offset += height
                    else:
                        frame.place_forget()
                
                step += 1
                self.after(16, _animation_step)  # ~60fps
            else:
                # 动画完成
                if on_complete:
                    on_complete()
        
        # 启动动画
        _animation_step()

    def __select_company(self, event):
        # 您的选择公司代码...
        item = self.frame_table.treeview.selection()
        if item:
            ticker_name = self.frame_table.treeview.item(item[0], "value")[0]
            ticker_code = self.frame_table.name2code[ticker_name]
            change = self.frame_table.treeview.item(item[0], "value")[1]
            change2 = self.frame_table.treeview.item(item[0], "value")[2]
            open_price = self.frame_table.treeview.item(item[0], "value")[3]
            close_price = self.frame_table.treeview.item(item[0], "value")[4]
            low_price = self.frame_table.treeview.item(item[0], "value")[5]
            high_price = self.frame_table.treeview.item(item[0], "value")[6]
            volume = self.frame_table.treeview.item(item[0], "value")[7]
            # 更新信息面板
            self.frame_info.update_info(ticker_name, ticker_code, change, change2, open_price, close_price, low_price, high_price, volume)
            # 更新图表
            # self.frame_right.load_data_csv(ticker_code)
            # self.frame_right.Draw()
            def load_data():
                self.after(0, self.frame_right.show_mask)
                self.frame_right.stock_code = ticker_code
                self.frame_right.data.stock_code = ticker_code
                self.frame_right.data.load_data_csv()
                # 在主线程中更新UI
                self.after(0, self.frame_right.new_data)
                self.after(0, self.frame_right.hide_mask)
            
            # 启动数据加载线程
            threading.Thread(target=load_data, daemon=True).start()

        if self.frame_info.hidden:
            # 防止重复触发
            if hasattr(self, '_animation_in_progress') and self._animation_in_progress:
                return
                
            # 标记动画开始
            self._animation_in_progress = True
            self.frame_info.hidden = False  # 显示信息面板
            self.frame_info.place(relx=0, rely=0.75, relwidth=1, relheight=0, anchor="nw")

            # 开始动画
            self._animate_frame_transition(
                frames=[self.frame_table, self.frame_info],
                start_heights=[0.75, 0],
                end_heights=[0.5, 0.25],
                start_y=[0, 0.75],
                end_y=[0, 0.5],
                duration=100,  # 毫秒
                easing="quad_out"
            )
            self._animation_in_progress = False
        return

if __name__ == "__main__":
    wn = Main_Window()
    wn.mainloop()