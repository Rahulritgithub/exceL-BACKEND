import re
import os
import pandas as pd
from glob import glob

def parse_log_file(log_file_path: str) ->  pd.DataFrame:
    """
    Parse a log file and extract structured data
    Returns dictionary with 40+ extracted metrics
    """
    columns = [
    "File Name", "Timestamp", "Chip Number", "Marking Id", "Chip Version",
    "SLT Test Version", "Current Frequency", "Current Power Mode",
    "VDDP", "VDDM", "VDDCORE", "VDDHF", "VDDIO", "VDDWL", 
    "Banks Failed", "Columns with Failures","Bank Co-ordinates with Failures",
    "Banks Repairable after CRAM test", "Banks Failed after CRAM Test", "Repair Data Applied", "Remark", "Total Banks Failed"
]

    test_columns = [
    "ATE_CMD_BANK_PE_ALL_REG_ACCESS", "ATE_CMD_BANK_PE_MACC", "ATE_CMD_BANK_PE_MULT5X5", 
    "ATE_CMD_BANK_PE_ACC", "ATE_CMD_BANK_PE_ROTATE", "ATE_CMD_BANK_PE_NORM_PRIORITY", 
    "ATE_CMD_BANK_PE_GEMV_FP8", "ATE_CMD_BANK_PE_GEMV_FP8_SFP16", "ATE_CMD_BANK_PE_GEMV_SFP16", 
    "ATE_CMD_BANK_PE_GEMV_INT4", "ATE_CMD_BANK_PE_GEMV_INT8", "ATE_CMD_BANK_PE_ROW_REDUCE", 
    "ATE_CMD_BANK_PE_NORM_REDUCE_ADDER", "ATE_CMD_BANK_PE_NORM_BYTEADDER_SHIFT_PRIO", 
    "ATE_CMD_BANK_PE_GEMV_BROADCAST", "ATE_CMD_BANK_PE_GEMV_SPARSITY", "ATE_CMD_BANK_PE_NORM_DATA_MUX", 
    "ATE_CMD_BANK_GEMV_HALF_ZERO", "ATE_CMD_BANK_PE_NORM", "ATE_CMD_BANK_NOC_PERECV_STORE_FRWD_NS", 
    "ATE_CMD_BANK_NOC_PERECV_STORE_FRWD_SN", "ATE_CMD_BANK_NOC_PASSTHROUGH_N", 
    "ATE_CMD_BANK_NOC_PASSTHROUGH_S", "ATE_CMD_BANK_NOC_PASSTHROUGH_W", "ATE_CMD_BANK_NOC_ROUTE_N", 
    "ATE_CMD_BANK_NOC_ROUTE_S", "ATE_CMD_BANK_NOC_ROUTE_W", "ATE_CMD_BANK_NOC_BUFFER", 
    "ATE_CMD_BANK_CRAM_BIST_10N", "ATE_CMD_BANK_CRAM_BIST_FULL", "ATE_CMD_BANK_CRAM_BIST_B2B", 
    "ATE_CMD_BANK_CRAM_BIST_BURST", "ATE_CMD_CMCM_ALL_FUNCTIONAL", "ATE_CMD_UCM_ALL", 
    "ATE_CMD_PCM_BANK_IDC_PING_S", "ATE_CMD_DDR_APB_ACCESS", "ATE_CMD_DDR_MCU_MEM", 
    "ATE_CMD_DDR_ACK_HO", "ATE_CMD_DDR_ACK_FS", "ATE_CMD_DDR_PHYINIT_TRAIN_NORTH", 
    "ATE_CMD_DDR_PHYINIT_ALL_NORTH_WR_RD", "ATE_CMD_DDR_MEM_SWP_WRRD_N", "ATE_CMD_DDR_MEM_SWP_RDLOOP_N", 
    "ATE_CMD_DDR_PHYINIT_TRAIN_EAST", "ATE_CMD_DDR_PHYINIT_ALL_EAST_WR_RD", "ATE_CMD_DDR_MEM_SWP_WRRD_E", 
    "ATE_CMD_DDR_MEM_SWP_RDLOOP_E", "ATE_CMD_DDR_PHYINIT_FULL"
]
    

    test_summary = [
    "ATE_CMD_BANK_PE_ALL_REG_ACCESS_grade", "ATE_CMD_BANK_PE_MACC_grade", "ATE_CMD_BANK_PE_MULT5X5_grade",
    "ATE_CMD_BANK_PE_ACC_grade", "ATE_CMD_BANK_PE_ROTATE_grade", "ATE_CMD_BANK_PE_NORM_PRIORITY_grade",
    "ATE_CMD_BANK_PE_GEMV_FP8_grade", "ATE_CMD_BANK_PE_GEMV_FP8_SFP16_grade", "ATE_CMD_BANK_PE_GEMV_SFP16_grade",
    "ATE_CMD_BANK_PE_GEMV_INT4_grade", "ATE_CMD_BANK_PE_GEMV_INT8_grade", "ATE_CMD_BANK_PE_ROW_REDUCE_grade",
    "ATE_CMD_BANK_PE_NORM_REDUCE_ADDER_grade", "ATE_CMD_BANK_PE_NORM_BYTEADDER_SHIFT_PRIO_grade",
    "ATE_CMD_BANK_PE_GEMV_BROADCAST_grade", "ATE_CMD_BANK_PE_GEMV_SPARSITY_grade", "ATE_CMD_BANK_PE_NORM_DATA_MUX_grade",
    "ATE_CMD_BANK_GEMV_HALF_ZERO_grade", "ATE_CMD_BANK_PE_NORM_grade", "ATE_CMD_BANK_NOC_PERECV_STORE_FRWD_NS_grade",
    "ATE_CMD_BANK_NOC_PERECV_STORE_FRWD_SN_grade", "ATE_CMD_BANK_NOC_PASSTHROUGH_N_grade",
    "ATE_CMD_BANK_NOC_PASSTHROUGH_S_grade", "ATE_CMD_BANK_NOC_PASSTHROUGH_W_grade", "ATE_CMD_BANK_NOC_ROUTE_N_grade",
    "ATE_CMD_BANK_NOC_ROUTE_S_grade", "ATE_CMD_BANK_NOC_ROUTE_W_grade", "ATE_CMD_BANK_NOC_BUFFER_grade",
    "ATE_CMD_BANK_CRAM_BIST_10N_grade", "ATE_CMD_BANK_CRAM_BIST_FULL_grade", "ATE_CMD_BANK_CRAM_BIST_B2B_grade",
    "ATE_CMD_BANK_CRAM_BIST_BURST_grade", "ATE_CMD_CMCM_ALL_FUNCTIONAL_grade", "ATE_CMD_UCM_ALL_grade",
    "ATE_CMD_PCM_BANK_IDC_PING_S_grade", "ATE_CMD_DDR_APB_ACCESS_grade", "ATE_CMD_DDR_MCU_MEM_grade",
    "ATE_CMD_DDR_ACK_HO_grade", "ATE_CMD_DDR_ACK_FS_grade", "ATE_CMD_DDR_PHYINIT_TRAIN_NORTH_grade",
    "ATE_CMD_DDR_PHYINIT_ALL_NORTH_WR_RD_grade", "ATE_CMD_DDR_MEM_SWP_WRRD_N_grade", "ATE_CMD_DDR_MEM_SWP_RDLOOP_N_grade",
    "ATE_CMD_DDR_PHYINIT_TRAIN_EAST_grade", "ATE_CMD_DDR_PHYINIT_ALL_EAST_WR_RD_grade", "ATE_CMD_DDR_MEM_SWP_WRRD_E_grade",
    "ATE_CMD_DDR_MEM_SWP_RDLOOP_E_grade", "ATE_CMD_DDR_PHYINIT_FULL_grade"
]
    

    patterns = {
    "Timestamp": r"curr_time=(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})",
    "Chip Number": r"chip_id=([\w\d\.]+)",
    "Marking Id": r"Marking ID: ([\w\d\-\_]+)",
    "Chip Version": r"Chip version: ([\w\d]+)",
    "SLT Test Version": r"Diagnostic fw version: (v[\d\.]+)",
    "Current Frequency": r"ctUtilsPower : INFO : Current Frequency: (\d+)",
    "Current Power Mode": r"ctUtilsPower : INFO : Current Power Mode: (\w+)",
    "VDDP": r"VDDP: (\d+)",
    "VDDM": r"VDDM: (\d+)",
    "VDDCORE": r"VDDCORE: (\d+)",
    "VDDHF": r"VDDHF: (\d+)",
    "VDDIO": r"VDDIO: (\d+)",
    "VDDWL": r"VDDWL: (\d+)",
    "Banks Failed": r"Banks Failed: \{([\d, ]+)\}",
    
}

    patterns1 = {
    "Columns with Failures": r"Columns with failures: \{([\d, ]+)\}",
    "Banks Repairable after CRAM test": r"Banks Repairable after CRAM test: \{([\d, ]+)\}",
    "Banks Failed after CRAM Test": r"Banks Failed after CRAM [Tt]est:\s*\{([\d, ]+)\}",
    "Repair Data Applied": r"Repair Data Applied: \{(.*?)\}",
    "Total Banks Failed": r"Total Numbers of Banks Failed: (\d+)",
    "Bank Co-ordinates with Failures": r"Bank Coordinates with failures:\s*(\[\[.*?\]\])",

}

    file_name = os.path.basename(log_file_path)

    extracted_data = {col: "N/A" for col in columns + test_columns + test_summary}
    
    extracted_data["File Name"] = file_name  # Store file name
