import PyInstaller.__main__
import customtkinter
import os
import shutil
import platform

print("Cleaning old broken builds...")
# Nuke the old cache to guarantee a fresh compile
for item in ['build', 'dist', 'main.spec', 'src/main.spec']:
    if os.path.exists(item):
        if os.path.isdir(item):
            shutil.rmtree(item)
        else:
            os.remove(item)

# Find the exact physical folder of CustomTkinter on your PC
ctk_path = os.path.dirname(customtkinter.__file__)
print(f"Found CustomTkinter at: {ctk_path}")

# Fix the separator string based on the OS (Windows = ;, Mac/Linux = :)
separator = ';' if platform.system() == 'Windows' else ':'

print("Starting aggressive PyInstaller build...")

# Run PyInstaller programmatically with hardcoded paths and hidden imports
PyInstaller.__main__.run([
    'src/main.py',
    '--onefile',
    f'--add-data={ctk_path}{separator}customtkinter/', # Dynamically injects ; or :
    '--hidden-import=customtkinter',
    '--hidden-import=numpy',
    '--hidden-import=psutil',
    '--hidden-import=GPUtil',
    '--hidden-import=pyopencl',
    '--hidden-import=requests',
    '--clean'
])

print("\nBuild complete! Your executable is in the 'dist' folder.")