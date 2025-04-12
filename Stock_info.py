import pandas as pd
import tkinter as tk

class StockInfo:
    def __init__(self, treeview):
        self.treeview = treeview
        self.data = pd.DataFrame(columns=["Name","Last","High","Low","Chg.","Chg. %","Vol.","Time"])

        self.treeview.tag_configure('positive', background='#CCFFCC')  # 浅绿色 - 正值变化
        self.treeview.tag_configure('negative', background='#FFCCCC')  # 浅红色 - 负值变化
        self.treeview.tag_configure('neutral', background='#FFFFFF')   # 白色 - 无变化

        # self.update_data()

    def update_data(self):
        """Update the listbox with the current data."""
        
        

    def load_from_csv(self, csv_file):
        """Load items from a CSV file into the listbox."""
        try:
            df = pd.read_csv(csv_file)
            for index, row in df.iterrows():
                item = [row["Name"], row["Last"], row["High"], row["Low"],
                        row["Chg."], row["Chg. %"], row["Vol."], row["Time"]]
                self.treeview.insert("", tk.END, values=item, tags=self.get_tags(row["Chg."]))
        except FileNotFoundError:
            print(f"File {csv_file} not found.")

    def get_tags(self, change):
        """Determine the tag based on the change value."""
        if change > 0:
            return ('positive',)
        elif change < 0:
            return ('negative',)
        else:
            return ('neutral',)

            