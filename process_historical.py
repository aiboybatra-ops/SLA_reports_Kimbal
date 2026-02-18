#!/usr/bin/env python3
"""
Process historical data from 2026-01-22
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from daily_reporter import DailyReporter

# Override the base path and date
class HistoricalReporter(DailyReporter):
    def __init__(self, base_path, date):
        """Initialize with specific date"""
        self.base_path = Path(base_path)
        self.today_date = date
        self.report_date_folder = self.base_path / self.today_date

if __name__ == "__main__":
    print("🚀 Processing historical data from 2026-01-22")
    
    base_path = Path(__file__).parent
    reporter = HistoricalReporter(base_path=base_path, date="2026-01-22")
    
    # Process Report_1_Comms_Reporting
    print(f"\n{'='*60}")
    print(f"Processing Report_1_Comms_Reporting for 2026-01-22")
    print(f"{'='*60}\n")
    
    success = reporter.process_comms_reporting()
    
    if success:
        print(f"\n✅ Historical data processing completed!")
        print(f"📂 Check output files in: {base_path}/2026-01-22/Report_1_Comms_Reporting/DG*/output/")
    else:
        print(f"\n⚠️ Processing completed with some issues")
