# Communication Status Summary Reports Guide

## Overview
The enhanced comm status reporting system now generates comprehensive analytics across multiple dimensions to provide deep insights into meter communication performance.

## Generated Reports

When you run `daily_reporter.py`, the following communication status reports are automatically generated for each DG:

### 1. **Overall Summary Report**
**File:** `Comm_Summary_Overall_{DG_NAME}_{DATE}.csv`

Contains high-level metrics:
- Total meters: Communicating, Never Comm, Non Comm
- Communication percentage
- Single-row summary for quick reference

**Example:**
```
Category,Grouping,Communicating,Never Comm,Non Comm,Total,Communicating %
Overall,All,25000,3000,2000,30000,83.33
```

---

### 2. **Ageing Analysis Report**
**File:** `Comm_Summary_Ageing_{DG_NAME}_{DATE}.csv`

Breaks down problematic meters by age:

#### Non Comm Meters (Days since last communication):
- 1-7 days
- 8-15 days
- 16-30 days
- 31-60 days
- 61-90 days
- >90 days

#### Never Comm Meters (Days since installation):
- 1-7 days
- 8-15 days
- 16-30 days
- 31-60 days
- 61-90 days
- >90 days

**Use Case:** Identify meters requiring immediate attention based on how long they've been non-communicating.

**Example:**
```
Category,Grouping,Count,Percentage
Ageing - Non Comm,1-7 days,150,7.5
Ageing - Non Comm,8-15 days,280,14.0
Ageing - Non Comm,16-30 days,520,26.0
Ageing - Never Comm,1-7 days,45,1.5
Ageing - Never Comm,8-15 days,180,6.0
```

---

### 3. **Date Trends Report**
**File:** `Comm_Summary_DateTrends_{DG_NAME}_{DATE}.csv`

Shows daily communication patterns:
- Number of meters communicating each day
- Trend analysis to identify communication patterns
- Percentage of total meters

**Use Case:** Track communication health over time, identify dates with communication issues.

**Example:**
```
Category,Grouping,Count,Percentage
Daily Trend - Communicating,2026-02-12,25000,83.33
Daily Trend - Communicating,2026-02-11,24800,82.67
Daily Trend - Communicating,2026-02-10,24500,81.67
```

---

### 4. **Hierarchical Breakdown Report**
**File:** `Comm_Summary_Hierarchical_{DG_NAME}_{DATE}.csv`

Three-level geographical breakdown:

#### By Circle
- Overall communication status per circle
- Communication percentage for each circle

#### By Division
- Communication status per division
- Linked to parent circle

#### By Subdivision
- Most granular level
- Communication status per subdivision
- Linked to parent division and circle

**Use Case:** Identify geographical areas with communication problems, drill down from circle to subdivision level.

**Example:**
```
Category,Circle,Division,Subdivision,Communicating,Never Comm,Non Comm,Total,Communicating %
By Circle,BHARUCH-35,,,20500,2000,1500,24000,85.42
By Division,BHARUCH-35,ANKLESHWAR IND-23,,10200,1000,800,12000,85.00
By Subdivision,BHARUCH-35,ANKLESHWAR IND-23,ANKLESHWAR EAST-437,5100,500,400,6000,85.00
```

---

### 5. **Master Combined Report**
**File:** `Comm_Summary_Master_{DG_NAME}_{DATE}.csv`

All-in-one comprehensive report combining:
- Overall summary
- Ageing analysis
- Date trends
- Hierarchical breakdown

**Use Case:** Single file for complete analysis, easy to share with stakeholders.

---

## Terminal Output

When processing completes, you'll see a comprehensive summary in the terminal:

```
============================================================
📊 COMPREHENSIVE COMM STATUS SUMMARY FOR DG1
============================================================

=== 1. OVERALL COMM STATUS ===
   Communicating: 25000 (83.33%)
   Never Comm: 3000
   Non Comm: 2000
   Total Records: 30000

=== 2. AGEING ANALYSIS ===

   Non Comm Meters (by days since last communication):
      1-7 days: 150 meters (7.5%)
      8-15 days: 280 meters (14.0%)
      16-30 days: 520 meters (26.0%)
      31-60 days: 650 meters (32.5%)
      61-90 days: 280 meters (14.0%)
      >90 days: 120 meters (6.0%)

   Never Comm Meters (by days since installation):
      1-7 days: 45 meters (1.5%)
      8-15 days: 180 meters (6.0%)
      16-30 days: 890 meters (29.7%)
      31-60 days: 1200 meters (40.0%)
      61-90 days: 485 meters (16.2%)
      >90 days: 200 meters (6.7%)

=== 3. COMMUNICATION TRENDS BY DATE ===
   (Showing daily communication counts)
      2026-02-12: 25000 meters
      2026-02-11: 24800 meters
      2026-02-10: 24500 meters
      ... and 7 more dates (see CSV for full details)

=== 4. HIERARCHICAL BREAKDOWN ===

   By Circle (3 circles):
      BHARUCH-35: 20500/24000 (85.42%)
      VADODARA-36: 3200/4000 (80.00%)
      SURAT-37: 1300/2000 (65.00%)

   By Division (8 divisions):
      ANKLESHWAR IND-23: 10200/12000 (85.00%)
      JAMBUSAR-24: 6500/7500 (86.67%)
      ... and 3 more divisions

   By Subdivision (25 subdivisions):
      ANKLESHWAR EAST-437: 5100/6000 (85.00%)
      ANKLESHWAR WEST-438: 3800/4500 (84.44%)
      ... and 20 more subdivisions
```

---

## Key Metrics Explained

### Communication Status Categories

1. **Communicating**: Meters that communicated today (matching processing date)
2. **Non Comm**: Meters that communicated before but not today
3. **Never Comm**: Meters that have never communicated since installation

### Ageing Buckets

Age ranges help prioritize maintenance:
- **1-7 days**: Recent issues, quick investigation needed
- **8-15 days**: Early intervention window
- **16-30 days**: Requires attention
- **31-60 days**: Problem meters needing field visit
- **61-90 days**: Long-term issues
- **>90 days**: Critical - may need hardware replacement

---

## Usage Tips

1. **Start with Overall**: Check the overall communication percentage
2. **Identify Problem Areas**: Use hierarchical breakdown to find circles/divisions/subdivisions with low communication rates
3. **Prioritize by Age**: Use ageing analysis to prioritize field visits (start with recent non-comm)
4. **Track Progress**: Compare date trends across multiple days to see if communication is improving
5. **Export for Analysis**: All reports are CSV format - easy to import into Excel, Power BI, or other tools

---

## File Locations

All reports are saved in:
```
{DATE}/Report_{N}_Comms_Reporting/{DG_NAME}/output/
```

Example:
```
2026-02-12/Report_1_Comms_Reporting/DG1/output/
├── Comm_Summary_Overall_DG1_2026-02-12.csv
├── Comm_Summary_Ageing_DG1_2026-02-12.csv
├── Comm_Summary_DateTrends_DG1_2026-02-12.csv
├── Comm_Summary_Hierarchical_DG1_2026-02-12.csv
└── Comm_Summary_Master_DG1_2026-02-12.csv
```

---

## Integration

These reports can be:
- Imported into Power BI dashboards
- Sent via email automation
- Posted to Microsoft Teams
- Used in scheduled reports
- Analyzed in Excel pivot tables

---

## Questions?

For issues or enhancement requests, check the main README.md or contact the development team.
