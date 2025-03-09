import os
import json
import tempfile
import matplotlib
matplotlib.use('Agg') 
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
import re
import io
from io import BytesIO
from app.parser_script import parse_log_file, parse_log_file2, parse_log_file3  # ✅ Absolute import

import matplotlib.pyplot as plt
import base64
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
import shutil
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

google_credentials_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")

if not google_credentials_base64:
    raise Exception("❌ GOOGLE_CREDENTIALS_BASE64 not found in environment variables.")

# ✅ Decode Base64 to JSON string
google_credentials_json = base64.b64decode(google_credentials_base64).decode("utf-8")

# ✅ Convert JSON string to dictionary
credentials_dict = json.loads(google_credentials_json)

# ✅ Authenticate with Google APIs
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict)
client = gspread.authorize(credentials)
service = build("sheets", "v4", credentials=credentials)
drive_service = build("drive", "v3", credentials=credentials)

app = Flask(__name__)
CORS(app)

def create_slt_tracker(merge_df):
    print("Columns in Merge Sheet:", merge_df.columns.tolist())

    required_columns = ["Marking Id", "Current Power Mode", "Final Bin", "Bank Related Fails", "Non-Bank Related Fails"]
    for column in required_columns:
        if column not in merge_df.columns:
            raise ValueError(f"Column '{column}' not found in the Merge sheet.")

    merge_df = merge_df.drop_duplicates(subset=["Marking Id", "Current Power Mode"], keep="first")

    unique_ids = merge_df["Marking Id"].unique()
    slt_tracker_df = pd.DataFrame({
        "Marking Id": unique_ids,
        "Binning_ECO": "",
        "Binning_SPORT": "",
        "Failure_Remarks_ECO": "",
        "Failure_Remarks_SPORT": "",
        "Final Binning": "",
    })

    binning_dict = merge_df.set_index(["Marking Id", "Current Power Mode"])["Final Bin"].to_dict()
    failure_dict = merge_df.set_index(["Marking Id", "Current Power Mode"])[["Bank Related Fails", "Non-Bank Related Fails"]].to_dict(orient='index')


    for index, row in slt_tracker_df.iterrows():
        marking_id = row["Marking Id"]
        
        if (marking_id, "ECO") in binning_dict:
            slt_tracker_df.at[index, "Binning_ECO"] = binning_dict[(marking_id, "ECO")]
        if (marking_id, "SPORT") in binning_dict:
            slt_tracker_df.at[index, "Binning_SPORT"] = binning_dict[(marking_id, "SPORT")]
        
        if (marking_id, "ECO") in failure_dict:
            slt_tracker_df.at[index, "Failure_Remarks_ECO"] = f"Bank Related: {failure_dict[(marking_id, 'ECO')]['Bank Related Fails']}, Non-Bank Related: {failure_dict[(marking_id, 'ECO')]['Non-Bank Related Fails']}"
        if (marking_id, "SPORT") in failure_dict:
            slt_tracker_df.at[index, "Failure_Remarks_SPORT"] = f"Bank Related: {failure_dict[(marking_id, 'SPORT')]['Bank Related Fails']}, Non-Bank Related: {failure_dict[(marking_id, 'SPORT')]['Non-Bank Related Fails']}"

    slt_tracker_df["Final Binning"] = slt_tracker_df.apply(calculate_final_binning, axis=1)
    
    return slt_tracker_df

def calculate_final_binning(row):
    eco_bin = row["Binning_ECO"].strip()
    sport_bin = row["Binning_SPORT"].strip()

    if eco_bin == "HB1(ECO)":
        return "HB1(ECO)"
    elif eco_bin == "Failed(ECO)" and sport_bin == "HB2(SPORT)":
        return "HB2(SPORT)"
    elif eco_bin == "HB1(ECO)" and sport_bin == "HB2(SPORT)":
        return "HB1(ECO)"
    elif eco_bin == "Failed(ECO)" and (sport_bin == "Failed(SPORT)" or not sport_bin):
        return "Failed(ECO)"
    return ""


