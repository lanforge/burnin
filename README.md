# LANForge Burn-In Tester

A custom-built PC burn-in testing suite designed specifically for LANForge systems. 
It heavily stresses the CPU, RAM, and GPU to ensure system stability before shipping.

## Features

- **Phase 1: Monitor** - Tracks real-time CPU & GPU usage, and maximum temperatures.
- **Phase 2: CPU/RAM Burner** - Maxes out all logical CPU cores and allocates large blocks of RAM.
- **Phase 3: GPU Burner** - Utilizes PyOpenCL (or numpy fallback) to perform heavy parallel matrix computations on the GPU.
- **Phase 4: Crypto Payload** - Simulates SHA-256 crypto mining to intensively test the CPU under prolonged, consistent hashing workloads.
- **Certificate Generation** - Automatically gathers system specs (Hostname, OS, CPU, RAM, GPU), maximum recorded temperatures, and duration, and sends a JSON payload to your custom Database API.

## Requirements

Ensure you have Python 3.8+ installed on the system.

```bash
pip install -r requirements.txt
```

*(Note: PyOpenCL may require standard OpenCL drivers installed on the system, which are usually included with NVIDIA/AMD/Intel graphics drivers.)*

## How to Run

Simply execute the main file:

```bash
python src/main.py
```

## How to Package as an Executable (Windows)

To deploy this to newly built LANForge PCs without installing Python every time, you can package it into a standalone `.exe`:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the `.exe`:
```bash
pyinstaller --noconsole --onefile src/main.py
```

The resulting `main.exe` will be found in the `dist` folder.
