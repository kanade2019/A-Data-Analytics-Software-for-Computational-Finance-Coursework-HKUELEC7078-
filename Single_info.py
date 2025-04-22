import tkinter as tk

class SingleInfo(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)  # 添加背景色
        self.hidden = False
        self.master = master
        # self.configure(highlightbackground="gray", highlightthickness=1)  # 添加边框

        # 设置默认数据以便可视化
        self.label_ticker_name = tk.Label(self, text="N/A", font=("Arial", 15, "bold"))
        self.label_ticker_code = tk.Label(self, text="N/A", font=("Arial", 12, "bold"))
        self.label_change = tk.Label(self, text="Chg\tChg%", font=("Arial", 12))
        self.label_open = tk.Label(self, text="Open: N/A", font=("Arial", 10))
        self.label_close = tk.Label(self, text="Close: N/A", font=("Arial", 10))
        self.label_low = tk.Label(self, text="Low: N/A", font=("Arial", 10))
        self.label_high = tk.Label(self, text="High: N/A", font=("Arial", 10))
        self.label_vol = tk.Label(self, text="Vol: N/A", font=("Arial", 10))

        self.label_ticker_name.place(relx=0.5, rely=0, anchor="n")
        self.label_ticker_code.place(relx=0.5, rely=0.175, anchor="n")
        self.label_change.place(relx=0.5, rely=0.35, anchor="n")
        self.label_open.place(relx=0.1, rely=0.5, anchor="nw")
        self.label_close.place(relx=0.6, rely=0.5, anchor="nw")
        self.label_low.place(relx=0.1, rely=0.667, anchor="nw")
        self.label_high.place(relx=0.6, rely=0.667, anchor="nw")
        self.label_vol.place(relx=0.5, rely=0.833, anchor="n")

        self.close_button = tk.Button(self, text="x", font=("Arial", 10), justify="center")
        self.close_button.place(relx=1, rely=0, relheight=0.178, relwidth=0.1, anchor="ne")
    
    def update_info(self, ticker_name, ticker_code, change, change2, open_price, close_price, low_price, high_price, volume):
        """更新显示的股票信息"""
        self.label_ticker_name.config(text=ticker_name)
        self.label_ticker_code.config(text=ticker_code)
        self.label_change.config(text="Chg: " + change + '(' + change2 + '%)')
        self.label_open.config(text=f"Open: {open_price}")
        self.label_close.config(text=f"Close: {close_price}")
        self.label_low.config(text=f"Low: {low_price}")
        self.label_high.config(text=f"High: {high_price}")
        self.label_vol.config(text=f"Vol: {volume}")

    def __quit(self):
        return