def create_yield_summary(slt_tracker_df):
    # Calculate counts for each category
    failed_eco_count = (slt_tracker_df["Binning_ECO"] == "Failed(ECO)").sum()
    hb1_eco_count = (slt_tracker_df["Binning_ECO"] == "HB1(ECO)").sum()
    special_eco_count = (slt_tracker_df["Binning_ECO"] == "Special Case").sum()
    
    # Calculate Grand Total as the sum of individual counts
    grand_total = failed_eco_count + hb1_eco_count + special_eco_count
    
    summary = {
        "SPORT-from SLT Tracker": ["Failed (SPORT)", "HB1 (SPORT)", "Special Case", "Grand Total"],
        "Count of marking ID": [
            failed_eco_count,
            hb1_eco_count,
            special_eco_count,
            grand_total  # Corrected Grand Total
        ]
    }
    yield_df = pd.DataFrame(summary)

    return yield_df


def create_yield_summary2(slt_tracker_df):
    # Calculate counts for each category
    failed_sport_count = (slt_tracker_df["Binning_SPORT"] == "Failed(SPORT)").sum()
    hb1_sport_count = (slt_tracker_df["Binning_SPORT"] == "HB1(SPORT)").sum()
    special_case_count = (slt_tracker_df["Binning_SPORT"] == "Special Case").sum()
    
    # Calculate Grand Total as the sum of individual counts
    grand_total = failed_sport_count + hb1_sport_count + special_case_count
    
    summary = {
        "SPORT-from SLT Tracker": ["Failed (SPORT)", "HB1 (SPORT)", "Special Case", "Grand Total"],
        "Count of marking ID": [
            failed_sport_count,
            hb1_sport_count,
            special_case_count,
            grand_total  # Corrected Grand Total
        ]
    }
    yield_df1 = pd.DataFrame(summary)

    return yield_df1

def create_yield_summary3(slt_tracker_df):
    # Calculate counts for each category
    failed_eco_count = (slt_tracker_df["Final Binning"] == "Failed(ECO)").sum()
    hb1_eco_count = (slt_tracker_df["Final Binning"] == "HB1(ECO)").sum()
    special_eco_count = (slt_tracker_df["Final Binning"] == "Special Case").sum()
    failed_sport_count = (slt_tracker_df["Final Binning"] == "Failed(SPORT)").sum()
    hb1_sport_count = (slt_tracker_df["Final Binning"] == "HB1(SPORT)").sum()
    special_case_count = (slt_tracker_df["Final Binning"] == "Special Case").sum()
    
    # Calculate Grand Total as the sum of individual counts
    grand_total = failed_eco_count + hb1_eco_count + special_eco_count + failed_sport_count + hb1_sport_count + special_case_count
    
    summary = {
        "Final Binning": ["Failed (ECO)","HB1 (ECO)","Failed (SPORT)", "HB1 (SPORT)", "Special Case", "Grand Total"],
        "Count of marking ID": [
            failed_eco_count,
            hb1_eco_count,
            failed_sport_count,
            hb1_sport_count,
            special_case_count,
            grand_total  # Corrected Grand Total
        ]
    }
    yield_summary = pd.DataFrame(summary)

    return yield_summary



def count_bank_nonbank_failures_ECO(Merge):
    # Extract unique failure categories from both columns, excluding N/A values
    unique_bank_failures = Merge["Bank Related Fails"].dropna().replace("N/A", None).dropna().unique()
    unique_nonbank_failures = Merge["Non-Bank Related Fails"].dropna().replace("N/A", None).dropna().unique()
    
    # Initialize dictionaries for counts
    conditions = {failure: 0 for failure in unique_bank_failures}
    conditions.update({failure: 0 for failure in unique_nonbank_failures})

    # Count failures in ECO mode
    for key in conditions.keys():
        conditions[key] += ((Merge["Current Power Mode"] == "ECO") & 
                            ((Merge["Bank Related Fails"] == key) | 
                             (Merge["Non-Bank Related Fails"] == key))).sum()
    
    # Count adjacent failures
    adjacent_conditions = {key + " (Adjacent)": 0 for key in conditions.keys()}
    for key in conditions.keys():
        adjacent_conditions[key + " (Adjacent)"] += ((Merge["Current Power Mode"] == "ECO") & 
                                                     ((Merge["Bank Related Fails"] == key) | 
                                                      (Merge["Non-Bank Related Fails"] == key)) & 
                                                     (Merge["Adjacent"] == "Yes")).sum()

    # Merge counts
    conditions.update(adjacent_conditions)

    # Convert dictionary to DataFrame
    summary = pd.DataFrame(list(conditions.items()), columns=["failure_ECO", "Count"])

    # Filter out zero-count entries
    summary = summary[summary["Count"] > 0].reset_index(drop=True)

    # Compute grand total
    grand_total = summary["Count"].sum()

    # Append the Grand Total row
    summary.loc[len(summary.index)] = ["Grand Total", grand_total]

    return summary

