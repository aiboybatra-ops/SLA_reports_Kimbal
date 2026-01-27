#!/usr/bin/env python3
"""
Daily SLA Reporting Automation System
Processes raw data and generates final reports
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
import platform

class LocalWebhookReceiver(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            print(f"📥 Received webhook: {data}")
            
            # Handle different types of commands
            if 'text' in data:
                message = data['text']
                if 'process' in message.lower() or 'run' in message.lower():
                    print("🎯 Processing command received!")
                    # Here we would trigger the actual processing
                    
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received"}).encode())
            
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<html><body><h1>Webhook Receiver Active</h1></body></html>")

class DesktopNotifier:
    def __init__(self):
        """Initialize desktop notifier"""
        self.system = platform.system()
    
    def send_notification(self, title, message):
        """Send desktop notification based on OS"""
        try:
            if self.system == "Darwin":  # macOS
                subprocess.run([
                    'osascript', '-e', 
                    f'display notification "{message}" with title "{title}"'
                ])
            elif self.system == "Windows":
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    timeout=10
                )
            elif self.system == "Linux":
                subprocess.run(['notify-send', title, message])
            
            print(f"🖥️ Desktop notification: {title} - {message}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send desktop notification: {e}")
            return False

class EmailNotifier:
    def __init__(self, smtp_server, smtp_port, username, password, from_email):
        """Initialize email notifier"""
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        
        # Common SMS gateways for major carriers
        self.sms_gateways = {
            'verizon': '@vtext.com',
            'att': '@txt.att.net',
            'tmobile': '@tmomail.net',
            'sprint': '@messaging.sprintpcs.com',
            'cricket': '@sms.mycricket.com'
        }
    
    def send_email(self, to_emails, subject, body, is_html=False):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email sent to {to_emails}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_sms(self, phone_number, carrier, message):
        """Send SMS via email-to-SMS gateway"""
        if carrier.lower() not in self.sms_gateways:
            print(f"❌ Unsupported carrier: {carrier}")
            return False
            
        sms_email = phone_number + self.sms_gateways[carrier.lower()]
        return self.send_email([sms_email], "SLA Alert", message[:160])  # SMS limit

class TeamsNotifier:
    def __init__(self, webhook_url):
        """Initialize Teams notifier with webhook URL"""
        self.webhook_url = webhook_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def send_message(self, message, title=None):
        """Send simple text message to Teams with retry logic"""
        payload = {
            "text": message
        }
        if title:
            payload["title"] = title
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    self.webhook_url, 
                    json=payload, 
                    timeout=10
                )
                if response.status_code == 200:
                    print(f"✅ Teams message sent successfully")
                    return True
                else:
                    print(f"⚠️ Teams API returned status {response.status_code}")
            except requests.exceptions.Timeout:
                print(f"⏰ Teams message timeout (attempt {attempt + 1}/{max_retries})")
            except requests.exceptions.ConnectionError as e:
                print(f"🔌 Teams connection error (attempt {attempt + 1}/{max_retries}): {str(e)[:50]}...")
            except Exception as e:
                print(f"❌ Teams message failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                import time
                time.sleep(2 ** attempt)  # Exponential backoff
        
        print(f"❌ Teams message failed after {max_retries} attempts")
        return False
    
    def send_adaptive_card(self, card_content):
        """Send adaptive card to Teams"""
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": card_content
                }
            ]
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send adaptive card: {e}")
            return False

class WebhookManager:
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.thread = None
    
    def start_server(self):
        """Start local webhook server in background thread"""
        try:
            self.server = HTTPServer(('localhost', self.port), LocalWebhookReceiver)
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            print(f"🌐 Webhook server started on port {self.port}")
            return True
        except Exception as e:
            print(f"❌ Failed to start webhook server: {e}")
            return False
    
    def stop_server(self):
        """Stop the webhook server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("🛑 Webhook server stopped")

