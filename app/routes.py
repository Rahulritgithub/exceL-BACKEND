from flask import request, jsonify
import pandas as pd
import tempfile
import os
from scripts.parser_script import parse_log_file, parse_log_file2, parse_log_file3
from scripts.app import (
    clear_sheet, update_google_sheet, update_google_sheet1, get_existing_data,
    ensure_sheet_exists, upload_to_google_drive, update_chart_sheet,
    create_slt_tracker, create_yield_summary, create_yield_summary2,
    create_yield_summary3, count_bank_nonbank_failures_ECO, count_bank_nonbank_failures_SPORT,generate_combined_pie_chart
)

def process_logs_logic(files):
    if not files:
        return {"error": "No files uploaded"}, 400

    sheet_data = {"Format 1": [], "Format 2": [], "Merge": []}

    for file in files:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file.filename)
            file.save(temp_file_path)

            try:
                df1 = parse_log_file(temp_file_path)
                df2 = parse_log_file2(temp_file_path)
                df3 = parse_log_file3(temp_file_path)

                if df1 is not None and not df1.empty:
                    sheet_data["Format 1"].append(df1)
                if df2 is not None and not df2.empty:
                    sheet_data["Format 2"].append(df2)
                if df3 is not None and not df3.empty:
                    sheet_data["Merge"].append(df3)
            except Exception as e:
                return {"error": f"Error processing file {file.filename}: {str(e)}"}, 500

    try:
        ensure_sheet_exists("Format 1")
        ensure_sheet_exists("Format 2")
        ensure_sheet_exists("Merge")
        ensure_sheet_exists("SLT Tracker")
        ensure_sheet_exists("Yield")
        ensure_sheet_exists("Chart")

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

        clear_sheet("SLT Tracker")
        clear_sheet("Yield")

        if sheet_data["Merge"]:
            existing_merge_data = get_existing_data("Merge")
            new_merge_data = pd.concat(sheet_data["Merge"], ignore_index=True)
            combined_merge_data = pd.concat([existing_merge_data, new_merge_data], ignore_index=True)
            update_google_sheet("Merge", combined_merge_data)

            slt_tracker_df = create_slt_tracker(combined_merge_data)
            update_google_sheet("SLT Tracker", slt_tracker_df)

            yield_df = create_yield_summary(slt_tracker_df)
            update_google_sheet1("Yield", yield_df)

            yield_df2 = create_yield_summary2(slt_tracker_df)
            update_google_sheet1("Yield", yield_df2)

            yield_df3 = create_yield_summary3(slt_tracker_df)
            update_google_sheet1("Yield", yield_df3)

            yield_df4 = count_bank_nonbank_failures_ECO(combined_merge_data)
            update_google_sheet1("Yield", yield_df4)

            yield_df5 = count_bank_nonbank_failures_SPORT(combined_merge_data)
            update_google_sheet1("Yield", yield_df5)

            test_columns = ['Noc PassThrough', 'Noc Route', 'Bank Cram Test', 'CMCM Functional Tests', 'UCM_ALL', 'LPDDR Test', 'Failed Banks']
            eco_chart = generate_combined_pie_chart(combined_merge_data[combined_merge_data['Current Power Mode'] == 'ECO'], "ECO Mode - Combined Test Results", test_columns)
            sport_chart = generate_combined_pie_chart(combined_merge_data[combined_merge_data['Current Power Mode'] == 'SPORT'], "SPORT Mode - Combined Test Results", test_columns)

            update_chart_sheet(eco_chart, sport_chart)

        return jsonify({"message": "Google Sheets updated successfully"}), 200
    except Exception as e:
        print(f"Error updating Google Sheets: {str(e)}")
        return {"error": f"Error updating Google Sheets: {str(e)}"}, 500

def get_piechart_logic(files):
    if not files:
        return {"error": "No files uploaded"}, 400
    
    sheet_data = {"Merge": []}

    for file in files:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file.read())
            temp_file_path = temp_file.name

        try:
            df_merge = parse_log_file3(temp_file_path)
            if df_merge is not None and not df_merge.empty:
                sheet_data["Merge"].append(df_merge)
        except Exception as e:
            return {"error": f"Error parsing {file.filename}: {e}"}, 400
        finally:
            os.remove(temp_file_path)

    if not sheet_data["Merge"]:
        return {"error": "No valid merged data found"}, 400

    combined_df = pd.concat(sheet_data["Merge"], ignore_index=True)

    if 'Current Power Mode' not in combined_df.columns:
        return {"error": "No 'Current Power Mode' column found in the data"}, 400

    eco_df = combined_df[combined_df['Current Power Mode'] == 'ECO']
    sport_df = combined_df[combined_df['Current Power Mode'] == 'SPORT']

    test_columns = ['Noc PassThrough', 'Noc Route', 'Bank Cram Test', 'CMCM Functional Tests', 'UCM_ALL', 'LPDDR Test', 'Failed Banks']

    eco_chart = generate_combined_pie_chart(eco_df, "ECO Mode - Combined Test Results", test_columns)
    sport_chart = generate_combined_pie_chart(sport_df, "SPORT Mode - Combined Test Results", test_columns)
    
    pie_charts = {
        "ECO": f"data:image/png;base64,{eco_chart}" if eco_chart else None,
        "SPORT": f"data:image/png;base64,{sport_chart}" if sport_chart else None
    }

    return pie_charts
