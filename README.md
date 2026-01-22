<<<<<<< HEAD
# SLA_reports_Kimbal
=======
# Daily SLA Reporting Automation System

## Structure
```
DailySLAReporting/
├── daily_reporter.py          # Main automation script
├── 2026-01-22/               # Today's date folder (auto-created)
│   └── Report_1_Comms_Reporting/
│       ├── raw_data/         # Place your raw files here
│       └── output/           # Final reports will be saved here
└── README.md
```

## How It Works

1. **Automatic Date Detection**: The system automatically uses today's date (2026-01-22)
2. **Raw Data Location**: Place raw data files in `[DATE]/Report_1_Comms_Reporting/raw_data/`
3. **One-Time Daily Run**: Execute `python daily_reporter.py` once per day
4. **Output Generation**: Final reports will be saved in `[DATE]/Report_1_Comms_Reporting/output/`

## Quick Start

1. Place your raw data files in the `raw_data` folder
2. Run the script:
   ```bash
   python daily_reporter.py
   ```
3. Check output files in the `output` folder

## Next Steps

We'll configure this for your specific data format and processing logic.
>>>>>>> f15a250 (Initial commit: Daily SLA Reporting System with file validation and summary generation)
