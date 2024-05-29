from datetime import datetime
import tkinter as tk
from summary_extract.summary_gui import summaryGUI

if __name__ == '__main__':
    start_time = datetime.now()
    window = tk.Tk()
    app = summaryGUI(window)
    window.mainloop()
    print(f"Runtime of the program: {datetime.now() - start_time}")