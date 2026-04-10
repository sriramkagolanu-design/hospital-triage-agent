# -----------------------------
# LOGGER MODULE
# -----------------------------

import datetime
import json


def log(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def log_input(input_data):
    log(f"Received input:\n{json.dumps(input_data, indent=2)}")


def log_output(output_data):
    log(f"Generated output:\n{json.dumps(output_data, indent=2)}")


def log_error(error_message):
    log(f"Error: {error_message}", level="ERROR")