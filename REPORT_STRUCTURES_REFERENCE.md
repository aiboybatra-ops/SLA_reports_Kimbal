# Communication Status Reports - Data Structure Reference

## Report 1: Overall Summary
**File:** `Comm_Summary_Overall_{DG_NAME}_{DATE}.csv`

### Columns:
- `Category` - Always "Overall"
- `Grouping` - Always "All"
- `Communicating` - Count of communicating meters
- `Never Comm` - Count of never communicated meters
- `Non Comm` - Count of non-communicating meters
- `Total` - Total meter count
- `Communicating %` - Percentage of communicating meters

### Sample Data:
```csv
Category,Grouping,Communicating,Never Comm,Non Comm,Total,Communicating %
Overall,All,25456,2890,1654,30000,84.85
```

---

## Report 2: Ageing Analysis
**File:** `Comm_Summary_Ageing_{DG_NAME}_{DATE}.csv`

### Columns:
- `Category` - "Ageing - Non Comm" or "Ageing - Never Comm"
- `Grouping` - Age bucket (1-7 days, 8-15 days, etc.)
- `Count` - Number of meters in this bucket
- `Percentage` - Percentage within the category

### Sample Data:
```csv
Category,Grouping,Count,Percentage
Ageing - Non Comm,1-7 days,124,7.5
Ageing - Non Comm,8-15 days,231,13.96
Ageing - Non Comm,16-30 days,430,25.99
Ageing - Non Comm,31-60 days,539,32.59
Ageing - Non Comm,61-90 days,231,13.96
Ageing - Non Comm,>90 days,99,5.99
Ageing - Never Comm,1-7 days,43,1.49
Ageing - Never Comm,8-15 days,173,5.99
Ageing - Never Comm,16-30 days,867,30.00
Ageing - Never Comm,31-60 days,1156,40.00
Ageing - Never Comm,61-90 days,462,15.99
Ageing - Never Comm,>90 days,189,6.54
```

### Interpretation:
- **Non Comm Ageing:** Days since last successful communication
  - Priority: 1-7 days (recent failures, likely easy fixes)
  - Concern: >30 days (may need hardware intervention)

- **Never Comm Ageing:** Days since installation
  - Priority: >30 days (should have communicated by now)
  - Critical: >90 days (likely installation or hardware issue)

---

## Report 3: Date Trends
**File:** `Comm_Summary_DateTrends_{DG_NAME}_{DATE}.csv`

### Columns:
- `Category` - Always "Daily Trend - Communicating"
- `Grouping` - Date (YYYY-MM-DD format)
- `Count` - Number of meters that communicated on this date
- `Percentage` - Percentage of total meters

### Sample Data:
```csv
Category,Grouping,Count,Percentage
Daily Trend - Communicating,2026-02-12,25456,84.85
Daily Trend - Communicating,2026-02-11,25234,84.11
Daily Trend - Communicating,2026-02-10,24987,83.29
Daily Trend - Communicating,2026-02-09,25123,83.74
Daily Trend - Communicating,2026-02-08,24856,82.85
Daily Trend - Communicating,2026-02-07,25345,84.48
Daily Trend - Communicating,2026-02-06,25012,83.37
```

### Use Cases:
- **Trend Analysis:** Is communication improving or declining?
- **Problem Detection:** Sudden drops indicate network/infrastructure issues
- **Weekend Patterns:** Compare weekday vs weekend communication
- **Validation:** Today's count should match Overall report

---

## Report 4: Hierarchical Breakdown
**File:** `Comm_Summary_Hierarchical_{DG_NAME}_{DATE}.csv`

### Columns:
- `Category` - "By Circle", "By Division", or "By Subdivision"
- `Circle` - Circle name
- `Division` - Division name (blank for Circle-level rows)
- `Subdivision` - Subdivision name (blank for Circle/Division rows)
- `Communicating` - Count of communicating meters
- `Never Comm` - Count of never communicated meters
- `Non Comm` - Count of non-communicating meters
- `Total` - Total meter count
- `Communicating %` - Percentage of communicating meters

### Sample Data:
```csv
Category,Circle,Division,Subdivision,Communicating,Never Comm,Non Comm,Total,Communicating %
By Circle,BHARUCH-35,,,17254,1934,1312,20500,84.17
By Circle,VADODARA-36,,,5123,612,265,6000,85.38
By Circle,SURAT-37,,,3079,344,77,3500,87.97
By Division,BHARUCH-35,ANKLESHWAR IND-23,,8627,967,656,10250,84.17
By Division,BHARUCH-35,JAMBUSAR-24,,5314,595,403,6312,84.19
By Division,BHARUCH-35,HANSOT-25,,3313,372,253,3938,84.13
By Division,VADODARA-36,DABHOI-26,,2561,306,133,3000,85.37
By Division,VADODARA-36,KARJAN-27,,2562,306,132,3000,85.40
By Subdivision,BHARUCH-35,ANKLESHWAR IND-23,ANKLESHWAR EAST-437,4313,484,328,5125,84.16
By Subdivision,BHARUCH-35,ANKLESHWAR IND-23,ANKLESHWAR WEST-438,4314,483,328,5125,84.18
By Subdivision,BHARUCH-35,JAMBUSAR-24,JAMBUSAR RURAL-439,2657,298,201,3156,84.19
By Subdivision,BHARUCH-35,JAMBUSAR-24,JAMBUSAR URBAN-440,2657,297,202,3156,84.19
```