# Function to extract data from a single log file
    
    with open(log_file_path, "r") as log_file:
        log_content = log_file.read()
        for key, pattern in patterns.items():
            match = re.search(pattern, log_content)
            if match:
                extracted_data[key] = match.group(1)

        for key, pattern in patterns1.items():
            match = re.search(pattern, log_content)
            if match:
                extracted_data[key] = match.group(1)

        for summary in test_summary:
            pattern2 = rf"Test Name: {summary.replace('_grade', '')} : (PASS|FAIL)"
            match = re.search(pattern2, log_content)
            if match:
                extracted_data[summary] = match.group(1)

    # Extract test_columns data
        for test_col in test_columns:
            pattern = rf"{test_col}': (set\(\)|\[.*?\]|\{{.*?\}}|\d+)"
            match = re.search(pattern, log_content)
            if match:
                extracted_data[test_col] = match.group(1)

    def extract_bank_coordinates(text):
        pattern = r"Bank Coordinates with failures:\s*(\[\[.*?\]\])"
        match = re.search(pattern, text)

        if match:
            coordinates_str = match.group(1)  # Extract full list as a string
            coordinates_list = eval(coordinates_str)  # Convert string to list
        
        # Format the extracted data
            if len(coordinates_list) > 5:
                return ", ".join(map(str, coordinates_list[:5])) + ", +more..."
            else:
                return ", ".join(map(str, coordinates_list))
    
        return "N/A"

    
    def count_failures(test_group, extracted_data):
        fail_count = 0
        for test in test_group:
            if extracted_data.get(f"{test}_grade") == "FAIL":
                fail_count += 1
        return f"{fail_count}f" if fail_count > 0 else "P"
    

    extracted_data["Failed Banks"] = count_failures([
    "ATE_CMD_BANK_PE_ALL_REG_ACCESS", "ATE_CMD_BANK_PE_MACC", "ATE_CMD_BANK_PE_MULT5X5", 
    "ATE_CMD_BANK_PE_ACC", "ATE_CMD_BANK_PE_ROTATE", "ATE_CMD_BANK_PE_NORM_PRIORITY", 
    "ATE_CMD_BANK_PE_GEMV_FP8", "ATE_CMD_BANK_PE_GEMV_FP8_SFP16", "ATE_CMD_BANK_PE_GEMV_SFP16", 
    "ATE_CMD_BANK_PE_GEMV_INT4", "ATE_CMD_BANK_PE_GEMV_INT8", "ATE_CMD_BANK_PE_ROW_REDUCE", 
    "ATE_CMD_BANK_PE_NORM_REDUCE_ADDER", "ATE_CMD_BANK_PE_NORM_BYTEADDER_SHIFT_PRIO", 
    "ATE_CMD_BANK_PE_GEMV_BROADCAST", "ATE_CMD_BANK_PE_GEMV_SPARSITY", "ATE_CMD_BANK_PE_NORM_DATA_MUX", 
    "ATE_CMD_BANK_GEMV_HALF_ZERO", "ATE_CMD_BANK_PE_NORM", "ATE_CMD_BANK_PE_ZERO_DETECT", "ATE_CMD_BANK_NOC_BUFFER"
], extracted_data)

    extracted_data["Noc PassThrough"] = count_failures([
    "ATE_CMD_BANK_NOC_PASSTHROUGH_N", "ATE_CMD_BANK_NOC_PASSTHROUGH_S", 
    "ATE_CMD_BANK_NOC_PASSTHROUGH_E", "ATE_CMD_BANK_NOC_PASSTHROUGH_W"
], extracted_data)
    
    extracted_data["Noc Route"] = count_failures([
    "ATE_CMD_BANK_NOC_ROUTE_N", "ATE_CMD_BANK_NOC_ROUTE_S", 
    "ATE_CMD_BANK_NOC_ROUTE_E", "ATE_CMD_BANK_NOC_ROUTE_W"
], extracted_data)

    extracted_data["Bank Cram Test"] = count_failures([
    "ATE_CMD_BANK_CRAM_BIST_10N", "ATE_CMD_BANK_CRAM_BIST_FULL", 
    "ATE_CMD_BANK_CRAM_BIST_B2B", "ATE_CMD_BANK_CRAM_BIST_BURST"
], extracted_data)

    extracted_data["CMCM Functional Tests"] = count_failures([
    "ATE_CMD_CMCM_ALL_FUNCTIONAL"
], extracted_data)

    extracted_data["UCM_ALL"] = count_failures([
    "ATE_CMD_UCM_ALL"
], extracted_data)

    extracted_data["LPDDR Test"] = count_failures([
    "ATE_CMD_DDR_APB_ACCESS", "ATE_CMD_DDR_MCU_MEM", "ATE_CMD_DDR_ACK_HO", 
    "ATE_CMD_DDR_ACK_FS", "ATE_CMD_DDR_PHYINIT_TRAIN_NORTH", 
    "ATE_CMD_DDR_PHYINIT_ALL_NORTH_WR_RD", "ATE_CMD_DDR_MEM_SWP_WRRD_N", 
    "ATE_CMD_DDR_MEM_SWP_RDLOOP_N", "ATE_CMD_DDR_PHYINIT_TRAIN_EAST", 
    "ATE_CMD_DDR_PHYINIT_ALL_EAST_WR_RD", "ATE_CMD_DDR_MEM_SWP_WRRD_E", 
    "ATE_CMD_DDR_MEM_SWP_RDLOOP_E", "ATE_CMD_DDR_PHYINIT_FULL"
], extracted_data)

    def get_failure_count(value):
        if value == "P":
            return 0
        elif value.endswith('f'):
            try:
                return int(value[:-1])  # Extract numeric part before 'f'
            except:
                return 0
        return 0
    fb_count = get_failure_count(extracted_data.get("Failed Banks", ""))
    bct_count = get_failure_count(extracted_data.get("Bank Cram Test", ""))
    ucm_count = get_failure_count(extracted_data.get("UCM_ALL", ""))
    lpddr_count = get_failure_count(extracted_data.get("LPDDR Test", ""))
    cmcm_count = get_failure_count(extracted_data.get("CMCM Functional Tests", ""))
    noc_route_count = get_failure_count(extracted_data.get("Noc Route", ""))
    noc_passthrough_count = get_failure_count(extracted_data.get("Noc Passthrough", ""))

    bank_failures=[]
    Remarks = []
    Non_Bank = []

    if fb_count >= 1:
        Remarks.append("Failed Banks")
        bank_failures.append("Failed Banks")
    if bct_count >= 1:
        Remarks.append("Bank Cram Test")
        bank_failures.append("Bank Cram Test")
    if ucm_count >= 1:
        Remarks.append("UCM")
        Non_Bank.append("UCM")
    if lpddr_count >= 1:
        Remarks.append("LPDDR")
        Non_Bank.append("LPDDR")
    if cmcm_count >= 1:
        Remarks.append("CMCM")
        Non_Bank.append("CMCM")
    if noc_route_count >= 1:
        Remarks.append("Noc Route")
        Non_Bank.append("Noc Route")
    if noc_passthrough_count >= 1:
        Remarks.append("Noc Passthrough")
        Non_Bank.append("Noc Passthrough")

    if bank_failures:
        extracted_data["Bank Related Fails"] = f"Bank-rel({', '.join(bank_failures)})"
    else:
        extracted_data["Bank Related Fails"] = "N/A"

    if Non_Bank:
        extracted_data["Non-Bank Related Fails"] = f"Non-Bank-rel({', '.join(Non_Bank)})"
    else:
        extracted_data["Non-Bank Related Fails"] = "N/A"

    if Remarks:
        extracted_data["Remarks"] = f"Bank-rel({', '.join(Remarks)})"
    else:
        extracted_data["Remarks"] = "N/A"

    def format_adjacent_failures(numbers):
        numbers = sorted(set(map(int, numbers.split(", "))))  # Convert to sorted list of integers
        if not numbers:
            return "No Adjacent Failures"
        ranges = []
        start = numbers[0]
        prev = numbers[0]
        for num in numbers[1:]:
            if num == prev + 1:
                prev = num  # Continue range
            else:
                ranges.append(f"{start}-{prev}" if start != prev else str(start))
                start = prev = num  # Start new range
        ranges.append(f"{start}-{prev}" if start != prev else str(start))
        return ", ".join(ranges)

    if extracted_data["Columns with Failures"] != "N/A":
        extracted_data["Adjacent Columns Failures"] = format_adjacent_failures(extracted_data["Columns with Failures"])

    def format_multiple_values(value, limit=5):
        if value == "N/A":
            return value
        if isinstance(value, str):
            if value.startswith("{") or value.startswith("["):
                values = re.findall(r"\d+", value)
                if len(values) > limit:
                    return ", ".join(values[:limit]) + ", +more..."
                else:
                    return ", ".join(values)
            return value
    for key in ["Banks Failed", "Columns with Failures", "Banks Repairable after CRAM test", "Banks Failed after CRAM Test"]:
        extracted_data[key] = format_multiple_values(extracted_data[key])

    if extracted_data["Repair Data Applied"] != "N/A":
        repair_data_list = re.findall(r"(\d+: \[\d+, \d+\])", extracted_data["Repair Data Applied"])
        if len(repair_data_list) > 5:
            extracted_data["Repair Data Applied"] = ", ".join(repair_data_list[:5]) + ", +more..."
        else:
            extracted_data["Repair Data Applied"] = ", ".join(repair_data_list)

    if extracted_data["Adjacent Columns Failures"] != "N/A":
        extracted_data["Adjacent"] = "YES"
    else:
        extracted_data["Adjacent"] = "NO"

    if "More than 2 bad columns. Bad CHIP" in log_content:
        extracted_data["Remark"] = "More than 2 bad columns. Bad CHIP"
    elif "passing" in log_content:
        extracted_data["Remark"] = "passing"
    elif "BAD CHIP. Below Test failed" in log_content:
        extracted_data["Remark"] = "BAD CHIP. Below Test failed"
    else:
        extracted_data["Remark"] = "No match found"

