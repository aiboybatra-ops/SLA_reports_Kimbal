#!/usr/bin/env python3
"""
Generate simplified comm status reports from existing Final_SLA_Report files
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json

def generate_comm_summaries(final_report_path, output_dir, dg_name, date):
    """Generate simplified comm status summary reports from Final SLA Report"""
    
    print(f"📊 Reading Final SLA Report: {final_report_path.name}")
    df_final = pd.read_csv(final_report_path)
    
    print(f"   Total records: {len(df_final)}")
    
    # Calculate overall summary
    total_records = len(df_final)
    comm_counts = df_final["Comm Status"].value_counts().to_dict()
    
    # ===== REPORT 1: OVERALL STATUS & HIERARCHICAL BREAKDOWN =====
    status_data = []
    
    # Overall row
    overall_row = {
        "Category": "Overall",
        "Circle": "",
        "Division": "",
        "Subdivision": "",
        "Communicating": comm_counts.get("Communicating", 0),
        "Never Comm": comm_counts.get("Never Comm", 0),
        "Non Comm": comm_counts.get("Non Comm", 0),
        "Total": total_records,
        "Communicating %": round(100 * comm_counts.get("Communicating", 0) / total_records, 2) if total_records > 0 else 0
    }
    status_data.append(overall_row)
    
    # Hierarchical breakdown
    print(f"🏢 Creating hierarchical breakdown...")
    
    # By Circle
    if 'Circle' in df_final.columns:
        for circle in sorted(df_final['Circle'].dropna().unique()):
            circle_data = df_final[df_final['Circle'] == circle]
            circle_comm_counts = circle_data['Comm Status'].value_counts().to_dict()
            status_data.append({
                "Category": "By Circle",
                "Circle": str(circle),
                "Division": "",
                "Subdivision": "",
                "Communicating": int(circle_comm_counts.get("Communicating", 0)),
                "Never Comm": int(circle_comm_counts.get("Never Comm", 0)),
                "Non Comm": int(circle_comm_counts.get("Non Comm", 0)),
                "Total": int(len(circle_data)),
                "Communicating %": round(100 * circle_comm_counts.get("Communicating", 0) / len(circle_data), 2) if len(circle_data) > 0 else 0
            })
    
    # By Division
    if 'Division' in df_final.columns:
        for division in sorted(df_final['Division'].dropna().unique()):
            division_data = df_final[df_final['Division'] == division]
            division_comm_counts = division_data['Comm Status'].value_counts().to_dict()
            circle_val = division_data['Circle'].mode()[0] if 'Circle' in division_data.columns and len(division_data['Circle'].mode()) > 0 else ""
            
            status_data.append({
                "Category": "By Division",
                "Circle": str(circle_val),
                "Division": str(division),
                "Subdivision": "",
                "Communicating": int(division_comm_counts.get("Communicating", 0)),
                "Never Comm": int(division_comm_counts.get("Never Comm", 0)),
                "Non Comm": int(division_comm_counts.get("Non Comm", 0)),
                "Total": int(len(division_data)),
                "Communicating %": round(100 * division_comm_counts.get("Communicating", 0) / len(division_data), 2) if len(division_data) > 0 else 0
            })
    
    # By Subdivision
    if 'Subdivision' in df_final.columns:
        for subdivision in sorted(df_final['Subdivision'].dropna().unique()):
            subdivision_data = df_final[df_final['Subdivision'] == subdivision]
            subdivision_comm_counts = subdivision_data['Comm Status'].value_counts().to_dict()
            circle_val = subdivision_data['Circle'].mode()[0] if 'Circle' in subdivision_data.columns and len(subdivision_data['Circle'].mode()) > 0 else ""
            division_val = subdivision_data['Division'].mode()[0] if 'Division' in subdivision_data.columns and len(subdivision_data['Division'].mode()) > 0 else ""
            
            status_data.append({
                "Category": "By Subdivision",
                "Circle": str(circle_val),
                "Division": str(division_val),
                "Subdivision": str(subdivision),
                "Communicating": int(subdivision_comm_counts.get("Communicating", 0)),
                "Never Comm": int(subdivision_comm_counts.get("Never Comm", 0)),
                "Non Comm": int(subdivision_comm_counts.get("Non Comm", 0)),
                "Total": int(len(subdivision_data)),
                "Communicating %": round(100 * subdivision_comm_counts.get("Communicating", 0) / len(subdivision_data), 2) if len(subdivision_data) > 0 else 0
            })
    
    df_status = pd.DataFrame(status_data)
    status_path = output_dir / f"Comm_Status_Summary_{dg_name}_{date}.csv"
    df_status.to_csv(status_path, index=False)
    print(f"✨ Status summary: {status_path.name}")
    
    # ===== REPORT 2: AGEING ANALYSIS =====
    print(f"📊 Analyzing ageing for Non Comm and Never Comm meters...")
    ageing_data = []
    
    # Age buckets
    age_buckets = {
        '1-7 days': (1, 7),
        '8-15 days': (8, 15),
        '16-30 days': (16, 30),
        '31-60 days': (31, 60),
        '61-90 days': (61, 90),
        '>90 days': (91, 999999)
    }
    
    if 'Communicated At' in df_final.columns:
        non_comm_df = df_final[df_final['Comm Status'] == 'Non Comm'].copy()
        never_comm_df = df_final[df_final['Comm Status'] == 'Never Comm'].copy()
        
        # Calculate ageing for Non Comm (days since last communication)
        if len(non_comm_df) > 0:
            def calculate_days_since_comm(comm_at):
                try:
                    dt = pd.to_datetime(comm_at, dayfirst=True, errors='coerce')
                    if pd.notna(dt):
                        today = pd.to_datetime(date)
                        return (today - dt).days
                except:
                    pass
                return None
            
            non_comm_df['Days_Since_Comm'] = non_comm_df['Communicated At'].apply(calculate_days_since_comm)
            
            for bucket_name, (min_days, max_days) in age_buckets.items():
                count = len(non_comm_df[(non_comm_df['Days_Since_Comm'] >= min_days) & 
                                        (non_comm_df['Days_Since_Comm'] <= max_days)])
                ageing_data.append({
                    "Category": "Non Comm",
                    "Age Bucket": bucket_name,
                    "Count": count,
                    "Percentage": round(100 * count / len(non_comm_df), 2) if len(non_comm_df) > 0 else 0
                })
        
        # Calculate ageing for Never Comm (days since installation)
        if len(never_comm_df) > 0 and 'Installation date' in never_comm_df.columns:
            def calculate_days_since_installation(inst_date):
                try:
                    dt = pd.to_datetime(inst_date, dayfirst=True, errors='coerce')
                    if pd.notna(dt):
                        today = pd.to_datetime(date)
                        return (today - dt).days
                except:
                    pass
                return None
            
            never_comm_df['Days_Since_Installation'] = never_comm_df['Installation date'].apply(calculate_days_since_installation)
            
            for bucket_name, (min_days, max_days) in age_buckets.items():
                count = len(never_comm_df[(never_comm_df['Days_Since_Installation'] >= min_days) & 
                                          (never_comm_df['Days_Since_Installation'] <= max_days)])
                ageing_data.append({
                    "Category": "Never Comm",
                    "Age Bucket": bucket_name,
                    "Count": count,
                    "Percentage": round(100 * count / len(never_comm_df), 2) if len(never_comm_df) > 0 else 0
                })
    
    if ageing_data:
        df_ageing = pd.DataFrame(ageing_data)
        ageing_path = output_dir / f"Comm_Ageing_Analysis_{dg_name}_{date}.csv"
        df_ageing.to_csv(ageing_path, index=False)
        print(f"✨ Ageing analysis: {ageing_path.name}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 SIMPLIFIED COMM STATUS SUMMARY FOR {dg_name}")
    print(f"{'='*60}")
    
    print(f"\n=== OVERALL COMM STATUS ===")
    print(f"   Communicating: {overall_row['Communicating']} ({overall_row['Communicating %']}%)")
    print(f"   Never Comm: {overall_row['Never Comm']}")
    print(f"   Non Comm: {overall_row['Non Comm']}")
    print(f"   Total Records: {overall_row['Total']}")
    
    # Print hierarchical summary
    circles = len([item for item in status_data if item['Category'] == 'By Circle'])
    divisions = len([item for item in status_data if item['Category'] == 'By Division'])
    subdivisions = len([item for item in status_data if item['Category'] == 'By Subdivision'])
    
    print(f"\n=== HIERARCHICAL BREAKDOWN ===")
    print(f"   Circles: {circles}")
    print(f"   Divisions: {divisions}")
    print(f"   Subdivisions: {subdivisions}")
    
    # Print ageing summary
    if ageing_data:
        print(f"\n=== AGEING ANALYSIS ===")
        
        non_comm_ageing = [item for item in ageing_data if item['Category'] == 'Non Comm']
        never_comm_ageing = [item for item in ageing_data if item['Category'] == 'Never Comm']
        
        if non_comm_ageing:
            print(f"\n   Non Comm Meters (days since last communication):")
            for item in non_comm_ageing:
                if item['Count'] > 0:
                    print(f"      {item['Age Bucket']}: {item['Count']} meters ({item['Percentage']}%)")
        
        if never_comm_ageing:
            print(f"\n   Never Comm Meters (days since installation):")
            for item in never_comm_ageing:
                if item['Count'] > 0:
                    print(f"      {item['Age Bucket']}: {item['Count']} meters ({item['Percentage']}%)")
    
    return {
        'overall': overall_row,
        'status_count': len(status_data),
        'ageing_count': len(ageing_data) if ageing_data else 0
    }


if __name__ == "__main__":
    base_path = Path("/Users/rishubatra/Library/CloudStorage/OneDrive-SharedLibraries-SinhalUdyogpvtltd/Communication site - Daily_SLA_Reporting")
    date = "2026-02-06"
    
    print(f"🚀 Generating Simplified Comm Status Reports for {date}")
    print(f"{'='*70}\n")
    
    report_folder = base_path / date / "Report_1_Comms_Reporting"
    
    # Process each DG
    for dg_folder in report_folder.iterdir():
        if dg_folder.is_dir() and dg_folder.name.startswith("DG"):
            dg_name = dg_folder.name
            output_dir = dg_folder / "output"
            final_report = output_dir / f"Final_SLA_Report_{date}.csv"
            
            if not final_report.exists():
                print(f"⚠️  Skipping {dg_name} - Final_SLA_Report not found")
                continue
            
            print(f"\n{'='*70}")
            print(f"Processing {dg_name}")
            print(f"{'='*70}")
            
            result = generate_comm_summaries(final_report, output_dir, dg_name, date)
    
    print(f"\n{'='*70}")
    print(f"✅ All simplified reports generated successfully!")
    print(f"{'='*70}")

