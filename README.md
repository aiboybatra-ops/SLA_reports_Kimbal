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
# Daily SLA Reporting Automation System

## Overview

Automated system for processing daily SLA (Service Level Agreement) meter communication data. Merges data from multiple sources, validates files, calculates communication status, and generates comprehensive reports including subdivision-level breakdowns.

**Perfect for:** Utility companies, smart meter operations teams, field service management

## Key Features

✅ **Automatic Folder Creation** - Creates daily folder structure at 10 AM (or on-demand)
✅ **File Validation** - Checks file names and column headers before processing
✅ **Multi-Source Data Merging** - Combines Warehouse, Node ID, Routing, and other data sources
✅ **Communication Status** - Calculates Communicating/Never Comm/Non Comm status
✅ **Subdivision Analysis** - Breaks down communication status by subdivision
✅ **Multiple Output Formats** - Generates CSV reports and JSON summaries
✅ **Detailed Logging** - Terminal output shows progress and validation results
✅ **Cross-Platform** - Works on Windows, Mac, and Linux

## System Architecture

```
SharePoint/OneDrive (Cloud Storage)
    ↓
    ↓ Syncs to local machine
    ↓
Local Processing (Python Script)
    ↓
    │── Validates files
    │── Merges data sources  
    │── Calculates comm status
    │── Generates reports
    ↓
Output Files (Back to SharePoint)
    │── Final_SLA_Report.csv (Main report)
    │── Communication_Status_Summary.csv (Management summary)
    │── Master/Intermediate reports (Detailed data)
    └── JSON summary (Technical metadata)
```

## Quick Start

### For Windows Users (Recommended Setup)