def count_bank_nonbank_failures_SPORT(Merge):
    # Extract unique failure categories from both columns, excluding N/A values
    unique_bank_failures = Merge["Bank Related Fails"].dropna().replace("N/A", None).dropna().unique()
    unique_nonbank_failures = Merge["Non-Bank Related Fails"].dropna().replace("N/A", None).dropna().unique()
    
    # Initialize dictionaries for counts
    conditions = {failure: 0 for failure in unique_bank_failures}
    conditions.update({failure: 0 for failure in unique_nonbank_failures})

    # Count failures in ECO mode
    for key in conditions.keys():
        conditions[key] += ((Merge["Current Power Mode"] == "SPORT") & 
                            ((Merge["Bank Related Fails"] == key) | 
                             (Merge["Non-Bank Related Fails"] == key))).sum()
    
    # Count adjacent failures
    adjacent_conditions = {key + " (Adjacent)": 0 for key in conditions.keys()}
    for key in conditions.keys():
        adjacent_conditions[key + " (Adjacent)"] += ((Merge["Current Power Mode"] == "SPORT") & 
                                                     ((Merge["Bank Related Fails"] == key) | 
                                                      (Merge["Non-Bank Related Fails"] == key)) & 
                                                     (Merge["Adjacent"] == "Yes")).sum()

    # Merge counts
    conditions.update(adjacent_conditions)

    # Convert dictionary to DataFrame
    summary = pd.DataFrame(list(conditions.items()), columns=["Failure_SPORT", "Count"])

    # Filter out zero-count entries
    summary = summary[summary["Count"] > 0].reset_index(drop=True)

    # Compute grand total
    grand_total = summary["Count"].sum()

    # Append the Grand Total row
    summary.loc[len(summary.index)] = ["Grand Total", grand_total]

    return summary



'''def count_bank_nonbank_failures(Merge):
    # Extract unique failure categories from both columns, excluding N/A values
    unique_bank_failures = Merge["Bank Related Fails"].dropna().replace("N/A", None).dropna().unique()
    unique_nonbank_failures = Merge["Non-Bank Related Fails"].dropna().replace("N/A", None).dropna().unique()
    
    # Initialize dictionary for counts
    conditions = {failure: 0 for failure in unique_bank_failures}
    conditions.update({failure: 0 for failure in unique_nonbank_failures})

    # Count failures across all modes
    for key in conditions.keys():
        conditions[key] += ((Merge["Bank Related Fails"] == key) | (Merge["Non-Bank Related Fails"] == key)).sum()
    
    # Count adjacent failures
    adjacent_conditions = {key + " (Adjacent)": 0 for key in conditions.keys()}
    for key in conditions.keys():
        adjacent_conditions[key + " (Adjacent)"] += (((Merge["Bank Related Fails"] == key) | (Merge["Non-Bank Related Fails"] == key)) & (Merge["Adjacent"] == "Yes")).sum()
    
    # Merge counts
    conditions.update(adjacent_conditions)

    # Convert dictionary to DataFrame
    summary = pd.DataFrame(list(conditions.items()), columns=["Category", "Count"])

    # Filter out zero-count entries
    summary = summary[summary["Count"] > 0].reset_index(drop=True)

    # Compute grand total
    grand_total = summary["Count"].sum()

    # Append the Grand Total row
    summary.loc[len(summary.index)] = ["Grand Total", grand_total]

    return summary'''


