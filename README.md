# Personnas: College Student Bandwidth Model

Python simulation model for 24-hour bandwidth consumption patterns of college students. Models device usage, application behavior, and network demand across a campus population.

## What It Does

- Simulates per-student bandwidth consumption in 30-minute intervals across a 24-hour period
- Models multiple device types (laptop, phone, tablet, gaming console, etc.)
- Supports multiple usage scenarios (typical day, exam week, move-in day, etc.)
- Exports results as CSV data and HTML visual reports
- Used to generate realistic traffic load inputs for the TAMU Campus Simulator

## Quick Start

### Requirements

```bash
pip install matplotlib numpy pandas
```

### Run the Model

```bash
python CollegeStudentBandwidthModel.py
```

Output files will be generated in the current directory:
- `cs_devices_[timestamp].csv` — per-device bandwidth breakdown
- `cs_apps_[timestamp].csv` — per-application bandwidth breakdown
- `cs_usage_[timestamp].csv` — hourly usage summary
- `cs_timeseries_[timestamp].csv` — full 30-minute interval time series
- `bandwidthv18.html` — visual report

## Output Files

| File | Description |
|------|-------------|
| `cs_devices_*.csv` | Bandwidth by device type over 24 hours |
| `cs_apps_*.csv` | Bandwidth by application category |
| `cs_usage_*.csv` | Aggregate hourly usage totals |
| `cs_timeseries_*.csv` | Full time series at 30-min resolution |
| `*.html` | Visual HTML report with charts |
| `Figure_1.png` | Matplotlib chart of bandwidth curves |

## Model Overview

The model simulates a single college student's bandwidth demand across 24 hours using:

- **Device inventory**: Laptop, smartphone, tablet, smart TV, gaming console
- **Usage patterns**: Class hours, sleep, peak evening usage, streaming behavior
- **Application mix**: Streaming video, social media, web browsing, cloud sync, gaming
- **Scenario management**: Save and load different usage scenarios via JSON

### Key Parameters

```python
model = CollegeStudentBandwidthModel()

# Adjust student profile
model.set_device_parameters(...)

# Run simulation
model.simulate()

# Export results
model.export_csv()
model.generate_report()
```

## Scenarios

The model supports named scenarios for comparing different usage profiles:

```python
# Load a saved scenario
model.load_scenario('scenario_my_scene_1_[timestamp].csv')
```

Scenario files are prefixed `scenario_` and saved with timestamps.

## Integration with Campus Simulator

Bandwidth model outputs feed into [Campus-Sim](https://github.com/mtuckAI/Campus-Sim) to simulate realistic per-building network demand across different times of day and student populations.

## Version History

Version history is tracked via git. Current version: **v18** (February 2026).

## Contact

TAMU WiFi Team
