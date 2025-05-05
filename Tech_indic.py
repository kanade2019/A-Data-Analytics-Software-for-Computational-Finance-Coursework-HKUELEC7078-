import tkinter as tk
from tkinter import ttk

class TechIndic(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.ma_bollinger = tk.StringVar(value="")
        self.vol_macd_kdj_rsi = tk.StringVar(value="")

        # Store the value intended by the last click for each group
        self._toggled_ma_bollinger = ""
        self._toggled_vol_macd_kdj_rsi = ""

        separator = ttk.Separator(self, orient='horizontal')
        # Place separator in row 1, spanning across 2 columns, add vertical padding
        separator.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=10)

        # --- MA / Bollinger Group ---
        self.ma_button = ttk.Radiobutton(self, text="MA", value="ma", variable=self.ma_bollinger,
                                         command=lambda: self._handle_radio_toggle(self.ma_bollinger, "ma"))
        self.ma_button.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.bollinger_button = ttk.Radiobutton(self, text="Bollinger Bands", value="bollinger", variable=self.ma_bollinger,
                                                command=lambda: self._handle_radio_toggle(self.ma_bollinger, "bollinger"))
        self.bollinger_button.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        separator2 = ttk.Separator(self, orient='horizontal')
        # Place separator in row 1, spanning across 2 columns, add vertical padding
        separator2.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=10)

        # --- Volume / MACD / KDJ / RSI Group ---
        self.vol_button = ttk.Radiobutton(self, text="Volume", value="vol", variable=self.vol_macd_kdj_rsi,
                                          command=lambda: self._handle_radio_toggle(self.vol_macd_kdj_rsi, "vol"))
        self.vol_button.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.macd_button = ttk.Radiobutton(self, text="MACD", value="macd", variable=self.vol_macd_kdj_rsi,
                                           command=lambda: self._handle_radio_toggle(self.vol_macd_kdj_rsi, "macd"))
        self.macd_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.kdj_button = ttk.Radiobutton(self, text="KDJ", value="kdj", variable=self.vol_macd_kdj_rsi,
                                          command=lambda: self._handle_radio_toggle(self.vol_macd_kdj_rsi, "kdj"))
        self.kdj_button.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.rsi_button = ttk.Radiobutton(self, text="RSI", value="rsi", variable=self.vol_macd_kdj_rsi,
                                          command=lambda: self._handle_radio_toggle(self.vol_macd_kdj_rsi, "rsi"))
        self.rsi_button.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    def _handle_radio_toggle(self, variable, button_value):
        """
        Handles toggling behavior for Radiobuttons.
        If the clicked button's value was the intended value from the last click,
        it deselects the variable. Otherwise, it updates the intended value.
        """
        toggle_attr = ""
        # Determine which internal state variable to use
        if variable == self.ma_bollinger:
            toggle_attr = "_toggled_ma_bollinger"
        elif variable == self.vol_macd_kdj_rsi:
            toggle_attr = "_toggled_vol_macd_kdj_rsi"
        else:
            return # Should not happen

        previous_intended_value = getattr(self, toggle_attr)
        # The variable.get() value is the one *just set* by the Radiobutton click
        current_actual_value = variable.get()

        # Check if the button just set the variable AND the previous intention was the same value
        if current_actual_value == button_value and previous_intended_value == button_value:
            # Clicked the same selected button again -> Deselect
            variable.set("")
            setattr(self, toggle_attr, "") # Update intention to deselected
        else:
            # Clicked a new button or clicked a button after deselection -> Select
            # The variable is already set correctly by the radiobutton itself.
            # Just update our internal state tracking the intended value.
            setattr(self, toggle_attr, button_value) # Update intention to the new value

# Example usage (if running this file directly)
if __name__ == '__main__':
    root = tk.Tk()
    tech_indic_frame = TechIndic(root)
    tech_indic_frame.pack(padx=10, pady=10)

    # Optional: Add labels to show the current variable values
    tk.Label(root, text="MA/Bollinger Selection:").pack()
    ttk.Label(root, textvariable=tech_indic_frame.ma_bollinger).pack()
    tk.Label(root, text="Vol/MACD/KDJ/RSI Selection:").pack()
    ttk.Label(root, textvariable=tech_indic_frame.vol_macd_kdj_rsi).pack()

    root.mainloop()