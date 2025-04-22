import pandas as pd
import tkinter as tk
import glob
import tkinter.font as tkFont
import tkinter.ttk as ttk
import os

class StockInfo(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.my_font = tkFont.Font(family="Calibri", size=10)
        self.style = ttk.Style()
        self.Stock_columns = ["Ticker","Chg.","Chg. %","Close","Open","High","Low","Vol."]
        self.style.configure("Treeview.Heading", font=tkFont.Font(family="Calibri", size=11, weight="bold"))
        self.treeview = ttk.Treeview(master=self, columns=self.Stock_columns, show="headings", height=self.winfo_height()*0.85)
        self.vsbar = ttk.Scrollbar(self, orient="vertical", command=self.treeview.yview)
        self.hsbar = ttk.Scrollbar(self, orient="horizontal", command=self.treeview.xview)

        self.search_entry = ttk.Entry(self, font=self.my_font, width=self.winfo_width(), justify="left")
        self.treeview.configure(yscrollcommand=self.vsbar.set, xscrollcommand=self.hsbar.set)
        
        # self.search_entry.place(relx=0, rely=0, relwidth=1, height=35, anchor="nw")
        # self.treeview.place(relx=0, rely=0.1, relwidth=0.95, relheight=0.85, anchor="nw")
        # self.vsbar.place(relx=1, rely=0.1, relwidth=0.05, relheight=0.85, anchor="ne")
        # self.hsbar.place(relx=0, rely=1, relwidth=0.95, relheight=0.05, anchor="sw")
        self.search_entry.pack(side="top", fill="x")
        self.vsbar.pack(side="right", fill="y")
        self.hsbar.pack(side="bottom", fill="x")
        self.treeview.pack(side="top", fill="both", expand=True)

        self.data = pd.DataFrame(columns=self.Stock_columns)
        self.column_widths = [50 for _ in range(len(self.data.columns))]

        self.treeview.tag_configure('positive', background='#CCFFCC', font=self.my_font)  # 浅绿色 - 正值变化
        self.treeview.tag_configure('negative', background='#FFCCCC', font=self.my_font)  # 浅红色 - 负值变化
        self.treeview.tag_configure('neutral', background='#FFFFFF', font=self.my_font)   # 白色 - 无变化

        self.name2code = {}
        self.code2name = {}
        self.load_code_map()
        self.load_from_csv(r"datas\d_hk_txt\data\daily\hk\hkex stocks")

        self.__show()

        # bind events
        self.search_entry.bind("<KeyRelease>", self.__search)

    def __search(self, event):
        """Search for a ticker in the treeview."""
        match_str = self.search_entry.get()
        if match_str != "":
            self.__show(match_str)
        else:
            self.__show()

    def load_code_map(self):
        """Load the code map from a CSV file."""
        try:
            df = pd.read_csv(r"datas\Stock Map.csv")
            for tiker, name in zip(df["<TICKER>"], df["<NAME>"]):
                self.name2code[name] = tiker
                self.code2name[tiker] = name
        except FileNotFoundError:
            print("Code map file not found.")

    def load_from_csv(self, csv_files):
        """Load items from a CSV file into the listbox."""
        try:
            for csv_file in glob.glob(csv_files + r"\*.txt"):
                df = pd.read_csv(csv_file, encoding='utf-8')
                # get last information
                last_info = df.iloc[-1]
                try:
                    self.data.loc[len(self.data)] = [
                        self.code2name[last_info["<TICKER>"]],
                        round(last_info["<CLOSE>"]-last_info["<OPEN>"], 2),
                        round((last_info["<CLOSE>"]-last_info["<OPEN>"])/last_info["<OPEN>"]*100, 2),
                        last_info["<CLOSE>"],
                        last_info["<OPEN>"],
                        last_info["<HIGH>"],
                        last_info["<LOW>"],
                        last_info["<VOL>"]
                    ]  
                except KeyError:
                    print(f"KeyError: {last_info["<TICKER>"]} not found in code map.")
                    continue
        except FileNotFoundError:
            print(f"Cannot find files in {csv_file}.")

    def get_tags(self, change):
        """Determine the tag based on the change value."""
        if change > 0:
            return ('positive',)
        elif change < 0:
            return ('negative',)
        else:
            return ('neutral',)
        
    def __show(self, match_str=None):
        for item in self.treeview.get_children():
            self.treeview.delete(item)
        if match_str is None:
            """Display the data in the treeview."""
            for data in self.data.values:
                data = list(data)
                for i in range(len(data)):
                    if isinstance(data[i], str):
                        self.column_widths[i] = max(self.my_font.measure(str(data[i])), self.column_widths[i])
                for i in range(len(self.column_widths)):
                    col = self.data.columns[i]
                    self.treeview.heading(col, text=col, anchor="center")
                    self.treeview.column(col, anchor="center", width=self.column_widths[i], minwidth=self.column_widths[i])
                tags = self.get_tags(data[1])
                self.treeview.insert("", "end", values=data, tags=tags)
        else:
            for data in self.data.values:
                data = list(data)
                ticker_name = data[0]
                ticker_code = self.name2code[data[0]]
                if match_str.lower() in ticker_name.lower() or match_str.lower() in ticker_code.lower():
                    tags = self.get_tags(data[1])
                    self.treeview.insert("", "end", values=data, tags=tags)