import platform
import os
import urllib.request
import zipfile
import subprocess
import time

def setup_hardware_monitor():
    """
    Downloads and starts LibreHardwareMonitor on Windows to ensure accurate 
    temperature readings via the root\\LibreHardwareMonitor WMI namespace.
    """
    if platform.system() != 'Windows':
        return
        
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lhm_dir = os.path.join(base_dir, "LibreHardwareMonitor")
    lhm_exe = os.path.join(lhm_dir, "LibreHardwareMonitor.exe")
    
    # Download and extract if missing
    if not os.path.exists(lhm_exe):
        try:
            print("Downloading LibreHardwareMonitor for accurate sensors...")
            url = "https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/download/v0.9.3/LibreHardwareMonitor-0.9.3.zip"
            zip_path = os.path.join(base_dir, "LHM.zip")
            
            urllib.request.urlretrieve(url, zip_path)
            
            print("Extracting LibreHardwareMonitor...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(lhm_dir)
                
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except Exception as e:
            print(f"Failed to setup LHM: {e}")
            return
            
    # Check if already running to avoid multiple instances
    try:
        output = subprocess.check_output('tasklist', shell=True).decode('utf-8', errors='ignore')
        if "LibreHardwareMonitor.exe" in output:
            return
    except Exception:
        pass
        
    # Start the process in the background
    try:
        print("Starting LibreHardwareMonitor...")
        # 0x08000000 is CREATE_NO_WINDOW
        subprocess.Popen([lhm_exe], creationflags=0x08000000)
        # Give it a moment to initialize the WMI namespace
        time.sleep(3) 
    except Exception as e:
        print(f"Failed to start LHM: {e}")