def count_all_failures(Merge):
    # Count Bank Related Fails other than N/A or " " for ECO and SPORT separately
    bank_eco = ((Merge["Current Power Mode"] == "ECO") & Merge["Bank Related Fails"].notna() & (Merge["Bank Related Fails"] != " ")).sum()
    bank_sport = ((Merge["Current Power Mode"] == "SPORT") & Merge["Bank Related Fails"].notna() & (Merge["Bank Related Fails"] != " ")).sum()

    # Count Adjacent Column Failures other than N/A or " " for ECO and SPORT separately
    adjacent_eco = ((Merge["Current Power Mode"] == "ECO") & Merge["Adjacent"].notna() & (Merge["Adjacent"] != " ")).sum()
    adjacent_sport = ((Merge["Current Power Mode"] == "SPORT") & Merge["Adjacent"].notna() & (Merge["Adjacent"] != " ")).sum()

    # Count CMCM Functional Tests failures other than N/A, " ", "p" for ECO and SPORT separately
    cmcm_eco = ((Merge["Current Power Mode"] == "ECO") & Merge["CMCM Functional Tests"].notna() & (Merge["CMCM Functional Tests"] != " ") & (Merge["CMCM Functional Tests"] != "p")).sum()
    cmcm_sport = ((Merge["Current Power Mode"] == "SPORT") & Merge["CMCM Functional Tests"].notna() & (Merge["CMCM Functional Tests"] != " ") & (Merge["CMCM Functional Tests"] != "p")).sum()

    # Count LPDDR Test failures other than N/A, " ", "p" for ECO and SPORT separately
    lpddr_eco = ((Merge["Current Power Mode"] == "ECO") & Merge["LPDDR Test"].notna() & (Merge["LPDDR Test"] != " ") & (Merge["LPDDR Test"] != "p")).sum()
    lpddr_sport = ((Merge["Current Power Mode"] == "SPORT") & Merge["LPDDR Test"].notna() & (Merge["LPDDR Test"] != " ") & (Merge["LPDDR Test"] != "p")).sum()

    # Count Final Bin as passing when HB1 (ECO) or HB2 (SPORT)
    final_bin_pass_eco = (Merge["Final Bin"] == "HB1").sum()
    final_bin_pass_sport = (Merge["Final Bin"] == "HB2").sum()
    
    # Count Special Cases
    #special_case_eco = ((Merge["Current Power Mode"] == "ECO") & (Merge["Special Case"].notna())).sum()
    #special_case_sport = ((Merge["Current Power Mode"] == "SPORT") & (Merge["Special Case"].notna())).sum()
    
    # Total counts
    total_eco = bank_eco + adjacent_eco + cmcm_eco + lpddr_eco + final_bin_pass_eco 
    total_sport = bank_sport + adjacent_sport + cmcm_sport + lpddr_sport + final_bin_pass_sport 
    
    # Compute percentages
    def calc_percentage(count, total):
        return f"{(count / total * 100):.1f}%" if total > 0 else "0%"

    summary = pd.DataFrame({
        "Failure Modes": [
            "Bank-related Fails",
            "Adjacent Col Fails",
            "CMCM Func Fails",
            "LPDDR Fails",
            "Passing"
        ],
        "ECO": [bank_eco, adjacent_eco, cmcm_eco, lpddr_eco, final_bin_pass_eco],
        "SPORT": [bank_sport, adjacent_sport, cmcm_sport, lpddr_sport, final_bin_pass_sport],
        "ECO %": [calc_percentage(bank_eco, total_eco), calc_percentage(adjacent_eco, total_eco), calc_percentage(cmcm_eco, total_eco), calc_percentage(lpddr_eco, total_eco), calc_percentage(final_bin_pass_eco, total_eco)],
        "SPORT %": [calc_percentage(bank_sport, total_sport), calc_percentage(adjacent_sport, total_sport), calc_percentage(cmcm_sport, total_sport), calc_percentage(lpddr_sport, total_sport), calc_percentage(final_bin_pass_sport, total_sport)]
    })
    
    # Append total row
    summary.loc[len(summary.index)] = ["Total", total_eco, total_sport, "", ""]
    
    return summary



    

        



def clear_sheet(sheet_name):
    """Clears all data from a Google Sheet."""
    sheet = client.open("UAI").worksheet(sheet_name)
    sheet.clear()

# ✅ Function to update a Google Sheet
def update_google_sheet(sheet_name, data):
    """Updates a Google Sheet with new data."""
    sheet = client.open("UAI").worksheet(sheet_name)
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

