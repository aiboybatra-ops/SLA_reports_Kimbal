#!/usr/bin/env python3
"""
Process 2026-02-12 data for DG2 only
"""

from daily_reporter import DailyReporter
from pathlib import Path

if __name__ == "__main__":
    # Override date and path for historical processing
    base_path = Path("/Users/rishubatra/Library/CloudStorage/OneDrive-SharedLibraries-SinhalUdyogpvtltd/Communication site - Daily_SLA_Reporting")
    date = "2026-02-12"
    
    print(f"🚀 Processing data for {date} - DG2 only")
    print(f"Base path: {base_path}")
    print(f"{'='*70}\n")
    
    # Create reporter instance with base path
    reporter = DailyReporter(base_path=str(base_path))
    
    # Override the date to process historical data
    reporter.today_date = date
    reporter.report_date_folder = reporter.base_path / date
    
    # Temporarily modify the get_dg_report_structures to only return DG2
    original_get_dg = reporter.get_dg_report_structures
    
    def get_dg2_only(report_name="Report_1_Comms_Reporting", dg_pattern="DG*"):
        all_dgs = original_get_dg(report_name, dg_pattern)
        # Filter to only DG2
        return {k: v for k, v in all_dgs.items() if k == "DG2"}
    
    reporter.get_dg_report_structures = get_dg2_only
    
    # Process (will only process DG2 now)
    reporter.process_comms_reporting()
