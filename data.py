import numpy as np
import pandas as pd

class data():
    def __init__(self, stock_name=None, stock_code=None):
        self.stock_name = stock_name
        self.stock_code = stock_code
        self.data = pd.DataFrame(columns=["Date","Price","Open","High","Low","Vol.","Change %"])
        self.start_index = 0.0
        self.end_index = 1.0