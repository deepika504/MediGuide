"""
fix_brands.py  — Run this ONCE to update brand_info in the existing database.
Does NOT delete or recreate any records. Only updates the brand_info column
to include common Indian brand names so image scanning can match them.

Run from the MediGuide folder:
    python fix_brands.py
"""

import sqlite3
import os

DATABASE = os.path.join("database", "mediguide.db")


def update_brands():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    updates = [
        # (medicine name in DB,  new brand_info with added brands)
        (
            "Paracetamol",
            "Examples: Crocin, Calpol, Paracip, Dolo, Dolo-650, Pyrigesic, "
            "Metacin, Feverex, Febrex, Meftal (paracetamol component)."
        ),
        (
            "Ibuprofen",
            "Examples: Brufen, Ibugesic, Advil, Combiflam, Ibugesic Plus, Febrinil."
        ),
        (
            "Cough Syrup",
            "Example: Benadryl."
        ),
        (
            "Cetirizine",
            "Examples: Cetcip, Zyrtec, Alerid, Okacet, CTZ, Cetzine."
        ),
        (
            "Levocetirizine",
            "Examples: Levocet, Xyzal, Levorid, Teczine, Vozet."
        ),
        (
            "Amoxicillin",
            "Examples: Amoxil, Mox, Novamox, Wymox, Amoxyclav (with clavulanate)."
        ),
        (
            "Azithromycin",
            "Examples: Azithral, Azee, Zithromax, Azifast, Aziwok, Azicip."
        ),
        (
            "Pantoprazole",
            "Examples: Pantocid, Pan, Pantop, Pantodac, Nexpro, Controloc."
        ),
        (
            "Omeprazole",
            "Examples: Omez, Prilosec, Ocid, Omecip, Romesec."
        ),
        (
            "Famotidine",
            "Examples: Pepcid, Famtac, Topcid, Famotin."
        ),
        (
            "Ondansetron",
            "Examples: Ondem, Zofran, Emeset, Vomitab, Ondanset."
        ),
        (
            "Domperidone",
            "Examples: Domstal, Motilium, Vomistop, Domperi."
        ),
        (
            "Loperamide",
            "Examples: Imodium, Eldoper, Lomofen, Roko."
        ),
        (
            "Salbutamol",
            "Examples: Asthalin, Ventolin, Derihaler, Salbair, Salmol."
        ),
        (
            "Montelukast",
            "Examples: Montair, Singulair, Montemac, Romilast."
        ),
        (
            "Clotrimazole",
            "Examples: Candid, Canesten, Clop, Fungitek."
        ),
        (
            "Mupirocin",
            "Examples: T-Bact, Bactroban, Mupired."
        ),
        (
            "Diclofenac Gel",
            "Examples: Voveran, Voltaren, Diclomol, Reactin."
        ),
        (
            "Cetirizine",
            "Examples: Cetcip, Zyrtec, Alerid, Okacet, CTZ."
        ),
        (
            "Becosules",
            "Examples: Becosules, Becadex, Supradyn B."
        ),
        (
            "Vitamin B12",
            "Examples: Mecobalamin, Mecobion, Nervijen, Methylcobal."
        ),
        (
            "Oral Rehydration Salts",
            "Examples: Electral, Enerzal, Pedialyte, ORS sachets."
        ),
        (
            "Eno",
            "Examples: Eno fruit salt, various flavours."
        ),
    ]

    updated = 0
    skipped = 0

    for name, brand_info in updates:
        cursor.execute(
            "UPDATE medicines SET brand_info = ? WHERE name = ?",
            (brand_info, name)
        )
        if cursor.rowcount > 0:
            print(f"  ✓ Updated: {name}")
            updated += 1
        else:
            print(f"  – Not found in DB (skipped): {name}")
            skipped += 1

    conn.commit()
    conn.close()

    print(f"\nDone. {updated} record(s) updated, {skipped} skipped.")
    print("Your existing medicine records were NOT deleted.")


if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        print(f"ERROR: Database not found at '{DATABASE}'.")
        print("Make sure you run this script from inside the MediGuide folder.")
    else:
        print("Updating brand names in the database...\n")
        update_brands()
