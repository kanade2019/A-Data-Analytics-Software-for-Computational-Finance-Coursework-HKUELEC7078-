import tkinter as tk
from tkinter import ttk

class TechIndic(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.ma_bollinger = tk.StringVar(value="")
        self.vol_enabled = tk.BooleanVar(value=False)
        self.macd_enabled = tk.BooleanVar(value=False)
        self.kdj_enabled = tk.BooleanVar(value=False)
        self.rsi_enabled = tk.BooleanVar(value=False)

        # Store the value intended by the last click for each group
        self._toggled_ma_bollinger = ""
        self._toggled_vol_macd_kdj_rsi = ""

        separator = ttk.Separator(self, orient='horizontal')
        # Place separator in row 1, spanning across 2 columns, add vertical padding
        separator.place(relx=0.5, rely=0.1, relwidth=1, anchor="n", y=3)

        # --- MA / Bollinger Group ---
        self.ma_button = ttk.Radiobutton(self, text="MA", value="ma", variable=self.ma_bollinger,
                                         command=lambda: self._handle_radio_toggle(self.ma_bollinger, "ma"))
        self.ma_button.place(relx=0.05, rely=0.243, anchor="nw")

        self.bollinger_button = ttk.Radiobutton(self, text="Bollinger Bands", value="bollinger", variable=self.ma_bollinger,
                                                command=lambda: self._handle_radio_toggle(self.ma_bollinger, "bollinger"))
        self.bollinger_button.place(relx=0.5, rely=0.243, anchor="nw")

        separator2 = ttk.Separator(self, orient='horizontal')
        # Place separator in row 1, spanning across 2 columns, add vertical padding
        separator2.place(relx=0.5, rely=0.386, relwidth=1, anchor="n", y=3)
        self.mention_label = ttk.Label(self, text="Select up to three parameters", font=("Arial", 10, "bold"))
        self.mention_label.place(relx=0.5, rely=0.523, anchor="n")

        # --- Volume / MACD / KDJ / RSI Group ---
        self.vol_button = ttk.Checkbutton(self, text="Volume", variable=self.vol_enabled)
        self.vol_button.place(relx=0.05, rely=0.671, anchor="nw")
        self.macd_button = ttk.Checkbutton(self, text="MACD", variable=self.macd_enabled)
        self.macd_button.place(relx=0.5, rely=0.671, anchor="nw")
        self.kdj_button = ttk.Checkbutton(self, text="KDJ", variable=self.kdj_enabled)
        self.kdj_button.place(relx=0.05, rely=0.814, anchor="nw")
        self.rsi_button = ttk.Checkbutton(self, text="RSI", variable=self.rsi_enabled)
        self.rsi_button.place(relx=0.5, rely=0.814, anchor="nw")

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