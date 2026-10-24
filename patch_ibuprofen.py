"""
patch_ibuprofen.py — Run once to fix the Ibuprofen brand_info entry.
The previous fix_brands.py mistakenly included the word "paracetamol"
inside Ibuprofen's brand_info, which caused it to appear in Paracetamol
search results.

Run from the MediGuide folder:
    python patch_ibuprofen.py
"""

import sqlite3
import os

DATABASE = os.path.join("database", "mediguide.db")


def patch():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Remove "with paracetamol" so Ibuprofen no longer matches Paracetamol searches
    cursor.execute(
        "UPDATE medicines SET brand_info = ? WHERE name = ?",
        (
            "Examples: Brufen, Ibugesic, Advil, Combiflam, Ibugesic Plus, Febrinil.",
            "Ibuprofen"
        )
    )

    if cursor.rowcount > 0:
        print("Fixed: Ibuprofen brand_info updated.")
    else:
        print("Ibuprofen record not found — nothing changed.")

    conn.commit()
    conn.close()
    print("Done. No records were deleted.")


if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        print(f"ERROR: Database not found at '{DATABASE}'.")
        print("Run this script from inside the MediGuide folder.")
    else:
        patch()