# Helper function to update a sheet
def update_google_sheet1(sheet_name, data):

    sheet = client.open("UAI").worksheet(sheet_name)

    data_list = data.values.tolist()
    headers = data.columns.values.tolist()  # Extract column headers
    existing_data = sheet.get_all_values()
    
    # Find next empty row (leaving a gap for clarity)
    next_empty_row = len(existing_data) + 1  

    # Find next empty column (if previous data exists)
    next_empty_col = len(existing_data[0]) + 1 if existing_data else 1

    # Convert row/col index to A1 notation
    start_cell_headers = gspread.utils.rowcol_to_a1(next_empty_row, next_empty_col)
    start_cell_data = gspread.utils.rowcol_to_a1(next_empty_row + 1, next_empty_col)
    
    # Update headers first
    sheet.update(start_cell_headers, [headers], value_input_option='RAW')

    # Update data below the headers
    sheet.update(start_cell_data, data_list, value_input_option='RAW')





    



# Helper function to get existing data from a sheet
def get_existing_data(sheet_name):
    sheet = client.open("UAI").worksheet(sheet_name)
    existing_data = sheet.get_all_values()
    if existing_data:
        return pd.DataFrame(existing_data[1:], columns=existing_data[0])  # Skip headers
    else:
        return pd.DataFrame()


@app.route('/process_logs', methods=['POST'])
def process_logs():
    files = request.files.getlist('files')

    if not files:
        return {"error": "No files uploaded"}, 400

    sheet_data = {"Format 1": [], "Format 2": [], "Merge": []}

    # Process uploaded files
    for file in files:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file.filename)
            file.save(temp_file_path)

            try:
                df1 = parse_log_file(temp_file_path)  # Parse for Format 1
                df2 = parse_log_file2(temp_file_path)  # Parse for Format 2
                df3 = parse_log_file3(temp_file_path)  # Parse for Merge

                if df1 is not None and not df1.empty:
                    sheet_data["Format 1"].append(df1)
                if df2 is not None and not df2.empty:
                    sheet_data["Format 2"].append(df2)
                if df3 is not None and not df3.empty:
                    sheet_data["Merge"].append(df3)
            except Exception as e:
                return {"error": f"Error processing file {file.filename}: {str(e)}"}, 500

    try:
        # Ensure sheets exist
        ensure_sheet_exists("Format 1")
        ensure_sheet_exists("Format 2")
        ensure_sheet_exists("Merge")
        ensure_sheet_exists("SLT Tracker")
        ensure_sheet_exists("Yield")
        ensure_sheet_exists("Chart")

        # Update "Format 1" and "Format 2" sheets (existing logic)
        if sheet_data["Format 1"]:
            existing_format1_data = get_existing_data("Format 1")
            new_format1_data = pd.concat(sheet_data["Format 1"], ignore_index=True)
            combined_format1_data = pd.concat([existing_format1_data, new_format1_data], ignore_index=True)
            update_google_sheet("Format 1", combined_format1_data)

        if sheet_data["Format 2"]:
            existing_format2_data = get_existing_data("Format 2")
            new_format2_data = pd.concat(sheet_data["Format 2"], ignore_index=True)
            combined_format2_data = pd.concat([existing_format2_data, new_format2_data], ignore_index=True)
            update_google_sheet("Format 2", combined_format2_data)

        # Reset "SLT Tracker" and "Yield" sheets (existing logic)
        clear_sheet("SLT Tracker")
        clear_sheet("Yield")

        # Update "Merge" sheet
        if sheet_data["Merge"]:
            existing_merge_data = get_existing_data("Merge")
            new_merge_data = pd.concat(sheet_data["Merge"], ignore_index=True)
            combined_merge_data = pd.concat([existing_merge_data, new_merge_data], ignore_index=True)
            update_google_sheet("Merge", combined_merge_data)

            # Update "SLT Tracker" and "Yield" sheets (existing logic)
            slt_tracker_df = create_slt_tracker(combined_merge_data)
            update_google_sheet("SLT Tracker", slt_tracker_df)

            yield_df = create_yield_summary(slt_tracker_df)
            update_google_sheet1("Yield", yield_df)
            #update_google_sheet("Yield", yield_df1)

            yield_df2 = create_yield_summary2(slt_tracker_df)
            update_google_sheet1("Yield", yield_df2)

            yield_df3 = create_yield_summary3(slt_tracker_df)
            update_google_sheet1("Yield", yield_df3)

            yield_df4 = count_bank_nonbank_failures_ECO(combined_merge_data)
            update_google_sheet1("Yield", yield_df4)

            yield_df5 = count_bank_nonbank_failures_SPORT(combined_merge_data)
            update_google_sheet1("Yield",yield_df5)

            #yield_df6 = count_bank_nonbank_failures(combined_merge_data)
            #update_google_sheet1("Yield",yield_df6)

            yield_df7 = count_all_failures(combined_merge_data)
            update_google_sheet1("Yield",yield_df7)


         

            

            # Generate pie charts for ECO and SPORT modes
            test_columns = ['Noc PassThrough', 'Noc Route', 'Bank Cram Test', 'CMCM Functional Tests', 'UCM_ALL', 'LPDDR Test', 'Failed Banks']
            eco_chart = generate_combined_pie_chart(combined_merge_data[combined_merge_data['Current Power Mode'] == 'ECO'], "ECO Mode - Combined Test Results", test_columns)
            sport_chart = generate_combined_pie_chart(combined_merge_data[combined_merge_data['Current Power Mode'] == 'SPORT'], "SPORT Mode - Combined Test Results", test_columns)

            # Update "Chart" sheet with pie chart URLs
            update_chart_sheet(eco_chart, sport_chart)

        return jsonify({"message": "Google Sheets updated successfully"}), 200
    except Exception as e:
        print(f"Error updating Google Sheets: {str(e)}")
        return {"error": f"Error updating Google Sheets: {str(e)}"}, 500