### Hierarchy Structure:
```
BHARUCH-35 (Circle)
├── ANKLESHWAR IND-23 (Division)
│   ├── ANKLESHWAR EAST-437 (Subdivision)
│   └── ANKLESHWAR WEST-438 (Subdivision)
├── JAMBUSAR-24 (Division)
│   ├── JAMBUSAR RURAL-439 (Subdivision)
│   └── JAMBUSAR URBAN-440 (Subdivision)
└── HANSOT-25 (Division)
    └── ...
```

### Analysis Tips:
1. **Find Problem Circles:** Sort by "Communicating %" ascending
2. **Drill Down:** Check divisions within problem circles
3. **Pinpoint Issues:** Identify specific subdivisions needing attention
4. **Compare Performance:** Which circles/divisions perform best?
5. **Resource Allocation:** Focus teams on low-performing areas

---

## Report 5: Master Combined Report
**File:** `Comm_Summary_Master_{DG_NAME}_{DATE}.csv`

### Structure:
Combines all the above reports into one file with varying column structures:

#### Section 1: Overall (1 row)
```csv
Category,Grouping,Communicating,Never Comm,Non Comm,Total,Communicating %
Overall,All,25456,2890,1654,30000,84.85
```

#### Section 2: Ageing (12 rows - 6 Non Comm + 6 Never Comm)
```csv
Category,Grouping,Communicating,Never Comm,Non Comm,Total,Communicating %
Ageing - Non Comm,1-7 days,124,0,0,124,0
Ageing - Non Comm,8-15 days,231,0,0,231,0
...
```

#### Section 3: Date Trends (N rows - one per date)
```csv
Category,Grouping,Communicating,Never Comm,Non Comm,Total,Communicating %
Daily Trend - Communicating,2026-02-12,25456,0,0,25456,84.85
...
```

#### Section 4: Hierarchical (N rows - all circles, divisions, subdivisions)
```csv
Category,Circle,Division,Subdivision,Communicating,Never Comm,Non Comm,Total,Communicating %
By Circle,BHARUCH-35,,,17254,1934,1312,20500,84.17
By Division,BHARUCH-35,ANKLESHWAR IND-23,,8627,967,656,10250,84.17
By Subdivision,BHARUCH-35,ANKLESHWAR IND-23,ANKLESHWAR EAST-437,4313,484,328,5125,84.16
...
```

### Note on Column Variations:
- Ageing and Trends sections use simplified columns (Count mapped to Communicating)
- Hierarchical section adds Circle/Division/Subdivision columns
- Use `Category` column to filter sections when analyzing

---

## Data Field Definitions

### Comm Status Categories:
- **Communicating:** Meter communicated today (Communicated At date = processing date)
- **Non Comm:** Meter communicated before but not today
- **Never Comm:** Meter has never communicated (blank/invalid Communicated At)

### Date Formats:
- Input (Communicated At, Installation date): `DD-MM-YYYY HH:MM:SS`
- Output (Date Trends): `YYYY-MM-DD`

### Percentage Calculations:
- Always rounded to 2 decimal places
- Calculated as: (Count / Total) * 100
- For ageing: Percentage within category (Non Comm or Never Comm)
- For hierarchical: Percentage of meters in that geography

---

## Excel/Power BI Import Tips

### For Overall Summary:
- Simple table, use for KPI cards
- Create gauge chart for Communicating %

### For Ageing Analysis:
- Filter by Category to separate Non Comm vs Never Comm
- Create stacked bar chart showing age distribution
- Conditional formatting for >60 days (red)

### For Date Trends:
- Sort by Grouping (date) ascending
- Create line chart to show trend over time
- Add moving average for smoother trends

### For Hierarchical:
- Use Category filter to separate Circle/Division/Subdivision views
- Create drill-down hierarchy in Power BI
- Use treemap to show size (Total) and color (Communicating %)

### For Master Report:
- Create separate sheets/tables for each Category
- Use Power Query to split into multiple tables
- Create relationships between hierarchical levels

---

## File Size Expectations

Approximate row counts (varies by data):
- Overall: 1 row
- Ageing: 12 rows (6 + 6)
- Date Trends: 10-30 rows (depending on data span)
- Hierarchical: 50-200 rows (3 circles, 8 divisions, 25 subdivisions = ~36 rows minimum)
- Master: Sum of all above (~60-250 rows)

File sizes typically < 50KB per report.

---

## Troubleshooting

### Empty Ageing Report:
- Check if 'Communicated At' column exists in data
- Verify date formats are parseable
- For Never Comm ageing, 'Installation date' must exist

### Empty Date Trends:
- Verify meters have 'Communicated At' data
- Check date parsing is working
- Ensure Comm Status = 'Communicating' exists

### Missing Hierarchical Data:
- Verify Circle, Division, Subdivision columns exist in input
- Check for null/blank values in these columns
- Data must have valid geographical information

### Percentage Shows 0:
- Check if Total > 0
- Verify calculation isn't dividing by zero
- Look for data quality issues in input files
