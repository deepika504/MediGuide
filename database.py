import sqlite3
import os

DATABASE = os.path.join("database", "mediguide.db")


def create_database():
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            generic_name TEXT,
            active_ingredient TEXT,
            category TEXT,
            uses TEXT,
            how_it_works TEXT,
            side_effects TEXT,
            warnings TEXT,
            brand_info TEXT
        )
    """)

    medicines = [
        ("Paracetamol", "Paracetamol", "Paracetamol", "Pain relief",
         "Temporary relief of pain and fever.",
         "Helps reduce pain and elevated body temperature.",
         "Nausea, rash, stomach discomfort.",
         "Excessive use can cause serious liver damage.",
         "Examples: Crocin, Calpol."),

        ("Ibuprofen", "Ibuprofen", "Ibuprofen", "Pain relief",
         "Temporary relief of pain, inflammation and fever.",
         "Reduces substances involved in pain and inflammation.",
         "Stomach discomfort, nausea.",
         "May cause stomach bleeding or kidney problems.",
         "Examples: Brufen, Ibugesic."),

        ("Cetirizine", "Cetirizine", "Cetirizine hydrochloride", "Antihistamine",
         "Relief of allergy symptoms.",
         "Blocks histamine involved in allergic reactions.",
         "Drowsiness, dry mouth.",
         "May cause drowsiness.",
         "Examples: Cetcip, Zyrtec."),

        ("Levocetirizine", "Levocetirizine", "Levocetirizine", "Antihistamine",
         "Relief of allergy symptoms.",
         "Blocks histamine activity.",
         "Drowsiness, tiredness.",
         "Use according to product instructions.",
         "Examples: Levocet, Xyzal."),

        ("Amoxicillin", "Amoxicillin", "Amoxicillin", "Antibiotic",
         "Treatment of certain bacterial infections.",
         "Interferes with bacterial cell-wall formation.",
         "Nausea, diarrhea, rash.",
         "Use only when prescribed; allergies can be serious.",
         "Example: Amoxil."),

        ("Azithromycin", "Azithromycin", "Azithromycin", "Antibiotic",
         "Treatment of certain bacterial infections.",
         "Interferes with bacterial protein production.",
         "Nausea, diarrhea.",
         "Use only when prescribed.",
         "Example: Azithral."),

        ("Pantoprazole", "Pantoprazole", "Pantoprazole", "Acid reducer",
         "Treatment of certain acid-related stomach conditions.",
         "Reduces stomach acid production.",
         "Headache, nausea.",
         "Discuss prolonged use with a healthcare professional.",
         "Example: Pantocid."),

        ("Omeprazole", "Omeprazole", "Omeprazole", "Acid reducer",
         "Treatment of certain acid-related stomach conditions.",
         "Reduces stomach acid production.",
         "Headache, nausea.",
         "Follow product instructions and medical advice.",
         "Example: Omez."),

        ("Famotidine", "Famotidine", "Famotidine", "Acid reducer",
         "Relief of certain acid-related conditions.",
         "Blocks histamine receptors involved in acid production.",
         "Headache, constipation.",
         "Seek advice if you have kidney problems.",
         "Example: Pepcid."),

        ("Ondansetron", "Ondansetron", "Ondansetron", "Antiemetic",
         "Prevention or relief of certain types of nausea and vomiting.",
         "Blocks signals involved in nausea and vomiting.",
         "Headache, constipation.",
         "Use with medical guidance, especially with heart rhythm conditions.",
         "Examples: Ondem, Zofran."),

        ("Domperidone", "Domperidone", "Domperidone", "Antiemetic",
         "Used for certain nausea and vomiting conditions.",
         "Acts on dopamine receptors.",
         "Dry mouth, headache.",
         "Can affect heart rhythm; use only under medical guidance.",
         "Example: Domstal."),

        ("Oral Rehydration Salts", "ORS", "Glucose and electrolytes",
         "Rehydration",
         "Replaces fluids and electrolytes lost during dehydration.",
         "Helps the intestine absorb water and electrolytes.",
         "Generally well tolerated when prepared correctly.",
         "Mix exactly as instructed on the packet.",
         "Examples: Electral and other ORS products."),

        ("Digene", "Antacid combination", "Antacid ingredients", "Antacid",
         "Temporary relief of acidity and heartburn.",
         "Neutralizes stomach acid; some formulations help with gas.",
         "Constipation or diarrhea.",
         "Ingredients vary by formulation; check the label.",
         "Example: Digene."),

        ("Gelusil", "Antacid combination", "Antacid ingredients", "Antacid",
         "Temporary relief of acidity and heartburn.",
         "Neutralizes stomach acid.",
         "Constipation or diarrhea.",
         "Check ingredients and follow product directions.",
         "Example: Gelusil."),

        ("Loperamide", "Loperamide", "Loperamide", "Antidiarrheal",
         "Temporary control of some types of diarrhea.",
         "Slows movement in the intestine.",
         "Constipation, abdominal discomfort.",
         "Avoid self-treatment for bloody diarrhea or high fever.",
         "Example: Imodium."),

        ("Dextromethorphan", "Dextromethorphan", "Dextromethorphan",
         "Cough suppressant",
         "Temporary relief of certain coughs.",
         "Acts on the cough reflex.",
         "Dizziness, nausea, drowsiness.",
         "Can interact with medicines; check combination products.",
         "Found in some cough syrups."),

        ("Guaifenesin", "Guaifenesin", "Guaifenesin", "Expectorant",
         "Helps loosen mucus in some cough conditions.",
         "Helps thin and loosen mucus.",
         "Nausea, dizziness.",
         "Follow the product label.",
         "Found in some cough syrups."),

        ("Ambroxol", "Ambroxol", "Ambroxol", "Mucolytic",
         "Used in some products for cough with mucus.",
         "Helps loosen mucus.",
         "Nausea, stomach discomfort.",
         "Use according to the product label.",
         "Found in some cough preparations."),

        ("Salbutamol", "Salbutamol", "Salbutamol", "Bronchodilator",
         "Relief of certain airway narrowing symptoms.",
         "Relaxes muscles around the airways.",
         "Tremor, headache, fast heartbeat.",
         "Use only as directed by a healthcare professional.",
         "Examples: Asthalin, Ventolin."),

        ("Montelukast", "Montelukast", "Montelukast sodium",
         "Allergy and asthma medicine",
         "Used for certain asthma and allergy conditions.",
         "Blocks leukotrienes involved in inflammation.",
         "Headache, stomach discomfort.",
         "Mood or behavior changes require prompt medical advice.",
         "Example: Montair."),

        ("Clotrimazole", "Clotrimazole", "Clotrimazole", "Antifungal",
         "Treatment of certain fungal infections.",
         "Interferes with fungal cell membranes.",
         "Local irritation, redness.",
         "Use the correct formulation for the affected area.",
         "Example: Candid."),

        ("Mupirocin", "Mupirocin", "Mupirocin", "Topical antibiotic",
         "Treatment of certain bacterial skin infections.",
         "Interferes with bacterial protein production.",
         "Local irritation, redness.",
         "Use only as directed.",
         "Example: T-Bact."),

        ("Calamine Lotion", "Calamine", "Calamine", "Skin protectant",
         "Soothes minor itching and skin irritation.",
         "Provides a soothing protective effect.",
         "Dryness or irritation.",
         "For external use.",
         "Available from several manufacturers."),

        ("Povidone Iodine", "Povidone-iodine", "Povidone-iodine",
         "Antiseptic",
         "Antiseptic use on appropriate skin areas.",
         "Acts against many microorganisms.",
         "Skin irritation.",
         "Follow the product label; not suitable for every wound.",
         "Example: Betadine."),

        ("Vitamin C", "Ascorbic acid", "Vitamin C", "Vitamin supplement",
         "Prevention or treatment of vitamin C deficiency.",
         "Supports collagen formation and other body functions.",
         "Stomach upset at high amounts.",
         "Excessive intake may cause digestive problems.",
         "Available from several manufacturers."),

        ("Vitamin B Complex", "B-complex vitamins", "B vitamins",
         "Vitamin supplement",
         "Supplementation when B vitamins are needed.",
         "Provides vitamins involved in normal metabolism.",
         "Stomach discomfort.",
         "Check the ingredients and avoid excessive intake.",
         "Examples: Becosules and similar products."),

        ("Vitamin B12", "Cyanocobalamin", "Vitamin B12",
         "Vitamin supplement",
         "Prevention or treatment of vitamin B12 deficiency.",
         "Supports nerve function and red blood cell formation.",
         "Usually well tolerated.",
         "Deficiency may require professional evaluation.",
         "Available from several manufacturers."),

        ("Folic Acid", "Folic acid", "Folic acid", "Vitamin supplement",
         "Prevention or treatment of folate deficiency.",
         "Supports DNA and red blood cell formation.",
         "Mild stomach discomfort.",
         "Check with a professional about appropriate use.",
         "Available from several manufacturers."),

        ("Vitamin D3", "Cholecalciferol", "Vitamin D3",
         "Vitamin supplement",
         "Prevention or treatment of vitamin D deficiency.",
         "Supports calcium balance and bone health.",
         "Excessive intake can raise blood calcium.",
         "Avoid high doses without medical guidance.",
         "Available from several manufacturers."),

        ("Calcium Supplement", "Calcium salts", "Calcium",
         "Mineral supplement",
         "Provides calcium when supplementation is needed.",
         "Supplies calcium for bones and normal body functions.",
         "Constipation, bloating.",
         "Excessive intake may be harmful.",
         "Available from several manufacturers."),

        ("Iron Supplement", "Ferrous salts", "Iron",
         "Mineral supplement",
         "Prevention or treatment of iron deficiency.",
         "Supplies iron needed for hemoglobin production.",
         "Constipation, nausea, dark stools.",
         "Keep away from children; overdose can be dangerous.",
         "Available from several manufacturers."),

        ("Iron and Folic Acid", "Iron plus folic acid",
         "Iron and folic acid", "Nutritional supplement",
         "Provides iron and folic acid when needed.",
         "Supports normal red blood cell formation.",
         "Constipation, nausea.",
         "Use according to medical guidance.",
         "Available from several manufacturers."),

        ("Multivitamin", "Multivitamin preparation",
         "Multiple vitamins and minerals", "Nutritional supplement",
         "Supplementation of certain dietary nutrients.",
         "Provides a combination of vitamins and minerals.",
         "Stomach discomfort.",
         "Do not exceed label directions.",
         "Available from several manufacturers."),

        ("Zinc Supplement", "Zinc salts", "Zinc", "Mineral supplement",
         "Prevention or treatment of zinc deficiency.",
         "Provides zinc needed for normal body functions.",
         "Nausea, stomach discomfort.",
         "Excessive intake may cause harm.",
         "Available from several manufacturers."),

        ("Calcium and Vitamin D3", "Calcium plus cholecalciferol",
         "Calcium and Vitamin D3", "Nutritional supplement",
         "Provides calcium and vitamin D when needed.",
         "Supports calcium absorption and bone health.",
         "Constipation, stomach discomfort.",
         "Avoid unnecessary high doses.",
         "Examples: Shelcal and similar products."),

        ("Vitamin B12 Injection", "Cobalamin preparation",
         "Vitamin B12", "Vitamin treatment",
         "Treatment of vitamin B12 deficiency when an injection is indicated.",
         "Replaces vitamin B12.",
         "Injection-site discomfort; other reactions are possible.",
         "Must be administered according to medical guidance.",
         "Available from several manufacturers."),

        ("Multivitamin Syrup", "Multivitamin preparation",
         "Vitamins; formulation varies", "Supplement syrup",
         "Provides selected vitamins as a supplement.",
         "Supplies vitamins included in the formulation.",
         "Possible stomach discomfort.",
         "Check ingredients and age-specific label instructions.",
         "Brand and composition vary."),

        ("Iron Tonic", "Iron preparation",
         "Iron; formulation varies", "Iron supplement",
         "Used to prevent or treat iron deficiency when indicated.",
         "Provides iron for hemoglobin production.",
         "Constipation, nausea, dark stools.",
         "Check the actual iron content; overdose can be dangerous.",
         "Brand and composition vary."),

        ("Electral ORS", "Oral Rehydration Salts",
         "Glucose and electrolytes", "Rehydration",
         "Helps replace fluids and electrolytes.",
         "Supports absorption of water and electrolytes.",
         "Generally well tolerated when prepared correctly.",
         "Prepare according to the packet instructions.",
         "Example: Electral."),

        ("Eno", "Antacid preparation", "Sodium bicarbonate and salts",
         "Antacid",
         "Temporary relief of acidity and heartburn.",
         "Neutralizes stomach acid.",
         "Bloating or stomach discomfort.",
         "Check sodium content and follow label directions.",
         "Example: Eno."),

        ("Diclofenac Gel", "Diclofenac", "Diclofenac",
         "Topical pain reliever",
         "Relief of certain localized muscle and joint pain.",
         "Reduces substances involved in inflammation.",
         "Skin irritation.",
         "For external use; follow label instructions.",
         "Available from several manufacturers."),

        ("Benzoyl Peroxide", "Benzoyl peroxide", "Benzoyl peroxide",
         "Acne treatment",
         "Treatment of acne.",
         "Reduces acne-causing bacteria and helps unclog pores.",
         "Dryness, redness, irritation.",
         "May irritate skin and bleach fabrics.",
         "Available from several manufacturers."),

        ("Adapalene", "Adapalene", "Adapalene", "Acne treatment",
         "Treatment of acne.",
         "Helps prevent clogged pores.",
         "Dryness, redness, irritation.",
         "Follow product directions; ask a professional if pregnant or planning pregnancy.",
         "Available from several manufacturers."),

        ("Zincovit", "Multivitamin and mineral preparation",
         "Vitamins and minerals", "Nutritional supplement",
         "Nutritional supplementation.",
         "Provides selected vitamins and minerals.",
         "Possible stomach discomfort.",
         "Check the ingredient list and label directions.",
         "Example: Zincovit."),

        ("Becosules", "Vitamin B complex", "B vitamins",
         "Vitamin supplement",
         "Supplementation of B vitamins.",
         "Provides vitamins involved in normal body functions.",
         "Possible stomach discomfort.",
         "Use according to the product label.",
         "Example: Becosules."),

        ("Neurobion", "Vitamin B preparation", "B vitamins",
         "Vitamin supplement",
         "Vitamin supplementation, depending on formulation.",
         "Provides selected B vitamins.",
         "Possible stomach discomfort.",
         "Formulations differ; check the package.",
         "Example: Neurobion."),

        ("Revital H", "Multivitamin and mineral preparation",
         "Vitamins and minerals", "Nutritional supplement",
         "Nutritional supplementation.",
         "Provides selected vitamins and minerals.",
         "Possible stomach discomfort.",
         "Check the formulation and label directions.",
         "Example: Revital H."),

        ("Livogen", "Iron preparation", "Iron and formulation-dependent nutrients",
         "Iron supplement",
         "Used to provide iron when supplementation is indicated.",
         "Supplies iron needed for hemoglobin production.",
         "Constipation, nausea, dark stools.",
         "Check the specific formulation; keep away from children.",
         "Example: Livogen."),

        ("Cough Syrup", "Combination varies",
         "Ingredients vary by product", "Cough preparation",
         "Used for specific cough symptoms depending on ingredients.",
         "Action depends on the ingredients.",
         "Side effects vary by formulation.",
         "Check all ingredients; some products cause drowsiness or duplicate other medicines.",
         "Example: Benadryl."),

        ("Antacid Suspension", "Antacid combination",
         "Ingredients vary by product", "Antacid",
         "Temporary relief of acidity and heartburn.",
         "Usually neutralizes stomach acid.",
         "Constipation or diarrhea, depending on ingredients.",
         "Check the exact product label.",
         "Brand and composition vary."),

        ("Saline Nasal Spray", "Sodium chloride solution",
         "Sodium chloride and water", "Nasal care",
         "Moisturizes nasal passages and helps loosen mucus.",
         "Moistens and rinses the nasal passages.",
         "Occasional irritation.",
         "Use a clean nozzle and follow package directions.",
         "Available from several manufacturers."),

        ("Artificial Tears", "Lubricating eye drops",
         "Ingredients vary by product", "Eye lubricant",
         "Temporary relief of dry-eye symptoms.",
         "Lubricates the surface of the eye.",
         "Temporary blurred vision or irritation.",
         "Check the ingredients and seek advice for persistent eye symptoms.",
         "Brand and composition vary.")
    ]

    cursor.execute("DELETE FROM medicines")

    cursor.executemany("""
        INSERT INTO medicines
        (name, generic_name, active_ingredient, category, uses,
         how_it_works, side_effects, warnings, brand_info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, medicines)

    conn.commit()
    conn.close()

    print(f"Database created successfully: {len(medicines)} medicine records added.")


if __name__ == "__main__":
    create_database()