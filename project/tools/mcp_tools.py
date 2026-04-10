# -----------------------------
# MCP TOOLS (DB CONNECTED)
# -----------------------------

import sqlite3

DB_PATH = "utils/hospital.db"


def get_available_beds(bed_type: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT bed_id FROM beds WHERE type=? AND available=1",
            (bed_type,)
        )

        beds = [row[0] for row in cursor.fetchall()]
        conn.close()

        return beds if beds else ["No beds available"]

    except Exception as e:
        return [f"Error: {str(e)}"]


def get_available_doctors(speciality: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM doctors WHERE speciality=? AND available=1",
            (speciality,)
        )

        doctors = [row[0] for row in cursor.fetchall()]
        conn.close()

        return doctors if doctors else ["No doctors available"]

    except Exception as e:
        return [f"Error: {str(e)}"]