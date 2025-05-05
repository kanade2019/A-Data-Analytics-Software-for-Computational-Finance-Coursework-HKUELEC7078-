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
from Tech_indic import TechIndic
from tkinter import messagebox

class Main_Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Computational Finance")
        self.width = 800
        self.height = 600
        self.geometry(f"{self.width}x{self.height}")
        self.configure(bg="white")

        # Left frame containing table, info panel, and indicators
        self.frame_left = ttk.Frame(self)
        self.frame_left.place(relx=0.025, rely=0.05, relwidth=0.3, relheight=0.9, anchor="nw")

        # Stock information table
        self.frame_table = StockInfo(self.frame_left)
        self.frame_table.place(relx=0, rely=0, relwidth=1, relheight=0.75, anchor="nw")

        # Single stock detailed information panel (initially hidden)
        self.frame_info = SingleInfo(self.frame_left)
        # self.frame_info.place(relx=0, rely=0.5, relwidth=1, relheight=0.25, anchor="nw") # Initial placement if shown
        self.frame_info.place_forget() # Hide initially
        self.frame_info.hidden = True # Flag to track visibility state

        # Technical indicators selection panel
        self.frame_indicators = TechIndic(self.frame_left)
        self.frame_indicators.place(relx=0, rely=0.75, relwidth=1, relheight=0.25, anchor="nw")

        # Right frame for displaying charts/figures
        self.frame_right = Figures(self)
        self.frame_right.place(relx=0.35, rely=0.05, relwidth=0.625, relheight=0.9, anchor="nw")

        self.__bind_events() # Bind UI events

    def __bind_events(self):
        """Binds UI events to their respective handler methods."""
        self.frame_info.close_button.bind("<Button-1>", self.__close_single_info)
        self.frame_table.treeview.bind("<ButtonRelease-1>", self.__select_company)
        self.frame_table.treeview.bind("<KeyRelease>", self.__select_company)
        # Trace changes in indicator selection variables
        self.frame_indicators.ma_bollinger.trace_add("write", self.__update_indicator)
        self.frame_indicators.vol_enabled.trace_add("write", self.__update_indicator)
        self.frame_indicators.macd_enabled.trace_add("write", self.__update_indicator)
        self.frame_indicators.kdj_enabled.trace_add("write", self.__update_indicator)
        self.frame_indicators.rsi_enabled.trace_add("write", self.__update_indicator)
        return

    def __update_indicator(self, *args):
        """Updates the technical indicators displayed on the chart."""
        selected_indicator = self.frame_indicators.ma_bollinger.get()
        # print(selected_indicator, selected_indicator2) # Debug print
        # Update the corresponding variables in the Figures frame
        self.frame_right.show_ma_bollinger.set(selected_indicator)
        len_of_indicators = 0
        if self.frame_indicators.vol_enabled.get() == True:
            len_of_indicators += 1
        if self.frame_indicators.macd_enabled.get() == True:
            len_of_indicators += 1
        if self.frame_indicators.kdj_enabled.get() == True:
            len_of_indicators += 1
        if self.frame_indicators.rsi_enabled.get() == True:
            len_of_indicators += 1
        if len_of_indicators > 3:
            # Find out which variable was just changed by checking the args[0] (variable name)
            var_name = args[0]
            if var_name == str(self.frame_indicators.vol_enabled):
                self.frame_indicators.vol_enabled.set(False)
            elif var_name == str(self.frame_indicators.macd_enabled):
                self.frame_indicators.macd_enabled.set(False)
            elif var_name == str(self.frame_indicators.kdj_enabled):
                self.frame_indicators.kdj_enabled.set(False)
            elif var_name == str(self.frame_indicators.rsi_enabled):
                self.frame_indicators.rsi_enabled.set(False)
            
            messagebox.showwarning("Warning", "Select up to three parameters, please cancel one parameter and select again.")
            return  # Exit early to prevent the rest of the function from executing
        else:
            if self.frame_indicators.vol_enabled.get() == True:
                self.frame_right.frame_enabled[0].set(True)
            else:
                self.frame_right.frame_enabled[0].set(False)
            if self.frame_indicators.macd_enabled.get() == True:
                self.frame_right.frame_enabled[1].set(True)
            else:
                self.frame_right.frame_enabled[1].set(False)
            if self.frame_indicators.kdj_enabled.get() == True:
                self.frame_right.frame_enabled[2].set(True)
            else:
                self.frame_right.frame_enabled[2].set(False)
            if self.frame_indicators.rsi_enabled.get() == True:
                self.frame_right.frame_enabled[3].set(True)
            else:
                self.frame_right.frame_enabled[3].set(False)
        # Update the chart with the selected indicators
            

    def __close_single_info(self, event):
        """Starts the animation to close the single stock info panel."""
        # Prevent re-triggering if animation is already in progress
        if hasattr(self, '_animation_in_progress') and self._animation_in_progress:
            return

        # Mark animation start
        self._animation_in_progress = True

        # Start the animation (encapsulate all parameters)
        self._animate_frame_transition(
            frames=[self.frame_table, self.frame_info],
            start_heights=[0.5, 0.25], # Current heights
            end_heights=[0.75, 0],     # Target heights
            start_y=[0, 0.5],          # Current y positions
            end_y=[0, 0.75],           # Target y positions (info panel moves down slightly before disappearing)
            duration=100,              # milliseconds
            easing="quad_out",
            on_complete=lambda: setattr(self, '_animation_in_progress', False) # Reset flag on completion
        )

        self.frame_info.hidden = True  # Mark info panel as hidden logically
        # Note: place_forget() is handled within the animation loop when height becomes near zero
        return

    def _animate_frame_transition(self, frames, start_heights, end_heights, start_y, end_y,
                                  duration=300, easing="quad_out", on_complete=None):
        """
        Animates the relative height and position of multiple frames.

        Args:
            frames: List of frame widgets to animate.
            start_heights/end_heights: Lists of starting and ending relative heights (0.0 to 1.0).
            start_y/end_y: Lists of starting and ending relative y positions (0.0 to 1.0).
            duration: Animation duration in milliseconds.
            easing: Type of easing function (e.g., "quad_out").
            on_complete: Optional callback function to execute when animation finishes.
        """
        # Local variables, not stored in the class instance
        fps = 60 # Target frames per second
        delay = round(1000 / fps) # Delay between frames in ms
        steps = int(duration / delay) # Total number of steps
        step = 0 # Current step counter

        def _easing_function(t, type="quad_out"):
            """Internal easing function."""
            if type == "quad_out":
                # Equation for quadratic ease-out
                return 1 - (1 - t) * (1 - t)
            # Add more easing types here if needed...
            return t # Linear easing as default

        # Internal animation step function
        def _animation_step():
            nonlocal step # Allow modification of the outer 'step' variable

            if step <= steps:
                # Calculate progress (0.0 to 1.0)
                progress = step / steps
                # Apply easing function to progress
                eased_progress = _easing_function(progress, easing)

                # Update all frames in the list
                for i, frame in enumerate(frames):
                    # Interpolate current height based on eased progress
                    current_height = start_heights[i] + eased_progress * (end_heights[i] - start_heights[i])
                    # Interpolate current y position based on eased progress
                    current_y = start_y[i] + eased_progress * (end_y[i] - start_y[i])

                    # Update frame layout using place geometry manager
                    if current_height > 0.001:  # Avoid layout issues with near-zero height
                        frame.place(relx=0, rely=current_y, relwidth=1, relheight=current_height, anchor="nw")
                    else:
                        # Hide the frame completely if height is effectively zero
                        frame.place_forget()

                step += 1 # Increment step counter
                # Schedule the next animation step after the calculated delay
                self.after(delay, _animation_step)
            else:
                # Animation finished
                if on_complete:
                    on_complete() # Execute the completion callback if provided

        # Start the animation loop
        _animation_step()

    def __select_company(self, event):
        """Handles company selection from the treeview."""
        item = self.frame_table.treeview.selection() # Get selected item ID(s)
        if item: # Check if an item is actually selected
            # Extract data from the selected treeview item
            ticker_name = self.frame_table.treeview.item(item[0], "value")[0]
            ticker_code = self.frame_table.name2code[ticker_name] # Get code from mapping
            change = self.frame_table.treeview.item(item[0], "value")[1]
            change2 = self.frame_table.treeview.item(item[0], "value")[2]
            open_price = self.frame_table.treeview.item(item[0], "value")[4]
            close_price = self.frame_table.treeview.item(item[0], "value")[3]
            low_price = self.frame_table.treeview.item(item[0], "value")[6]
            high_price = self.frame_table.treeview.item(item[0], "value")[5]
            volume = self.frame_table.treeview.item(item[0], "value")[7]

            # Update the information panel with the selected stock's data
            self.frame_info.update_info(ticker_name, ticker_code, change, change2, open_price, close_price, low_price, high_price, volume)

            # If the info panel is currently hidden, animate it to show
            if self.frame_info.hidden:
                # Prevent re-triggering if animation is already in progress
                if hasattr(self, '_animation_in_progress') and self._animation_in_progress:
                    return

                # Mark animation start
                self._animation_in_progress = True
                self.frame_info.hidden = False  # Mark info panel as visible logically
                # Place the info panel initially at its starting position (bottom, zero height)
                self.frame_info.place(relx=0, rely=0.75, relwidth=1, relheight=0, anchor="nw")

                # Start the animation to expand the info panel
                self._animate_frame_transition(
                    frames=[self.frame_table, self.frame_info],
                    start_heights=[0.75, 0],     # Current heights
                    end_heights=[0.5, 0.25],     # Target heights
                    start_y=[0, 0.75],           # Current y positions
                    end_y=[0, 0.5],              # Target y positions
                    duration=100,                # milliseconds
                    easing="quad_out",
                    on_complete=lambda: setattr(self, '_animation_in_progress', False) # Reset flag on completion
                )

            # Load and display new data in the chart frame
            self.frame_right.new_data(ticker_code)

        return # Indicate event handled (optional)

if __name__ == "__main__":
    wn = Main_Window() # Create the main application window
    wn.mainloop()      # Start the Tkinter event loop