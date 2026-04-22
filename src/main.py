import multiprocessing
import sys
import os

# Ensure the parent directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.gui import BurnInApp

def main():
    if sys.platform.startswith('win'):
        multiprocessing.freeze_support()
        
    app = BurnInApp()
    app.mainloop()

if __name__ == "__main__":
    main()