# Convert "Total Banks Failed" safely to integer
    total_banks_failed = int(extracted_data.get("Total Banks Failed", "0"))  # Default "0" to avoid errors

    power_mode = extracted_data.get("Current Power Mode", "").strip().upper()

# Initialize Final Bin
    final_bin = "N/A"

    if power_mode == "ECO":
        if total_banks_failed <= 2:
            final_bin = "Failed(ECO)"
        elif extracted_data.get("Adjacent") == "YES":
            final_bin = "Failed(ECO)"
        else:
            chip_version = extracted_data.get("Chip Version", "").strip()
            non_bank = extracted_data.get("Non Bank", "").strip()

            if chip_version == "A0":
                # Ignore Noc Passthrough, check Non Bank
                if non_bank == "N/A":
                    final_bin = "Failed(ECO)"
                else:
                    final_bin = "HB1(ECO)"
            else:
                if non_bank == "N/A":
                    final_bin = "Failed(ECO)"
                else:
                    final_bin = "HB1(ECO)"

    elif power_mode == "SPORT":
        if total_banks_failed <= 5:
            final_bin = "Failed(SPORT)"
        elif extracted_data.get("Adjacent") == "YES":
            final_bin = "Failed(SPORT)"
        else:
            chip_version = extracted_data.get("Chip Version", "").strip()
            non_bank = extracted_data.get("Non Bank", "").strip()

            if chip_version == "A0":
                # Ignore Noc Passthrough, check Non Bank
                if non_bank == "N/A":
                    final_bin = "Failed(SPORT)"
                else:
                    final_bin = "HB1(SPORT)"
            else:
                if non_bank == "N/A":
                    final_bin = "Failed(SPORT)"
                else:
                    final_bin = "HB1(SPORT)"
    extracted_data["Final Bin"] = final_bin

    extracted_data_list = [extracted_data]

    return pd.DataFrame(extracted_data_list)

    



