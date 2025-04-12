import tkinter as tk
import pandas as pd
from Stock_info import StockInfo
import tkinter.ttk as ttk
from draw_figure import DrawFigure

class Main_Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Computational Finance")
        self.geometry("800x600")
        self.configure(bg="white")

        self.frame_table = tk.Frame(self)
        self.frame_table.place(relx=0.025, rely=0.05, relwidth=0.3, relheight=0.9, anchor="nw")
        self.yscrollbar = tk.Scrollbar(self.frame_table, orient="vertical")
        self.Stock_columns = ["Name", "Last", "High", "Low", "Chg.", "Chg. %", "Vol.", "Time"]
        self.tv = ttk.Treeview(master=self.frame_table, columns=self.Stock_columns, show="headings", yscrollcommand=self.yscrollbar.set)
        self.tv.pack(fill="both", expand=True)
        self.stki = StockInfo(self.tv)
        self.frame_figure = tk.Frame(self)
        self.frame_figure.place(relx=0.35, rely=0.05, relwidth=0.625, relheight=0.75, anchor="nw")
        self.stkf = DrawFigure(self.frame_figure)
        self.frame_indicators = tk.Frame(self)
        self.frame_indicators.place(relx=0.35, rely=0.825, relwidth=0.625, relheight=0.125, anchor="nw")

        self.__bind_events()

        for col in self.Stock_columns:
            self.tv.heading(col, text=col, anchor="center")
            self.tv.column(col, anchor="center", width=self.tv.winfo_width() // len(self.Stock_columns))
        self.yscrollbar.config(command=self.tv.yview)
        self.stki.load_from_csv("Stock Quotes.csv")

        # Create a frame show the figure
        # self.stkf.load_data_csv("Boeing")
        # self.stkf.Draw()

    def __bind_events(self):
        self.tv.bind("<Double-1>", self.__select_company)


    def __select_company(self, event):
        item = self.tv.selection()
        if item:
            company_name = self.tv.item(item[0], "values")[0]
            try:
                self.stkf.load_data_csv(company_name)
                self.stkf.Draw()
            except FileNotFoundError:
                print(f"File {company_name} not found.")
        return

if __name__ == "__main__":
    wn = Main_Window()
    wn.mainloop()