def ensure_sheet_exists(sheet_name):
    """Ensure that the specified sheet exists in the Google Sheets document."""

    # ✅ Get the list of sheets in the document
    sheet_metadata = service.spreadsheets().get(spreadsheetId="12pBanisGaUfCpTrKaKScpevxw_V_px66WFIzNzaLee8").execute()
    sheets = sheet_metadata.get('sheets', [])

    # ✅ Check if the sheet already exists
    sheet_exists = any(sheet['properties']['title'] == sheet_name for sheet in sheets)

    if not sheet_exists:
        # ✅ Create the sheet if it doesn't exist
        requests = [{
            "addSheet": {
                "properties": {
                    "title": sheet_name
                }
            }
        }]
        body = {'requests': requests}
        service.spreadsheets().batchUpdate(spreadsheetId="12pBanisGaUfCpTrKaKScpevxw_V_px66WFIzNzaLee8", body=body).execute()
        print(f"✅ Created new sheet: {sheet_name}")
    else:
        print(f"✅ Sheet '{sheet_name}' already exists.")



def upload_to_google_drive(image_base64, filename):
    """Uploads a base64-encoded image to Google Drive and returns a publicly accessible URL."""

    # ✅ Decode base64 image
    image_data = base64.b64decode(image_base64)

    # ✅ Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, filename)

    try:
        # ✅ Save the image to a temporary file
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(image_data)

        # ✅ Upload the file to Google Drive
        file_metadata = {"name": filename}
        media = MediaFileUpload(temp_file_path, mimetype="image/png")
        file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

        # ✅ Make the file publicly accessible
        drive_service.permissions().create(
            fileId=file["id"],
            body={"role": "reader", "type": "anyone"}
        ).execute()

        # ✅ Get the publicly accessible URL
        image_url = f"https://drive.google.com/uc?export=view&id={file['id']}"
        return image_url

    finally:
        # ✅ Ensure the temporary directory is deleted, even if an error occurs
        shutil.rmtree(temp_dir, ignore_errors=True)


def fetch_merge_sheet_data():
    """Fetches existing data from the Merge sheet and returns it as a DataFrame."""
    try:
        # ✅ Open the Google Sheet & Fetch data
        sheet = client.open("UAI").worksheet("Merge")
        data = sheet.get_all_records()

        if not data:
            return pd.DataFrame()  # Return empty DataFrame if no data exists
        
        return pd.DataFrame(data)

    except Exception as e:
        print(f"❌ Error fetching Merge sheet data: {e}")
        return pd.DataFrame()  # Return empty DataFrame in case of failure





