#!/usr/bin/env python3
"""
Process data from 2026-02-06 in SharePoint
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from daily_reporter import DailyReporter

class CustomDateReporter(DailyReporter):
    def __init__(self, base_path, date):
        """Initialize with specific date and path"""
        self.base_path = Path(base_path)
        self.today_date = date
        self.report_date_folder = self.base_path / self.today_date

if __name__ == "__main__":
    print("🚀 Processing SharePoint data from 2026-02-06")
    
    base_path = Path("/Users/rishubatra/Library/CloudStorage/OneDrive-SharedLibraries-SinhalUdyogpvtltd/Communication site - Daily_SLA_Reporting")
    reporter = CustomDateReporter(base_path=base_path, date="2026-02-06")
    
    print(f"\n{'='*70}")
    print(f"Processing Report_1_Comms_Reporting for 2026-02-06")
    print(f"{'='*70}\n")
    
    success = reporter.process_comms_reporting()
    
    if success:
        print(f"\n✅ Processing completed!")
        print(f"📂 Check output files in:")
        print(f"   {base_path}/2026-02-06/Report_1_Comms_Reporting/DG*/output/")
    else:
        print(f"\n⚠️ Processing completed with some issues")
