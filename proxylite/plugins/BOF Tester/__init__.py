# BOF Tester/__init__.py

name = "Buffer Overflow Tester"
description = "Fuzzes parameters with increasing payloads to detect potential buffer overflows."
author = "0xYourHandle"

from urllib.parse import urlparse, parse_qs, urlencode
import copy
import time

def run(request, response):
    try:
        url = request.url
        method = request.method
        headers = dict(request.headers)
        body = request.get_text()

        # Parse URL parameters
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)

        if not query_params and not body:
            print("[BOF Tester] No parameters found in request to test.")
            return

        fuzz_lengths = [100, 500, 1000, 2000, 4000]

        if query_params:
            print(f"[BOF Tester] Testing URL parameters: {list(query_params.keys())}")
            for param in query_params.keys():
                for length in fuzz_lengths:
                    fuzz_payload = "A" * length
                    fuzz_params = copy.deepcopy(query_params)
                    fuzz_params[param] = fuzz_payload
                    fuzz_query = urlencode(fuzz_params, doseq=True)
                    fuzz_url = parsed._replace(query=fuzz_query).geturl()

                    crafted_request = request.copy()
                    crafted_request.url = fuzz_url

                    # Send crafted request
                    crafted_response = request.send(crafted_request)

                    # Check for anomalies
                    if crafted_response.status_code >= 500:
                        print(f"[BOF Tester] Possible crash detected on param '{param}' with length {length}, status {crafted_response.status_code}")
                    if len(crafted_response.content) == 0:
                        print(f"[BOF Tester] Empty response, potential service crash on param '{param}' with length {length}")

                    time.sleep(0.3)  # to avoid overwhelming target

        if body and "application/x-www-form-urlencoded" in headers.get("Content-Type", ""):
            post_params = parse_qs(body)
            print(f"[BOF Tester] Testing POST parameters: {list(post_params.keys())}")
            for param in post_params.keys():
                for length in fuzz_lengths:
                    fuzz_payload = "A" * length
                    fuzz_params = copy.deepcopy(post_params)
                    fuzz_params[param] = fuzz_payload
                    fuzz_body = urlencode(fuzz_params, doseq=True)

                    crafted_request = request.copy()
                    crafted_request.set_text(fuzz_body)

                    crafted_response = request.send(crafted_request)

                    if crafted_response.status_code >= 500:
                        print(f"[BOF Tester] Possible crash detected on POST param '{param}' with length {length}, status {crafted_response.status_code}")
                    if len(crafted_response.content) == 0:
                        print(f"[BOF Tester] Empty response, potential service crash on POST param '{param}' with length {length}")

                    time.sleep(0.3)

    except Exception as e:
        print(f"[BOF Tester] Error during fuzzing: {e}")
