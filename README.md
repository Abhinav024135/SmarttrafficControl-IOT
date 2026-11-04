# Smart Traffic Light Control System

**Project 12 | HCLTech Career Shaper Programme | Embedded IoT**

A browser-based academic prototype demonstrating traffic monitoring, rule-based adaptive signal timing, emergency-vehicle priority workflows, intersection summaries and dataset analytics.

## Current implementation status
This deliverable is a **software simulation**, not a physical STM32 traffic controller. The dashboard reads the supplied CSV and generates session-local simulated traffic cycles. No ultrasonic sensor, STM32 board, LED signal, 7-segment display, fingerprint module, keypad or Bluetooth/Wi-Fi module is connected.

## Technology
- Python
- Streamlit
- Pandas and NumPy
- Plotly
- Visual Studio Code

## Run on Windows
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Dashboard pages
1. Overview — KPI cards and traffic charts.
2. Live Traffic Monitoring — lane table, intersection filter and generated traffic cycles.
3. Adaptive Signal Control — low/medium/high rule-based green-time recommendations and automatic/manual mode.
4. Emergency Management — dataset emergency events and manual simulated emergency trigger.
5. Intersection Management — intersection-level and lane-level summaries.
6. Dataset Analytics — preview, statistics, missing/duplicate checks, five Plotly charts and cleaned CSV download.
7. Security & Settings — simulated fingerprint/keypad status and local demonstration authentication.

## Dataset
The supplied dataset contains 500 rows and 8 fields:
`timestamp`, `intersection_id`, `lane_id`, `vehicle_count`, `green_duration_s`, `red_duration_s`, `peak_hour`, `emergency_flag`.

The original data is retained in `data/raw/dataset.csv`. A conservative cleaned copy is in `data/processed/cleaned_dataset.csv`. Original field names are preserved.

## Adaptive timing demonstration
- Low traffic (<8 vehicles): 15 seconds
- Medium traffic (8–17): 28 seconds
- High traffic (>=18): 48 seconds
- Configurable minimum/maximum green time clips the recommendation.

These are illustrative settings only, not validated traffic engineering timings. A real installation needs phase/conflict modelling, fail-safe interlocks, clearance intervals, hardware-in-the-loop testing and approval by qualified traffic engineers.

## Architecture (intended hardware)
Ultrasonic vehicle sensors → STM32 → vehicle count/density calculation → adaptive signal logic → traffic LEDs and 7-segment timer → Bluetooth/Wi-Fi → Python/IoT interface → Streamlit dashboard. Emergency detection and authentication are additional inputs.

Only the Python/Streamlit dashboard and software simulation are implemented here. Hardware and wireless interfaces are future integration work.

## Folder structure
- `app.py` — Streamlit application
- `requirements.txt` — Python dependencies
- `data/raw/` — original CSV and data dictionary
- `data/processed/` — cleaned CSV
- `analytics/traffic_analysis.py` — reproducible EDA charts
- `docs/` — architecture, working principle, tests and demo notes
- `firmware/` — STM32 integration reference

## Privacy and ethics
The supplied dataset is aggregate traffic-log data. Do not add number-plate images, identifiable camera footage or personal information without lawful authority and appropriate safeguards. The demo does not capture camera imagery or biometric data.
