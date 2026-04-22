import multiprocessing
import sys
import os

# Ensure the parent directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.hardware_setup import setup_hardware_monitor
from src.gui import BurnInApp

def main():
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
        
    # Auto-start LibreHardwareMonitor to guarantee accurate temperatures
    setup_hardware_monitor()
        
    app = BurnInApp()
    app.mainloop()

if __name__ == "__main__":
    main()