def extract_numeric(value):
    """Extracts numeric part from a string like '12F' -> 12, or handles 'P' as 100% passed."""
    if isinstance(value, str):
        value = value.strip().upper()
        if value == "P":
            return 0  # Ignore "P" (100% passed)
        match = re.search(r'(\d+)', value)
        return int(match.group(1)) if match else 0
    return 0

def generate_combined_pie_chart(df, title, test_columns):

    combined_data = {}

    for column in test_columns:
        if column in df.columns:
            df[column] = df[column].astype(str)  # Convert to string to avoid errors
            df[column] = df[column].apply(extract_numeric)  # Extract numeric values
            combined_data[column] = df[column].sum()  # Sum values per test column

    # Ensure there is valid data
    combined_data = {k: v for k, v in combined_data.items() if v > 0}
    if not combined_data:
        return None

    labels = list(combined_data.keys())
    sizes = list(combined_data.values())

    # Define colors
    colors = plt.cm.Paired(range(len(labels)))

    # Create the pie chart
    plt.figure(figsize=(5, 5))
    plt.pie(
        sizes,
        labels=[label if len(label) <= 15 else label[:10] + '...' for label in labels],
        colors=colors,
        autopct='%1.1f%%',
        pctdistance=0.75,
        textprops={'fontsize': 7}
    )
    
    plt.axis('equal')
    plt.title(title)

    # Convert chart to base64 image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()
    return img_base64




def update_chart_sheet(eco_chart, sport_chart):
    """Updates the 'Chart' sheet with pie chart URLs for ECO and SPORT modes."""
    try:
        # ✅ Open the Google Sheet & Fetch Chart sheet
        sheet = client.open("UAI").worksheet("Chart")

        # ✅ Clear the sheet
        sheet.clear()

        # ✅ Add headers
        sheet.update([["ECO Mode Chart", "SPORT Mode Chart"]])

        # ✅ Upload pie charts to Google Drive and get URLs
        if eco_chart:
            eco_url = upload_to_google_drive(eco_chart, "eco_chart.png")
            sheet.update_cell(2, 1, eco_url)  # ✅ Insert ECO chart URL

        if sport_chart:
            sport_url = upload_to_google_drive(sport_chart, "sport_chart.png")
            sheet.update_cell(2, 2, sport_url)  # ✅ Insert SPORT chart URL

        print("✅ Chart sheet updated successfully.")

    except Exception as e:
        print(f"❌ Error updating Chart sheet: {e}")



@app.route('/get_piechart', methods=['POST'])
def get_piechart():
    """Generate separate pie charts for ECO and SPORT power modes for each test column."""
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files uploaded"}), 400
    
    sheet_data = {"Merge": []}

    for file in files:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name

        try:
            df_merge = parse_log_file3(temp_file_path)  # Ensure `parse_log_file3()` is correctly implemented
            if df_merge is not None and not df_merge.empty:
                sheet_data["Merge"].append(df_merge)
        except Exception as e:
            return jsonify({"error": f"Error parsing {file.filename}: {e}"}), 400
        finally:
            os.remove(temp_file_path)

    if not sheet_data["Merge"]:
        return jsonify({"error": "No valid merged data found"}), 400

    combined_df = pd.concat(sheet_data["Merge"], ignore_index=True)

    if 'Current Power Mode' not in combined_df.columns:
        return jsonify({"error": "No 'Current Power Mode' column found in the data"}), 400

    # Filter data based on power modes
    eco_df = combined_df[combined_df['Current Power Mode'] == 'ECO']
    sport_df = combined_df[combined_df['Current Power Mode'] == 'SPORT']

    test_columns = ['Noc PassThrough', 'Noc Route', 'Bank Cram Test', 'CMCM Functional Tests', 'UCM_ALL', 'LPDDR Test', 'Failed Banks']

    # Generate combined pie charts for ECO and SPORT modes
    eco_chart = generate_combined_pie_chart(eco_df, "ECO Mode - Combined Test Results", test_columns)
    sport_chart = generate_combined_pie_chart(sport_df, "SPORT Mode - Combined Test Results", test_columns)
    
    pie_charts = {
        "ECO": f"data:image/png;base64,{eco_chart}" if eco_chart else None,
        "SPORT": f"data:image/png;base64,{sport_chart}" if sport_chart else None
    }

    return jsonify(pie_charts)



if __name__ == "__main__":
    app.run()
