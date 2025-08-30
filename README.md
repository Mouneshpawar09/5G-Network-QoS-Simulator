# 📡 5G Network QoS Simulator

A beginner-to-intermediate level **5G Network Simulator** built in **Python** that models multiple users connected to a base station.  
The simulator demonstrates **bandwidth allocation, MIMO channel effects, latency, and throughput** with visual plots and CSV reports.  

---

## 🚀 Features
- Simulates a **small-scale 5G Radio Access Network (RAN)** with multiple users (UEs).
- Implements **QoS metrics**: Throughput, Latency, and Signal-to-Noise Ratio (SNR).
- Supports simple **scheduling algorithms** (Equal Share, Proportional Fair).
- Models **MIMO channel gain** and **Rayleigh fading** for realistic wireless effects.
- Generates **CSV summary reports** and **visual plots (PNG)** automatically.
- Runs smoothly on **Windows 11** with open-source Python libraries.

---

## 📂 Project Structure
5g-sim/
├─ simulator.py # Main simulation script
├─ requirements.txt # Dependencies (numpy, pandas, matplotlib)
└─ output/ # Generated CSV + PNG results
1. Clone the repository:

   git clone https://github.com/Mouneshpawar09/5G-Network-QoS-Simulator
Create a virtual environment (recommended):
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

Install dependencies:

pip install -r requirements.txt
Run the simulator with:

python simulator.py