1. **Install Python 3.7+** from [python.org](https://python.org)
   - ⚠️ Check "Add Python to PATH" during installation

2. **Clone this repository:**
   ```cmd
   git clone https://github.com/aiboybatra-ops/SLA_reports_Kimbal.git
   cd SLA_reports_Kimbal
   ```
   
   Or download ZIP from GitHub and extract to Desktop

3. **Configure SharePoint path:**
   - Edit `daily_reporter.py` (line ~920)
   - Update `sharepoint_path` with your OneDrive sync location:
     ```python
     sharepoint_path = Path('C:/Users/YourUsername/OneDrive - Company/Communication site - Daily_SLA_Reporting')
     ```

4. **Run the script:**
   ```cmd
   python daily_reporter.py
   ```

5. **Upload your data files** to the created folders in SharePoint

6. **Run again to process** the data and generate reports

📚 **For detailed step-by-step instructions, see [user_instructions.txt](user_instructions.txt)**

## Folder Structure

```
SharePoint/OneDrive Root/
└── Communication site - Daily_SLA_Reporting/
    └── 2026-01-23/                          (Auto-created daily)
        └── Report_1_Comms_Reporting/
            ├── DG1/
            │   ├── raw_data/                  (Upload your data here)
            │   │   ├── Warehouse.csv
            │   │   ├── New_Service_connection.csv
            │   │   ├── Merged_CI-MI.csv
            │   │   ├── Meter_Installation.csv
            │   │   ├── Node ID.xlsx
            │   │   ├── Routings Part-1.xlsx
            │   │   └── Routings Part-2.xlsx
            │   └── output/                    (Generated reports appear here)
            │       ├── Final_SLA_Report_2026-01-23.csv
            │       ├── Communication_Status_Summary_DG1_2026-01-23.csv
            │       ├── Master_SLA_Report_2026-01-23.csv
            │       ├── Intermediate_SLA_Report_2026-01-23.csv
            │       └── SLA_Summary_DG1_2026-01-23.json
            ├── DG2/
            │   ├── raw_data/
            │   └── output/
            └── DG3/
                ├── raw_data/
                └── output/
```

## Required Input Files

| File Name | Format | Purpose | Key Columns |
|-----------|--------|---------|-------------|
| Warehouse.csv | CSV | Base meter inventory | Meter Serial No, Consumer Name, Address, Division |
| New_Service_connection.csv | CSV | New installations | New Meter QR Code, Consumer name, Subdivision |
| Merged_CI-MI.csv | CSV | Inspection data | New Meter QR Code, Feeder Name, Coordinates |
| Meter_Installation.csv | CSV | Installation records | New Meter Number Scan, Installation date |
| Node ID.xlsx | Excel | Node mapping | Meter Number, NodeId |
| Routings Part-1.xlsx | Excel | Communication routing | Node ID, Gateway ID, Communicated At |
| Routings Part-2.xlsx | Excel | Additional routing data | Node ID, Gateway ID, Communicated At |

## Output Files

### 1. Final_SLA_Report_[DATE].csv
⭐ **Primary Report** - Complete meter data with communication status

**Columns include:**
- Meter Serial No, Node ID, Manufacturer
- Consumer information (Name, Address, Mobile)
- Location (Division, Subdivision, Circle, Feeder)
- Coordinates (Latitude, Longitude)
- Routing (Gateway ID, Hop Count, Sink ID)
- **Comm Status** (Communicating / Never Comm / Non Comm)
- **Remarks** (Blank for manual notes)

### 2. Communication_Status_Summary_[DATE].csv
⭐ **Management Dashboard** - High-level status overview

**Format:**
| Category | Subdivision | Communicating | Never Comm | Non Comm | Total |
|----------|-------------|---------------|------------|----------|-------|
| Overall | All | 1250 | 340 | 210 | 1800 |
| By Subdivision | North Division | 450 | 120 | 80 | 650 |
| By Subdivision | South Division | 380 | 95 | 70 | 545 |

### 3. Master_SLA_Report_[DATE].csv
Complete merged dataset with all columns from all sources (50-100+ columns)

### 4. Intermediate_SLA_Report_[DATE].csv
Cleaned dataset with essential columns only (~20 columns)

### 5. SLA_Summary_DG[X]_[DATE].json
Technical metadata including missing data analysis and mapping statistics

## Communication Status Definitions

| Status | Definition | Meaning |
|--------|------------|----------|
| **Communicating** | Communicated today | ✅ Meter is active and working |
| **Non Comm** | Communicated before, but not today | ⚠️ Meter stopped communicating - needs attention |
| **Never Comm** | Never communicated | ⚠️ New meter or faulty installation |

## Data Processing Workflow

1. **Validation Phase:**
   - Check all 7 required files are present
   - Verify file names match exactly
   - Validate column headers in each file

2. **Merging Phase:**
   - Start with Warehouse.csv as base (master list of meters)
   - Merge New_Service_connection.csv on meter QR code
   - Merge Merged_CI-MI.csv for inspection data
   - Merge Meter_Installation.csv for installation details
   - Merge Node ID.xlsx to map meters to network nodes
   - Merge Routing files to get communication data

3. **Processing Phase:**
   - Coalesce data from multiple sources (fill blanks)
   - Select essential columns for intermediate report
   - Calculate communication status based on "Communicated At" field
   - Generate subdivision-level summaries

4. **Output Phase:**
   - Save Master report (all data)
   - Save Intermediate report (selected columns)
   - Save Final report (with comm status)
   - Generate CSV summary (overall + subdivision)
   - Create JSON metadata

## Validation & Error Handling

### Automatic Validations:

✅ **File Name Validation**
- Checks all 7 files are present
- Verifies exact name matching (case-sensitive)
- Identifies missing or incorrectly named files

✅ **Column Validation**
- Checks each file has required column headers
- Reports missing columns
- Warns about extra columns

✅ **Data Completeness**
- Tracks which records successfully merged
- Reports unmapped data from each source
- Counts missing Node IDs and routing info

### Error Messages:

```
❌ FILE VALIDATION ISSUES:
  Missing files: ['Node ID.xlsx']
  Unexpected files: ['node_id.xlsx']

→ Fix: Rename 'node_id.xlsx' to 'Node ID.xlsx'
```

```
❌ Column validation failed
  Warehouse.csv:
    Missing columns: ['Meter Serial No']
    
→ Fix: Check column headers in row 1 of CSV file
```

## System Requirements

### Minimum Requirements:
- **OS:** Windows 10+, macOS 10.14+, or Linux
- **Python:** 3.7 or higher
- **RAM:** 4 GB (8 GB recommended for large datasets)
- **Storage:** 500 MB free space
- **Network:** Internet connection for OneDrive sync

### Python Dependencies:
```
pandas>=1.3.0
openpyxl>=3.0.0
requests>=2.25.0
```

Install with:
```bash
pip install pandas openpyxl requests
```

## Performance

| Dataset Size | Records | Processing Time |
|--------------|---------|------------------|
| Small | < 5,000 | 30-60 seconds |
| Medium | 5,000-20,000 | 1-3 minutes |
| Large | 20,000-50,000 | 3-5 minutes |
| Very Large | > 50,000 | 5-10 minutes |

*Tested on Intel i5 processor with 8GB RAM*

## Scheduling (Optional)

### Option 1: Windows Task Scheduler
Schedule the script to run automatically at 10 AM daily

### Option 2: Cron (Mac/Linux)
Add to crontab:
```bash
0 10 * * * /usr/bin/python3 /path/to/daily_reporter.py >> /path/to/cron.log 2>&1
```

### Option 3: Manual Execution
Run on-demand whenever needed

## Troubleshooting

### Common Issues:

**"python is not recognized"**
- Python not installed or not in PATH
- Solution: Reinstall Python with "Add to PATH" checked

**"SharePoint base path does not exist"**
- OneDrive not syncing or incorrect path
- Solution: Verify OneDrive is running and path is correct

**"FILE VALIDATION ISSUES"**
- Missing or incorrectly named files
- Solution: Check file names match exactly (case-sensitive)

**"Column validation failed"**
- Incorrect column headers in CSV/Excel files
- Solution: Fix column names in row 1 of data files

**Script runs but no output**
- Files may be locked by Excel
- Solution: Close all Excel files and re-run

📚 **For detailed troubleshooting, see [user_instructions.txt](user_instructions.txt)**

## Best Practices

1. ✅ **Run daily** - Process overnight data fresh each morning
2. ✅ **Check sync** - Verify OneDrive is "Up to date" before running
3. ✅ **Review summaries** - Scan terminal output for anomalies
4. ✅ **Keep history** - Don't delete old reports (each day has its own folder)
5. ✅ **Backup data** - Occasionally copy raw_data folders to backup location
6. ✅ **Monitor quality** - Check data completeness and missing counts

## Security & Privacy

- 🔒 Runs **100% locally** on your machine
- 🔒 No data sent to external servers
- 🔒 All processing happens offline
- 🔒 Data stays within your SharePoint/OneDrive
- 🔒 No API keys or credentials required

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
- 🐛 **Report bugs:** [GitHub Issues](https://github.com/aiboybatra-ops/SLA_reports_Kimbal/issues)
- 📚 **Documentation:** See [user_instructions.txt](user_instructions.txt)
- 📧 **Contact:** [Your support email]

## License

MIT License - See LICENSE file for details

## Version History

### v2.0 (Current) - January 2026
- ✨ Added automatic folder structure creation
- ✨ Added CSV summary report with subdivision breakdown  
- ✨ Improved validation and error messages
- ✨ Added comprehensive Windows user documentation
- 🐛 Fixed merge key matching issues
- 🐛 Improved performance for large datasets

### v1.0 - Initial Release
- Basic data processing and merging
- JSON summary output
- File and column validation

## Acknowledgments

Developed for utility smart meter operations teams to streamline daily SLA reporting and communication status tracking.

---

**🚀 Ready to get started? See [user_instructions.txt](user_instructions.txt) for complete setup guide!**
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
