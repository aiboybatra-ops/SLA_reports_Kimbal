#!/usr/bin/env python3
"""
Generate simplified comm status reports for 2026-02-12 DG2
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

# Import the generate_comm_summaries function
sys.path.insert(0, str(Path(__file__).parent))
from generate_summaries import generate_comm_summaries

if __name__ == "__main__":
    base_path = Path("/Users/rishubatra/Library/CloudStorage/OneDrive-SharedLibraries-SinhalUdyogpvtltd/Communication site - Daily_SLA_Reporting")
    date = "2026-02-12"
    
    print(f"🚀 Generating Simplified Comm Status Reports for {date} - DG2")
    print(f"{'='*70}\n")
    
    report_folder = base_path / date / "Report_1_Comms_Reporting"
    dg_name = "DG2"
    
    dg_folder = report_folder / dg_name
    output_dir = dg_folder / "output"
    final_report = output_dir / f"Final_SLA_Report_{date}.csv"
    
    if not final_report.exists():
        print(f"❌ Final_SLA_Report not found at {final_report}")
        sys.exit(1)
    
    print(f"{'='*70}")
    print(f"Processing {dg_name}")
    print(f"{'='*70}")
    
    result = generate_comm_summaries(final_report, output_dir, dg_name, date)
    
    print(f"\n{'='*70}")
    print(f"✅ Simplified reports generated successfully for {dg_name}!")
    print(f"{'='*70}")
