import tkinter as tk
import pandas as pd
from Stock_info import StockInfo
import tkinter.ttk as ttk
from draw_figure import DrawFigure

if __name__ == "__main__":
    wn = tk.Tk()
    wn.title("Computational Finance")
    wn.geometry("800x600")
    wn.configure(bg="white")

    h, w = wn.winfo_screenheight(), wn.winfo_screenwidth()

    # Create treeview with a scrollbar
    frame_table = tk.Frame(wn)
    frame_table.place(relx=0.025, rely=0.05, relwidth=0.3, relheight=0.9, anchor="nw")
    Stock_columns = ["Name", "Last", "High", "Low", "Chg.", "Chg. %", "Vol.", "Time"]
    yscrollbar = tk.Scrollbar(frame_table, orient="vertical")
    tv = ttk.Treeview(master=frame_table, columns=Stock_columns, show="headings", yscrollcommand=yscrollbar.set)
    tv.pack(fill="both", expand=True)
    for col in Stock_columns:
        tv.heading(col, text=col, anchor="center")
        tv.column(col, anchor="center", width=tv.winfo_width() // len(Stock_columns))
    yscrollbar.config(command=tv.yview)
    stki = StockInfo(tv)
    stki.load_from_csv("Stock Quotes.csv")

    # Create a frame show the figure
    frame_figure = tk.Frame(wn)
    frame_figure.place(relx=0.35, rely=0.05, relwidth=0.625, relheight=0.75, anchor="nw")
    stkf = DrawFigure(frame_figure)
    stkf.load_data_csv("Boeing")
    stkf.Draw()

    frame_indicators = tk.Frame(wn)
    frame_indicators.place(relx=0.35, rely=0.825, relwidth=0.625, relheight=0.125, anchor="nw")


    wn.mainloop()