def parse_log_file2(log_file_path: str) ->  pd.DataFrame:
    """
    Parse a log file for format2 and extract structured data.
    Returns a dictionary with extracted metrics instead of directly writing to Excel.
    """

    # Read the log file
    with open(log_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Extract Information
    extracted_data = {
        "File Name": os.path.basename(log_file_path),
        "Marking ID": "N/A",
        "Failures by Test": {},
        "Power Mode": "ECO" if "ECO" in log_file_path else "SPORT",
    }

    if lines:
        extracted_data["Marking ID"] = lines[0].strip().split(":")[1].strip() if lines[0].startswith("Marking ID:") else "N/A"

    for line in lines:
        line = line.strip()

        # Extract Failures by Test
        if "Failures by Test:" in line:
            extracted_data["Failures by Test"] = eval(line.split("Failures by Test:")[1].strip())

    # SLT Test to Category Mapping
    test_category_mapping = {
        "ATE_CMD_DDR_APB_ACCESS": "LPDDR Test",
        "ATE_CMD_DDR_MCU_MEM": "LPDDR Test",
        "ATE_CMD_DDR_ACK_HO": "LPDDR Test",
        "ATE_CMD_DDR_ACK_FS": "LPDDR Test",
        "ATE_CMD_DDR_PHYINIT_TRAIN_NORTH": "LPDDR Test",
        "ATE_CMD_DDR_PHYINIT_ALL_NORTH_WR_RD": "LPDDR Test",
        "ATE_CMD_DDR_MEM_SWP_WRRD_N": "LPDDR Test",
        "ATE_CMD_DDR_MEM_SWP_RDLOOP_N": "LPDDR Test",
        "ATE_CMD_DDR_PHYINIT_TRAIN_EAST": "LPDDR Test",
        "ATE_CMD_DDR_PHYINIT_ALL_EAST_WR_RD": "LPDDR Test",
        "ATE_CMD_DDR_MEM_SWP_WRRD_E": "LPDDR Test",
        "ATE_CMD_DDR_MEM_SWP_RDLOOP_E": "LPDDR Test",
        "ATE_CMD_DDR_PHYINIT_FULL": "LPDDR Test",
        "ATE_CMD_BANK_PE_ALL_REG_ACCESS": "Failed Banks",
        "ATE_CMD_BANK_PE_MACC": "Failed Banks",
        "ATE_CMD_BANK_PE_MULT5X5": "Failed Banks",
        "ATE_CMD_BANK_PE_ACC": "Failed Banks",
        "ATE_CMD_BANK_PE_ROTATE": "Failed Banks",
        "ATE_CMD_BANK_PE_NORM_PRIORITY": "Failed Banks",
        "ATE_CMD_BANK_PE_GEMV_FP8": "Failed Banks",
        "ATE_CMD_BANK_PE_GEMV_FP8_SFP16": "Failed Banks",
        "ATE_CMD_BANK_PE_GEMV_SFP16": "Failed Banks",
        "ATE_CMD_BANK_PE_GEMV_INT4": "Failed Banks",
        "ATE_CMD_BANK_PE_GEMV_INT8": "Failed Banks",
        "ATE_CMD_BANK_PE_ROW_REDUCE": "Failed Banks",
        "ATE_CMD_BANK_PE_NORM_REDUCE_ADDER": "Failed Banks",
        "ATE_CMD_BANK_PE_NORM_BYTEADDER_SHIFT_PRIO": "Failed Banks",
        "ATE_CMD_BANK_PE_GEMV_BROADCAST": "Failed Banks",
        "ATE_CMD_BANK_PE_GEMV_SPARSITY": "Failed Banks",
        "ATE_CMD_BANK_PE_NORM_DATA_MUX": "Failed Banks",
        "ATE_CMD_BANK_GEMV_HALF_ZERO": "Failed Banks",
        "ATE_CMD_BANK_PE_NORM": "Failed Banks",
        "ATE_CMD_BANK_PE_ZERO_DETECT": "Failed Banks",
        "ATE_CMD_BANK_NOC_PASSTHROUGH_N": "Noc PassThrough",
        "ATE_CMD_BANK_NOC_PASSTHROUGH_S": "Noc PassThrough",
        "ATE_CMD_BANK_NOC_PASSTHROUGH_E": "Noc PassThrough",
        "ATE_CMD_BANK_NOC_PASSTHROUGH_W": "Noc PassThrough",
        "ATE_CMD_BANK_NOC_ROUTE_N": "Noc Route",
        "ATE_CMD_BANK_NOC_ROUTE_S": "Noc Route",
        "ATE_CMD_BANK_NOC_ROUTE_E": "Noc Route",
        "ATE_CMD_BANK_NOC_ROUTE_W": "Noc Route",
        "ATE_CMD_BANK_NOC_BUFFER": "Failed Banks",
        "ATE_CMD_BANK_CRAM_BIST_10N": "Bank Cram Test",
        "ATE_CMD_BANK_CRAM_BIST_FULL": "Bank Cram Test",
        "ATE_CMD_BANK_CRAM_BIST_B2B": "Bank Cram Test",
        "ATE_CMD_BANK_CRAM_BIST_BURST": "Bank Cram Test",
        "ATE_CMD_CMCM_ALL_FUNCTIONAL": "CMCM Functional Tests",
        "ATE_CMD_UCM_ALL": "UCM_ALL",
        "ATE_CMD_PCM_SKT_SCAN_E": "PCM Fails",
        "ATE_CMD_PCM_SKT_SCAN_W": "PCM Fails",
        "ATE_CMD_PCM_SKT_SCAN_S": "PCM Fails",
        "ATE_CMD_PCM_SKT_SCAN_N": "PCM Fails",
        "ATE_CMD_PCM_BANK_IDC_PING_S": "Failed Banks",
        "ATE_CMD_PCM_IDC_READ_WRITE_S": "PCM Fails",
        "ATE_CMD_BANK_GEMV_QUARTER_POWER": "Power",
        "ATE_CMD_BANK_GEMV_POWER_STATUS_CHECK": "Power"
    }

    # Initialize extracted values
    extracted_data["Tests"] = []
    
    for test_name, bank_id in extracted_data["Failures by Test"].items():
        result = "FAIL" if bank_id else "PASS"
        category = test_category_mapping.get(test_name.strip(), "Unknown Category")

        extracted_data["Tests"].append({
            "SLT Test": test_name,
            "Bank Ids": str(bank_id),
            "Result": result,
            "Test Categories": category,
            "Power Mode": extracted_data["Power Mode"],
            "Result Type": "Pass_0B" if result == "PASS" else "Fail_1B"
        })
    df=pd.DataFrame(extracted_data["Tests"])
    return df

def parse_log_file3(log_file_path: str) ->  pd.DataFrame:
    """
    Parse a log file and extract structured data
    Returns dictionary with 40+ extracted metrics
    """
    columns = [
    "File Name", "Timestamp", "Chip Number", "Marking Id", "Chip Version",
    "SLT Test Version", "Current Frequency", "Current Power Mode",
    "VDDP", "VDDM", "VDDCORE", "VDDHF", "VDDIO", "VDDWL", 
    "Banks Failed", "Columns with Failures",
    "Banks Repairable after CRAM test", "Banks Failed after CRAM Test", "Repair Data Applied", "Remark", "Total Banks Failed"
]

    test_columns = [
    "ATE_CMD_BANK_PE_ALL_REG_ACCESS", "ATE_CMD_BANK_PE_MACC", "ATE_CMD_BANK_PE_MULT5X5", 
    "ATE_CMD_BANK_PE_ACC", "ATE_CMD_BANK_PE_ROTATE", "ATE_CMD_BANK_PE_NORM_PRIORITY", 
    "ATE_CMD_BANK_PE_GEMV_FP8", "ATE_CMD_BANK_PE_GEMV_FP8_SFP16", "ATE_CMD_BANK_PE_GEMV_SFP16", 
    "ATE_CMD_BANK_PE_GEMV_INT4", "ATE_CMD_BANK_PE_GEMV_INT8", "ATE_CMD_BANK_PE_ROW_REDUCE", 
    "ATE_CMD_BANK_PE_NORM_REDUCE_ADDER", "ATE_CMD_BANK_PE_NORM_BYTEADDER_SHIFT_PRIO", 
    "ATE_CMD_BANK_PE_GEMV_BROADCAST", "ATE_CMD_BANK_PE_GEMV_SPARSITY", "ATE_CMD_BANK_PE_NORM_DATA_MUX", 
    "ATE_CMD_BANK_GEMV_HALF_ZERO", "ATE_CMD_BANK_PE_NORM", "ATE_CMD_BANK_NOC_PERECV_STORE_FRWD_NS", 
    "ATE_CMD_BANK_NOC_PERECV_STORE_FRWD_SN", "ATE_CMD_BANK_NOC_PASSTHROUGH_N", 
    "ATE_CMD_BANK_NOC_PASSTHROUGH_S", "ATE_CMD_BANK_NOC_PASSTHROUGH_W", "ATE_CMD_BANK_NOC_ROUTE_N", 
    "ATE_CMD_BANK_NOC_ROUTE_S", "ATE_CMD_BANK_NOC_ROUTE_W", "ATE_CMD_BANK_NOC_BUFFER", 
    "ATE_CMD_BANK_CRAM_BIST_10N", "ATE_CMD_BANK_CRAM_BIST_FULL", "ATE_CMD_BANK_CRAM_BIST_B2B", 
    "ATE_CMD_BANK_CRAM_BIST_BURST", "ATE_CMD_CMCM_ALL_FUNCTIONAL", "ATE_CMD_UCM_ALL", 
    "ATE_CMD_PCM_BANK_IDC_PING_S", "ATE_CMD_DDR_APB_ACCESS", "ATE_CMD_DDR_MCU_MEM", 
    "ATE_CMD_DDR_ACK_HO", "ATE_CMD_DDR_ACK_FS", "ATE_CMD_DDR_PHYINIT_TRAIN_NORTH", 
    "ATE_CMD_DDR_PHYINIT_ALL_NORTH_WR_RD", "ATE_CMD_DDR_MEM_SWP_WRRD_N", "ATE_CMD_DDR_MEM_SWP_RDLOOP_N", 
    "ATE_CMD_DDR_PHYINIT_TRAIN_EAST", "ATE_CMD_DDR_PHYINIT_ALL_EAST_WR_RD", "ATE_CMD_DDR_MEM_SWP_WRRD_E", 
    "ATE_CMD_DDR_MEM_SWP_RDLOOP_E", "ATE_CMD_DDR_PHYINIT_FULL"
]

    test_summary = [
    "ATE_CMD_BANK_PE_ALL_REG_ACCESS_grade", "ATE_CMD_BANK_PE_MACC_grade", "ATE_CMD_BANK_PE_MULT5X5_grade",
    "ATE_CMD_BANK_PE_ACC_grade", "ATE_CMD_BANK_PE_ROTATE_grade", "ATE_CMD_BANK_PE_NORM_PRIORITY_grade",
    "ATE_CMD_BANK_PE_GEMV_FP8_grade", "ATE_CMD_BANK_PE_GEMV_FP8_SFP16_grade", "ATE_CMD_BANK_PE_GEMV_SFP16_grade",
    "ATE_CMD_BANK_PE_GEMV_INT4_grade", "ATE_CMD_BANK_PE_GEMV_INT8_grade", "ATE_CMD_BANK_PE_ROW_REDUCE_grade",
    "ATE_CMD_BANK_PE_NORM_REDUCE_ADDER_grade", "ATE_CMD_BANK_PE_NORM_BYTEADDER_SHIFT_PRIO_grade",
    "ATE_CMD_BANK_PE_GEMV_BROADCAST_grade", "ATE_CMD_BANK_PE_GEMV_SPARSITY_grade", "ATE_CMD_BANK_PE_NORM_DATA_MUX_grade",
    "ATE_CMD_BANK_GEMV_HALF_ZERO_grade", "ATE_CMD_BANK_PE_NORM_grade", "ATE_CMD_BANK_NOC_PERECV_STORE_FRWD_NS_grade",
    "ATE_CMD_BANK_NOC_PERECV_STORE_FRWD_SN_grade", "ATE_CMD_BANK_NOC_PASSTHROUGH_N_grade",
    "ATE_CMD_BANK_NOC_PASSTHROUGH_S_grade", "ATE_CMD_BANK_NOC_PASSTHROUGH_W_grade", "ATE_CMD_BANK_NOC_ROUTE_N_grade",
    "ATE_CMD_BANK_NOC_ROUTE_S_grade", "ATE_CMD_BANK_NOC_ROUTE_W_grade", "ATE_CMD_BANK_NOC_BUFFER_grade",
    "ATE_CMD_BANK_CRAM_BIST_10N_grade", "ATE_CMD_BANK_CRAM_BIST_FULL_grade", "ATE_CMD_BANK_CRAM_BIST_B2B_grade",
    "ATE_CMD_BANK_CRAM_BIST_BURST_grade", "ATE_CMD_CMCM_ALL_FUNCTIONAL_grade", "ATE_CMD_UCM_ALL_grade",
    "ATE_CMD_PCM_BANK_IDC_PING_S_grade", "ATE_CMD_DDR_APB_ACCESS_grade", "ATE_CMD_DDR_MCU_MEM_grade",
    "ATE_CMD_DDR_ACK_HO_grade", "ATE_CMD_DDR_ACK_FS_grade", "ATE_CMD_DDR_PHYINIT_TRAIN_NORTH_grade",
    "ATE_CMD_DDR_PHYINIT_ALL_NORTH_WR_RD_grade", "ATE_CMD_DDR_MEM_SWP_WRRD_N_grade", "ATE_CMD_DDR_MEM_SWP_RDLOOP_N_grade",
    "ATE_CMD_DDR_PHYINIT_TRAIN_EAST_grade", "ATE_CMD_DDR_PHYINIT_ALL_EAST_WR_RD_grade", "ATE_CMD_DDR_MEM_SWP_WRRD_E_grade",
    "ATE_CMD_DDR_MEM_SWP_RDLOOP_E_grade", "ATE_CMD_DDR_PHYINIT_FULL_grade"
]

    patterns = {
    "Timestamp": r"curr_time=(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})",
    "Chip Number": r"chip_id=([\w\d\.]+)",
    "Marking Id": r"Marking ID: ([\w\d\-\_]+)",
    "Chip Version": r"Chip version: ([\w\d]+)",
    "SLT Test Version": r"Diagnostic fw version: (v[\d\.]+)",
    "Current Frequency": r"ctUtilsPower : INFO : Current Frequency: (\d+)",
    "Current Power Mode": r"ctUtilsPower : INFO : Current Power Mode: (\w+)",
    "VDDP": r"VDDP: (\d+)",
    "VDDM": r"VDDM: (\d+)",
    "VDDCORE": r"VDDCORE: (\d+)",
    "VDDHF": r"VDDHF: (\d+)",
    "VDDIO": r"VDDIO: (\d+)",
    "VDDWL": r"VDDWL: (\d+)",
    "Banks Failed": r"Banks Failed: \{([\d, ]+)\}"
}

    patterns1 = {
    "Columns with Failures": r"Columns with failures: \{([\d, ]+)\}",
    "Banks Repairable after CRAM test": r"Banks Repairable after CRAM test: \{([\d, ]+)\}",
    "Banks Failed after CRAM Test": r"Banks Failed after CRAM [Tt]est:\s*\{([\d, ]+)\}",
    "Repair Data Applied": r"Repair Data Applied: \{(.*?)\}",
    "Total Banks Failed": r"Total Numbers of Banks Failed: (\d+)",
    "Bank Co-ordinates with Failures": r"Bank Coordinates with failures:\s*(\[\[.*?\]\])"
}
    file_name = os.path.basename(log_file_path)

    extracted_data = {col: "N/A" for col in columns + test_columns + test_summary}
    
    extracted_data["File Name"] = file_name  # Store file name
# Function to extract data from a single log file
    
    with open(log_file_path, "r") as log_file:
        log_content = log_file.read()
        for key, pattern in patterns.items():
            match = re.search(pattern, log_content)
            if match:
                extracted_data[key] = match.group(1)

        for key, pattern in patterns1.items():
            match = re.search(pattern, log_content)
            if match:
                extracted_data[key] = match.group(1)

        for summary in test_summary:
            pattern2 = rf"Test Name: {summary.replace('_grade', '')} : (PASS|FAIL)"
            match = re.search(pattern2, log_content)
            if match:
                extracted_data[summary] = match.group(1)

    # Extract test_columns data
        for test_col in test_columns:
            pattern = rf"{test_col}': (set\(\)|\[.*?\]|\{{.*?\}}|\d+)"
            match = re.search(pattern, log_content)
            if match:
                extracted_data[test_col] = match.group(1)
    
    def count_failures(test_group, extracted_data):
        fail_count = 0
        for test in test_group:
            if extracted_data.get(f"{test}_grade") == "FAIL":
                fail_count += 1
        return f"{fail_count}f" if fail_count > 0 else "P"
    

    extracted_data["Failed Banks"] = count_failures([
    "ATE_CMD_BANK_PE_ALL_REG_ACCESS", "ATE_CMD_BANK_PE_MACC", "ATE_CMD_BANK_PE_MULT5X5", 
    "ATE_CMD_BANK_PE_ACC", "ATE_CMD_BANK_PE_ROTATE", "ATE_CMD_BANK_PE_NORM_PRIORITY", 
    "ATE_CMD_BANK_PE_GEMV_FP8", "ATE_CMD_BANK_PE_GEMV_FP8_SFP16", "ATE_CMD_BANK_PE_GEMV_SFP16", 
    "ATE_CMD_BANK_PE_GEMV_INT4", "ATE_CMD_BANK_PE_GEMV_INT8", "ATE_CMD_BANK_PE_ROW_REDUCE", 
    "ATE_CMD_BANK_PE_NORM_REDUCE_ADDER", "ATE_CMD_BANK_PE_NORM_BYTEADDER_SHIFT_PRIO", 
    "ATE_CMD_BANK_PE_GEMV_BROADCAST", "ATE_CMD_BANK_PE_GEMV_SPARSITY", "ATE_CMD_BANK_PE_NORM_DATA_MUX", 
    "ATE_CMD_BANK_GEMV_HALF_ZERO", "ATE_CMD_BANK_PE_NORM", "ATE_CMD_BANK_PE_ZERO_DETECT", "ATE_CMD_BANK_NOC_BUFFER"
], extracted_data)

    extracted_data["Noc PassThrough"] = count_failures([
    "ATE_CMD_BANK_NOC_PASSTHROUGH_N", "ATE_CMD_BANK_NOC_PASSTHROUGH_S", 
    "ATE_CMD_BANK_NOC_PASSTHROUGH_E", "ATE_CMD_BANK_NOC_PASSTHROUGH_W"
], extracted_data)
    
    extracted_data["Noc Route"] = count_failures([
    "ATE_CMD_BANK_NOC_ROUTE_N", "ATE_CMD_BANK_NOC_ROUTE_S", 
    "ATE_CMD_BANK_NOC_ROUTE_E", "ATE_CMD_BANK_NOC_ROUTE_W"
], extracted_data)

    extracted_data["Bank Cram Test"] = count_failures([
    "ATE_CMD_BANK_CRAM_BIST_10N", "ATE_CMD_BANK_CRAM_BIST_FULL", 
    "ATE_CMD_BANK_CRAM_BIST_B2B", "ATE_CMD_BANK_CRAM_BIST_BURST"
], extracted_data)

    extracted_data["CMCM Functional Tests"] = count_failures([
    "ATE_CMD_CMCM_ALL_FUNCTIONAL"
], extracted_data)

    extracted_data["UCM_ALL"] = count_failures([
    "ATE_CMD_UCM_ALL"
], extracted_data)

    extracted_data["LPDDR Test"] = count_failures([
    "ATE_CMD_DDR_APB_ACCESS", "ATE_CMD_DDR_MCU_MEM", "ATE_CMD_DDR_ACK_HO", 
    "ATE_CMD_DDR_ACK_FS", "ATE_CMD_DDR_PHYINIT_TRAIN_NORTH", 
    "ATE_CMD_DDR_PHYINIT_ALL_NORTH_WR_RD", "ATE_CMD_DDR_MEM_SWP_WRRD_N", 
    "ATE_CMD_DDR_MEM_SWP_RDLOOP_N", "ATE_CMD_DDR_PHYINIT_TRAIN_EAST", 
    "ATE_CMD_DDR_PHYINIT_ALL_EAST_WR_RD", "ATE_CMD_DDR_MEM_SWP_WRRD_E", 
    "ATE_CMD_DDR_MEM_SWP_RDLOOP_E", "ATE_CMD_DDR_PHYINIT_FULL"
], extracted_data)

    def get_failure_count(value):
        if value == "P":
            return 0
        elif value.endswith('f'):
            try:
                return int(value[:-1])  # Extract numeric part before 'f'
            except:
                return 0
        return 0
    fb_count = get_failure_count(extracted_data.get("Failed Banks", ""))
    bct_count = get_failure_count(extracted_data.get("Bank Cram Test", ""))
    ucm_count = get_failure_count(extracted_data.get("UCM_ALL", ""))
    lpddr_count = get_failure_count(extracted_data.get("LPDDR Test", ""))
    cmcm_count = get_failure_count(extracted_data.get("CMCM Functional Tests", ""))
    noc_route_count = get_failure_count(extracted_data.get("Noc Route", ""))
    noc_passthrough_count = get_failure_count(extracted_data.get("Noc Passthrough", ""))

    bank_failures=[]
    Remarks = []
    Non_Bank = []

    if fb_count >= 1:
        Remarks.append("Failed Banks")
        bank_failures.append("Failed Banks")
    if bct_count >= 1:
        Remarks.append("Bank Cram Test")
        bank_failures.append("Bank Cram Test")
    if ucm_count >= 1:
        Remarks.append("UCM")
        Non_Bank.append("UCM")
    if lpddr_count >= 1:
        Remarks.append("LPDDR")
        Non_Bank.append("LPDDR")
    if cmcm_count >= 1:
        Remarks.append("CMCM")
        Non_Bank.append("CMCM")
    if noc_route_count >= 1:
        Remarks.append("Noc Route")
        Non_Bank.append("Noc Route")
    if noc_passthrough_count >= 1:
        Remarks.append("Noc Passthrough")
        Non_Bank.append("Noc Passthrough")

    if bank_failures:
        extracted_data["Bank Related Fails"] = f"Bank-rel({', '.join(bank_failures)})"
    else:
        extracted_data["Bank Related Fails"] = "N/A"

    if Non_Bank:
        extracted_data["Non-Bank Related Fails"] = f"Non-Bank-rel({', '.join(Non_Bank)})"
    else:
        extracted_data["Non-Bank Related Fails"] = "N/A"

    if Remarks:
        extracted_data["Remarks"] = f"Bank-rel({', '.join(Remarks)})"
    else:
        extracted_data["Remarks"] = "N/A"

    def format_adjacent_failures(numbers):
        numbers = sorted(set(map(int, numbers.split(", "))))  # Convert to sorted list of integers
        if not numbers:
            return "No Adjacent Failures"
        ranges = []
        start = numbers[0]
        prev = numbers[0]
        for num in numbers[1:]:
            if num == prev + 1:
                prev = num  # Continue range
            else:
                ranges.append(f"{start}-{prev}" if start != prev else str(start))
                start = prev = num  # Start new range
        ranges.append(f"{start}-{prev}" if start != prev else str(start))
        return ", ".join(ranges)

    if extracted_data["Columns with Failures"] != "N/A":
        extracted_data["Adjacent Columns Failures"] = format_adjacent_failures(extracted_data["Columns with Failures"])

    def format_multiple_values(value, limit=5):
        if value == "N/A":
            return value
        if isinstance(value, str):
            if value.startswith("{") or value.startswith("["):
                values = re.findall(r"\d+", value)
                if len(values) > limit:
                    return ", ".join(values[:limit]) + ", +more..."
                else:
                    return ", ".join(values)
            return value
    for key in ["Banks Failed", "Columns with Failures", "Banks Repairable after CRAM test", "Banks Failed after CRAM Test"]:
        extracted_data[key] = format_multiple_values(extracted_data[key])

    if extracted_data["Repair Data Applied"] != "N/A":
        repair_data_list = re.findall(r"(\d+: \[\d+, \d+\])", extracted_data["Repair Data Applied"])
        if len(repair_data_list) > 5:
            extracted_data["Repair Data Applied"] = ", ".join(repair_data_list[:5]) + ", +more..."
        else:
            extracted_data["Repair Data Applied"] = ", ".join(repair_data_list)

    if extracted_data["Adjacent Columns Failures"] != "N/A":
        extracted_data["Adjacent"] = "YES"
    else:
        extracted_data["Adjacent"] = "NO"

    if "More than 2 bad columns. Bad CHIP" in log_content:
        extracted_data["Remark"] = "More than 2 bad columns. Bad CHIP"
    elif "passing" in log_content:
        extracted_data["Remark"] = "passing"
    elif "BAD CHIP. Below Test failed" in log_content:
        extracted_data["Remark"] = "BAD CHIP. Below Test failed"
    else:
        extracted_data["Remark"] = "No match found"

# Convert "Total Banks Failed" safely to integer
    total_banks_failed = int(extracted_data.get("Total Banks Failed", "0"))  # Default "0" to avoid errors

    power_mode = extracted_data.get("Current Power Mode", "").strip().upper()

# Initialize Final Bin
    final_bin = "N/A"

    if power_mode == "ECO":
        if total_banks_failed <= 2:
            final_bin = "Failed(ECO)"
        elif extracted_data.get("Adjacent") == "YES":
            final_bin = "Failed(ECO)"
        else:
            chip_version = extracted_data.get("Chip Version", "").strip()
            non_bank = extracted_data.get("Non Bank", "").strip()

            if chip_version == "A0":
                # Ignore Noc Passthrough, check Non Bank
                if non_bank == "N/A":
                    final_bin = "Failed(ECO)"
                else:
                    final_bin = "HB1(ECO)"
            else:
                if non_bank == "N/A":
                    final_bin = "Failed(ECO)"
                else:
                    final_bin = "HB1(ECO)"

    elif power_mode == "SPORT":
        if total_banks_failed <= 5:
            final_bin = "Failed(SPORT)"
        elif extracted_data.get("Adjacent") == "YES":
            final_bin = "Failed(SPORT)"
        else:
            chip_version = extracted_data.get("Chip Version", "").strip()
            non_bank = extracted_data.get("Non Bank", "").strip()

            if chip_version == "A0":
                # Ignore Noc Passthrough, check Non Bank
                if non_bank == "N/A":
                    final_bin = "Failed(SPORT)"
                else:
                    final_bin = "HB1(SPORT)"
            else:
                if non_bank == "N/A":
                    final_bin = "Failed(SPORT)"
                else:
                    final_bin = "HB1(SPORT)"
    extracted_data["Final Bin"] = final_bin
    extracted_data["Mark Power"] = extracted_data["Current Power Mode"] + extracted_data["Marking Id"]
    
    delete_columns = test_columns + test_summary
    for i in set(delete_columns):
        extracted_data.pop(i, None)  # Safe deletion

    extracted_data_list = [extracted_data]
 
    return pd.DataFrame(extracted_data_list)

