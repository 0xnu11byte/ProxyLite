# proxylite/plugins/check_cors.py

name = "CORS Misconfiguration Scanner"
description = "Checks for permissive CORS headers in responses."
author = "0xYourHandle"

def run(request, response):
    if response:
        acao = response.headers.get("Access-Control-Allow-Origin")
        if acao == "*" or acao == request.headers.get("Origin"):
            print("[CORS Scanner] Potentially permissive CORS detected.")