class DailyReporter:
    def __init__(self, base_path=None):
        """Initialize the reporter with base path"""
        if base_path is None:
            base_path = Path(__file__).parent
        
        self.base_path = Path(base_path)
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.report_date_folder = self.base_path / self.today_date
        
        # No external notification systems (Teams/Power Automate) are used now.
        # Script runs locally and writes outputs + summary files only.
        
        # Use SharePoint path as base if not specified
        if base_path is None:
            base_path = Path('/Users/rishubatra/Library/CloudStorage/OneDrive-SharedLibraries-SinhalUdyogpvtltd/Communication site - Daily_SLA_Reporting')
        
    def get_report_structure(self, report_name):
        """Get paths for a specific report"""
        report_folder = self.report_date_folder / report_name
        raw_data_folder = report_folder / "raw_data"
        output_folder = report_folder / "output"
        
        return {
            "report_folder": report_folder,
            "raw_data": raw_data_folder,
            "output": output_folder,
        }
    
    def get_dg_report_structures(self, report_name="Report_1_Comms_Reporting", dg_pattern="DG*"):
        """Get paths for all DG subfolders within a report"""
        report_folder = self.report_date_folder / report_name
        # First try DG* pattern, then try any folder with raw_data subfolder
        dg_folders = list(report_folder.glob(dg_pattern))
        
        # If no DG* folders found, look for any folder containing raw_data
        if not dg_folders:
            potential_folders = [f for f in report_folder.iterdir() if f.is_dir()]
            dg_folders = [f for f in potential_folders if (f / "raw_data").exists()]
        
        structures = {}
        for dg_folder in dg_folders:
            raw_data_folder = dg_folder / "raw_data"
            output_folder = dg_folder / "output"
            
            structures[dg_folder.name] = {
                "report_folder": dg_folder,
                "raw_data": raw_data_folder,
                "output": output_folder,
            }
        
        return structures
    
    def create_structure(self, report_name):
        """Create the directory structure for a specific report if it doesn't exist"""
        paths = self.get_report_structure(report_name)
        paths["raw_data"].mkdir(parents=True, exist_ok=True)
        paths["output"].mkdir(parents=True, exist_ok=True)
        print(f"✓ Structure created for {report_name}")
        return paths
    
    def create_dg_structure(self, report_name, dg_name):
        """Create the directory structure for a specific DG subfolder if it doesn't exist"""
        report_folder = self.report_date_folder / report_name
        dg_folder = report_folder / dg_name
        raw_data_folder = dg_folder / "raw_data"
        output_folder = dg_folder / "output"
        
        raw_data_folder.mkdir(parents=True, exist_ok=True)
        output_folder.mkdir(parents=True, exist_ok=True)
        
        paths = {
            "report_folder": dg_folder,
            "raw_data": raw_data_folder,
            "output": output_folder,
        }
        
        print(f"✓ Structure created for {report_name}/{dg_name}")
        return paths
    
    def notify_folder_creation(self):
        """Log that daily folder structure has been created (no external notifications)"""
        message = f"📁 Folder created for {self.today_date}\n\nReady for data upload:\n{self.report_date_folder}/Report_1_Comms_Reporting/"
        print(message)
    
    def get_raw_files(self, report_name, file_extension=None):
        """Get all raw files for a report"""
        paths = self.get_report_structure(report_name)
        raw_data_folder = paths["raw_data"]
        
        if not raw_data_folder.exists():
            print(f"Raw data folder not found: {raw_data_folder}")
            return []
        
        if file_extension:
            files = list(raw_data_folder.glob(f"*{file_extension}"))
        else:
            files = list(raw_data_folder.glob("*"))
        
        return sorted(files)
    
    def create_default_dg_structure(self, report_name):
        """Create default DG subfolders (DG1, DG2, DG3) if they don't exist"""
        report_folder = self.report_date_folder / report_name
        default_dgs = ["DG1", "DG2", "DG3"]
        
        print(f"\n📁 Creating default DG folder structure...")
        for dg_name in default_dgs:
            dg_folder = report_folder / dg_name
            raw_data_folder = dg_folder / "raw_data"
            output_folder = dg_folder / "output"
            
            raw_data_folder.mkdir(parents=True, exist_ok=True)
            output_folder.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ Created {dg_name} structure")
        
        print(f"✅ Default DG folders created: {', '.join(default_dgs)}")
        return default_dgs
    
    def process_comms_reporting(self):
        """Process Communications Reporting for all DG subfolders"""
        report_name = "Report_1_Comms_Reporting"
        print(f"\n{'='*60}")
        print(f"Processing {report_name} for {self.today_date}")
        print(f"{'='*60}\n")
        
        # Create date folder if it doesn't exist
        self.report_date_folder.mkdir(parents=True, exist_ok=True)
        print(f"✓ Date folder ensured: {self.report_date_folder}")
            
        # Create main folder structure and notify
        main_paths = self.create_structure(report_name)
        self.notify_folder_creation()
                
        # Get all DG subfolder structures
        dg_structures = self.get_dg_report_structures(report_name)
                
        # If no DG subfolders exist, create default ones (DG1, DG2, DG3)
        if not dg_structures:
            print(f"\n⚠️ No existing DG subfolders found in {report_name}")
            print(f"   Creating default DG structure...")
            default_dgs = self.create_default_dg_structure(report_name)
            # Re-fetch structures after creation
            dg_structures = self.get_dg_report_structures(report_name)
            
        if not dg_structures:
            print(f"❌ Failed to create DG subfolders")
            return False
                
        print(f"📁 Found {len(dg_structures)} DG subfolder(s): {list(dg_structures.keys())}")
            
        # Process each DG subfolder
        for dg_name, paths in dg_structures.items():
            print(f"\n--- Processing {dg_name} ---")
            raw_dir = paths["raw_data"]
                        
            # Validate filenames before processing
            if not self.validate_filenames(raw_dir):
                continue  # Skip this DG if files are invalid
                        
            # Validate columns before processing
            if not self.validate_columns(raw_dir):
                continue  # Skip this DG if columns are invalid
                        
            # Ensure structure exists
            paths = self.create_dg_structure(report_name, dg_name)
            raw_dir = paths["raw_data"]
                        
            # Skip if raw_data folder is empty
            if not raw_dir.exists() or not any(raw_dir.iterdir()):
                print(f"⚠️ Raw data folder for {dg_name} is empty or doesn't exist, skipping...")
                continue
            
            # Stats tracking
            stats = {}
                
            # 1. Load Warehouse base
            warehouse_path = raw_dir / "Warehouse.csv"
            if not warehouse_path.exists():
                print(f"❌ Base file {warehouse_path.name} not found in {dg_name}")
                continue
                
            print(f"📦 Loading Warehouse base...")
            df_master = pd.read_csv(warehouse_path)
            df_master['Meter Serial No'] = df_master['Meter Serial No'].astype(str).str.strip()
            stats['Warehouse'] = {'total': len(df_master)}
                
            # 2. Merge New_Service_connection
            nsc_path = raw_dir / "New_Service_connection.csv"
            if nsc_path.exists():
                print(f"🔗 Merging {nsc_path.name}...")
                df_nsc = pd.read_csv(nsc_path)
                df_nsc['New Meter QR Code '] = df_nsc['New Meter QR Code '].astype(str).str.strip()
                    
                # Track mapping stats
                matched = df_nsc['New Meter QR Code '].isin(df_master['Meter Serial No']).sum()
                stats['New_Service_connection'] = {
                    'total': len(df_nsc),
                    'mapped': matched,
                    'unmapped': len(df_nsc) - matched
                }
                    
                df_master = pd.merge(df_master, df_nsc, left_on='Meter Serial No', right_on='New Meter QR Code ', how='left', suffixes=('', '_NSC'))
                
            # 3. Merge Merged_CI-MI
            ci_mi_path = raw_dir / "Merged_CI-MI.csv"
            if ci_mi_path.exists():
                print(f"🔗 Merging {ci_mi_path.name}...")
                df_ci_mi = pd.read_csv(ci_mi_path)
                df_ci_mi['New Meter QR Code'] = df_ci_mi['New Meter QR Code'].astype(str).str.strip()
                    
                # Track mapping stats
                matched = df_ci_mi['New Meter QR Code'].isin(df_master['Meter Serial No']).sum()
                stats['Merged_CI-MI'] = {
                    'total': len(df_ci_mi),
                    'mapped': matched,
                    'unmapped': len(df_ci_mi) - matched
                }
                    
                df_master = pd.merge(df_master, df_ci_mi, left_on='Meter Serial No', right_on='New Meter QR Code', how='left', suffixes=('', '_CIMI'))
    
            # 4. Merge Meter_Installation
            mi_path = raw_dir / "Meter_Installation.csv"
            if mi_path.exists():
                print(f"🔗 Merging {mi_path.name}...")
                df_mi = pd.read_csv(mi_path)
                df_mi['New Meter Number Scan'] = df_mi['New Meter Number Scan'].astype(str).str.strip()
                    
                # Track mapping stats
                matched = df_mi['New Meter Number Scan'].isin(df_master['Meter Serial No']).sum()
                stats['Meter_Installation'] = {
                    'total': len(df_mi),
                    'mapped': matched,
                    'unmapped': len(df_mi) - matched
                }
                    
                df_master = pd.merge(df_master, df_mi, left_on='Meter Serial No', right_on='New Meter Number Scan', how='left', suffixes=('', '_MI'))
    
            # 5. Merge Node ID
            node_id_path = raw_dir / "Node ID.xlsx"
            if node_id_path.exists():
                print(f"🔗 Merging {node_id_path.name}...")
                df_node = pd.read_excel(node_id_path)
                df_node['Meter Number'] = df_node['Meter Number'].astype(str).str.strip()
                    
                # Track mapping stats
                matched = df_node['Meter Number'].isin(df_master['Meter Serial No']).sum()
                stats['Node_ID'] = {
                    'total': len(df_node),
                    'mapped': matched,
                    'unmapped': len(df_node) - matched
                }
                    
                df_master = pd.merge(df_master, df_node, left_on='Meter Serial No', right_on='Meter Number', how='left')
                # Ensure only one NodeId exists (the excel has NodeId column)
                if 'NodeId' in df_master.columns:
                    print(f"✅ NodeId merged successfully")
    
            # 6. Merge Routing files
            routing_files = sorted(list(raw_dir.glob("Routings Part-*.xlsx")))
            if not routing_files: # Check for single Routings.xlsx or similar
                routing_files = list(raw_dir.glob("Routings*.xlsx"))
                    
            if routing_files:
                print(f"🔗 Merging {len(routing_files)} routing file(s)...")
                df_routings_list = []
                for rf in routing_files:
                    df_routings_list.append(pd.read_excel(rf))
                    
                df_routings = pd.concat(df_routings_list, ignore_index=True).drop_duplicates()
                df_routings['Node ID'] = df_routings['Node ID'].astype(str).str.strip()
                    
                if 'NodeId' in df_master.columns:
                    # Clean NodeId to remove .0 if it's a float before converting to string
                    def clean_node_id(val):
                        if pd.isna(val): return ""
                        try:
                            return str(int(float(val)))
                        except:
                            return str(val).strip()
    
                    df_master['NodeId_str'] = df_master['NodeId'].apply(clean_node_id)
                        
                    # Track mapping stats
                    matched = df_routings['Node ID'].isin(df_master['NodeId_str']).sum()
                    stats['Routings'] = {
                        'total': len(df_routings),
                        'mapped': matched,
                        'unmapped': len(df_routings) - matched
                    }
                        
                    df_master = pd.merge(df_master, df_routings, left_on='NodeId_str', right_on='Node ID', how='left', suffixes=('', '_ROUTING'))
                    df_master.drop(columns=['NodeId_str'], inplace=True)
                    print(f"✅ Routing data merged successfully")
                else:
                    print(f"⚠️ Skipping routing merge: NodeId not found in master data")
    
            # Summary of missing data in master file
            print(f"\n{'='*60}")
            print(f"MAPPING & MISSING DATA SUMMARY FOR {dg_name}")
            print(f"{'='*60}")
            print(f"Warehouse Base: {stats['Warehouse']['total']} records")
                
            for key, s in stats.items():
                if key == 'Warehouse': continue
                print(f"\nSource: {key}")
                print(f"  - Total records in source: {s['total']}")
                print(f"  - Successfully mapped to master: {s['mapped']}")
                print(f"  - Unmapped (Missing in Warehouse): {s['unmapped']}")
                
            print(f"\nMaster Data Coverage (Missing values in master):")
            if 'NodeId' in df_master.columns:
                missing_node = df_master['NodeId'].isna().sum()
                print(f"  - Meters without Node ID: {missing_node} ({stats['Warehouse']['total'] - missing_node} found)")
                
            if 'Gateway ID' in df_master.columns:
                missing_route = df_master['Gateway ID'].isna().sum()
                print(f"  - Meters without Routing Info: {missing_route} ({stats['Warehouse']['total'] - missing_route} found)")
                
            print(f"{'='*60}\n")
                
            # Save master result
            master_output_path = paths["output"] / f"Master_SLA_Report_{self.today_date}.csv"
            df_master.to_csv(master_output_path, index=False)
            print(f"\n✨ Master report created: {master_output_path.name}")
                
            # 7. Create Intermediate File with specific fields
            print(f"📝 Creating intermediate report...")
                
            # Coalesce fields from multiple sources to fill blanks
            print(f"🔄 Coalescing data from multiple sources...")
                
            def coalesce_cols(df, base_col, sources):
                result = df[base_col].copy() if base_col in df.columns else pd.Series([pd.NA] * len(df))
                for s in sources:
                    if s in df.columns:
                        result = result.fillna(df[s])
                return result
    
            # Map the coalesced columns
            df_master['Final_Feeder'] = coalesce_cols(df_master, 'Feeder Name(From Field)', ['Feeder Name(From Field)_CIMI', 'Feeder Name(From Field)_MI'])
            df_master['Final_ConsName'] = coalesce_cols(df_master, 'Consumer Name', ['Consumer name', 'Consumer Name_MI'])
            df_master['Final_Address'] = coalesce_cols(df_master, 'Address', ['address', 'Address_MI'])
            df_master['Final_Mobile'] = coalesce_cols(df_master, 'Mobile Number', ['Mobile Number_CIMI', 'Mobile Number_MI'])
            df_master['Final_Lat'] = coalesce_cols(df_master, 'Latitude', ['Latitude_CIMI', 'Latitude_MI'])
            df_master['Final_Long'] = coalesce_cols(df_master, 'Longitude', ['Longitude_CIMI', 'Longitude_MI'])
            df_master['Final_Subdivision'] = coalesce_cols(df_master, 'Installed Sub Division', ['Sub Division Name', 'Sub Division Name_CIMI', 'Sub Division Name_MI'])
    
            # Define the mapping (Requested Name: Final Column Name)
            column_mapping = {
                "Meter Serial No": "Meter Serial No",
                "Node ID": "NodeId",
                "Manufacturer": "Manufacturer",
                "Installation Status": "Installation Status",
                "Installation date": "Installation date",
                "Consumer No": "Consumer No",
                "Division": "Division",
                "Subdivision": "Final_Subdivision",
                "Circle": "Circle",
                "Feeder Name": "Final_Feeder",
                "Cons Name": "Final_ConsName",
                "Cons Address": "Final_Address",
                "Mob No.": "Final_Mobile",
                "Latitude": "Final_Lat",
                "Longitude": "Final_Long",
                "Gateway ID": "Gateway ID",
                "Hop Count": "Hop Count",
                "Sink ID": "Sink ID",
                "Communicated At": "Communicated At",
                "Source Endpoint": "Source Endpoint"
            }
                
            # Select and rename columns
            final_cols = []
            rename_dict = {}
            missing_columns = []
                    
            for requested, actual in column_mapping.items():
                if actual in df_master.columns:
                    final_cols.append(actual)
                    rename_dict[actual] = requested
                else:
                    missing_columns.append(requested)
                    print(f"⚠️ Column {requested} ({actual}) not found")
                            
            df_intermediate = df_master[final_cols].rename(columns=rename_dict)
                    
            # Add missing columns with empty values
            for missing_col in missing_columns:
                df_intermediate[missing_col] = ""
                
            intermediate_output_path = paths["output"] / f"Intermediate_SLA_Report_{self.today_date}.csv"
            df_intermediate.to_csv(intermediate_output_path, index=False)
            print(f"✨ Intermediate report created: {intermediate_output_path.name}")
    
            # 8. Create Final Report with Comm Status
            print(f"📡 Calculating Comm Status for Final Report...")
            df_final = df_intermediate.copy()
                
            def calculate_comm_status(comm_at):
                if pd.isna(comm_at) or str(comm_at).strip() == "":
                    return "Never Comm"
                try:
                    # Try parsing the date (Handling DD-MM-YYYY HH:MM:SS)
                    dt = pd.to_datetime(comm_at, dayfirst=True, errors='coerce')
                    if pd.isna(dt):
                        return "Never Comm"
                            
                    if dt.strftime("%Y-%m-%d") == self.today_date:
                        return "Communicating"
                    else:
                        return "Non Comm"
                except:
                    return "Never Comm"
            
            # Handle missing Communicated At column gracefully
            if 'Communicated At' not in df_intermediate.columns:
                df_final['Comm Status'] = "Never Comm"
            else:
    
                df_final['Comm Status'] = df_final['Communicated At'].apply(calculate_comm_status)
                
            # Add blank Remarks column
            df_final['Remarks'] = ""
                
            final_output_path = paths["output"] / f"Final_SLA_Report_{self.today_date}.csv"
            df_final.to_csv(final_output_path, index=False)
            
            print(f"✨ Final report created: {final_output_path.name}")
            print(f"📊 Total records: {len(df_final)}")
            
            # 9. Create JSON summary for Teams / Power Automate
            summary = {
                "date": self.today_date,
                "dg_name": dg_name,
                "total_records": int(len(df_final)),
            }
            
            # Overall Comm Status counts
            comm_counts = df_final["Comm Status"].value_counts().to_dict()
            summary["comm_status_overall"] = {
                "Communicating": int(comm_counts.get("Communicating", 0)),
                "Never Comm": int(comm_counts.get("Never Comm", 0)),
                "Non Comm": int(comm_counts.get("Non Comm", 0)),
            }
            
            # Comm Status by Subdivision (reserved for future extension)
            # Intentionally omitted from JSON summary for now.
            
            # Missing data summary from earlier stats
            missing_node = locals().get("missing_node", None)
            missing_route = locals().get("missing_route", None)
            # Count rows where Communicated At is blank/invalid
            if "Communicated At" in df_final.columns:
                missing_comm_at = df_final["Communicated At"].isna().sum()
            else:
                missing_comm_at = None
            summary["missing_data_summary"] = {
                "meters_without_node_id": int(missing_node) if missing_node is not None else None,
                "meters_without_routing_info": int(missing_route) if missing_route is not None else None,
                "rows_missing_communicated_at": int(missing_comm_at) if missing_comm_at is not None else None,
                "source_mapping": stats,
            }
            
            summary_output_path = paths["output"] / f"SLA_Summary_{dg_name}_{self.today_date}.json"
            with open(summary_output_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"📄 Summary file created: {summary_output_path.name}")
            
            # Print final summary to terminal
            print(f"\n📊 FINAL COMM STATUS SUMMARY FOR {dg_name}:")
            print(f"   Communicating: {summary['comm_status_overall']['Communicating']}")
            print(f"   Never Comm: {summary['comm_status_overall']['Never Comm']}")
            print(f"   Non Comm: {summary['comm_status_overall']['Non Comm']}")
            print(f"   Total Records: {summary['total_records']}")
            
            # Print missing data summary
            missing_summary = summary['missing_data_summary']
            print(f"\n🔍 MISSING DATA SUMMARY:")
            if missing_summary['meters_without_node_id'] is not None:
                print(f"   Meters without Node ID: {missing_summary['meters_without_node_id']}")
            if missing_summary['meters_without_routing_info'] is not None:
                print(f"   Meters without routing info: {missing_summary['meters_without_routing_info']}")
            if missing_summary['rows_missing_communicated_at'] is not None:
                print(f"   Rows missing Communicated At: {missing_summary['rows_missing_communicated_at']}")
            
            # Print mapping summary
            print(f"\n🔗 MAPPING SUMMARY:")
            for source_name, mapping_stats in missing_summary['source_mapping'].items():
                if source_name != 'Warehouse':  # Skip warehouse as it's the base
                    total = mapping_stats['total']
                    mapped = mapping_stats['mapped']
                    unmapped = mapping_stats['unmapped']
                    print(f"   {source_name}: Total={total}, Mapped={mapped}, Unmapped={unmapped}")
            
        print(f"\n✅ Processing completed for all DG subfolders")
        return True
    
    def get_expected_files(self):
        """Return list of expected raw data files"""
        return [
            "Warehouse.csv",
            "New_Service_connection.csv",
            "Merged_CI-MI.csv",
            "Meter_Installation.csv",
            "Node ID.xlsx",
            "Routings Part-1.xlsx",  # May have multiple parts
            "Routings Part-2.xlsx",  # May have multiple parts
        ]
    
    def get_file_column_mapping(self):
        """Define expected columns per file type"""
        return {
            "Warehouse.csv": [
                "Meter Serial No",
                "Feeder Name(From Field)",
                "Consumer Name",
                "Address",
                "Mobile Number",
                "Latitude",
                "Longitude",
                "Installed Sub Division",
                "Division",
                "Circle",
            ],
            "New_Service_connection.csv": [
                "New Meter QR Code ",  # Note the trailing space
                "Feeder Name(From Field)",
                "Consumer name",
                "address",
                "Mobile Number",
                "Latitude",
                "Longitude",
                "Sub Division Name",
            ],
            "Merged_CI-MI.csv": [
                "New Meter QR Code",
                "Feeder Name(From Field)",
                "Consumer Name",
                "Address",
                "Mobile Number",
                "Latitude",
                "Longitude",
                "Sub Division Name",
            ],
            "Meter_Installation.csv": [
                "New Meter Number Scan",
                "Feeder Name(From Field)",
                "Consumer Name",
                "Address",
                "Mobile Number",
                "Latitude",
                "Longitude",
                "Sub Division Name",
            ],
            "Node ID.xlsx": [
                "Meter Number",
                "NodeId",
            ],
            "Routings Part-1.xlsx": [  # Same structure as Part-2
                "Node ID",
                "Gateway ID",
                "Hop Count",
                "Sink ID",
                "Communicated At",
                "Source Endpoint",
            ],
            "Routings Part-2.xlsx": [  # Same structure as Part-1
                "Node ID",
                "Gateway ID",
                "Hop Count",
                "Sink ID",
                "Communicated At",
                "Source Endpoint",
            ],
        }
    
    def validate_filenames(self, raw_dir):
        """Validate that expected files are present in raw_data folder"""
        expected_files = self.get_expected_files()
        actual_files = {f.name for f in raw_dir.iterdir() if f.is_file()}
        
        missing_files = []
        extra_files = []
        
        # Check for missing files
        for expected in expected_files:
            if expected not in actual_files:
                # Special case: routing files may be named differently or have different parts
                if expected.startswith("Routings"):
                    routing_files = [f for f in actual_files if "Routings" in f and f.endswith((".xlsx", ".xls"))]
                    if not routing_files:
                        missing_files.append(expected)
                else:
                    missing_files.append(expected)
        
        # Check for extra files
        for actual in actual_files:
            if actual not in expected_files:
                # Allow other routing files that match pattern
                if not (actual.startswith("Routings") and actual.endswith((".xlsx", ".xls"))):
                    extra_files.append(actual)
        
        if missing_files or extra_files:
            print("\n❌ FILE VALIDATION ISSUES:")
            if missing_files:
                print(f"  Missing files: {missing_files}")
            if extra_files:
                print(f"  Unexpected files: {extra_files}")
            print("\n⚠️ Please upload the correct files and run again.")
            return False
        
        print("✅ All expected files present")
        return True
    
    def validate_columns(self, raw_dir):
        """Validate column headers in each file"""
        expected_columns = self.get_file_column_mapping()
        all_valid = True
        
        for file_path in raw_dir.iterdir():
            if not file_path.is_file():
                continue
            
            # Check if this file type is in our expected mapping
            file_key = file_path.name
            if file_path.name.startswith("Routings") and file_path.name.endswith((".xlsx", ".xls")):
                # Use any routing file as the template for column expectations
                file_key = "Routings Part-1.xlsx"
            
            if file_key in expected_columns:
                print(f"\n🔍 Validating columns in {file_path.name}...")
                
                try:
                    if file_path.suffix.lower() in ['.xlsx', '.xls']:
                        df = pd.read_excel(file_path, nrows=0)  # Read only headers
                    else:
                        df = pd.read_csv(file_path, nrows=0, low_memory=False)  # Read only headers
                    
                    actual_cols = set(df.columns.tolist())
                    expected_cols = set(expected_columns[file_key])
                    
                    missing_cols = expected_cols - actual_cols
                    extra_cols = actual_cols - expected_cols
                    
                    if missing_cols:
                        print(f"  ❌ Missing columns: {list(missing_cols)}")
                        all_valid = False
                    if extra_cols:
                        print(f"  ⚠️ Extra columns: {list(extra_cols)}")
                        # Not failing for extra columns, just warning
                    
                    if not missing_cols:
                        print(f"  ✅ Columns validated for {file_path.name}")
                        
                except Exception as e:
                    print(f"  ❌ Could not read {file_path.name}: {e}")
                    all_valid = False
        
        if not all_valid:
            print("\n⚠️ Column validation failed. Please fix the file columns and run again.")
        else:
            print("\n✅ All file columns validated successfully")
        
        return all_valid

    
    def run(self):
        """Run the daily reporting process (local only, no webhooks)"""
        try:
            print(f"\n🚀 Daily Reporting System Started")
            print(f"   Date: {self.today_date}")
            print(f"   Base Path: {self.base_path}")
            
            # Ensure base path exists
            if not self.base_path.exists():
                print(f"\n❌ Error: SharePoint base path does not exist: {self.base_path}")
                print(f"   Please ensure OneDrive is syncing and the path is correct.")
                sys.exit(1)
            
            self.process_comms_reporting()
            
            print(f"\n✅ Process completed")
            print(f"\n📂 Folder structure ready at: {self.report_date_folder}")
            print(f"   You can now upload raw data files to the DG*/raw_data/ folders")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    # Use SharePoint path as base path (adjust per user machine if needed)
    sharepoint_path = Path('/Users/rishubatra/Library/CloudStorage/OneDrive-SharedLibraries-SinhalUdyogpvtltd/Communication site - Daily_SLA_Reporting')
    
    reporter = DailyReporter(base_path=sharepoint_path)
    reporter.run()
