"""
MediGuide — app.py
Flask application for medicine information and image-based OCR scanning.
Educational project. Not a medical advice or prescription tool.
"""

from flask import Flask, render_template, request
import sqlite3
import os
import re
import threading
import webbrowser
from difflib import SequenceMatcher
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter

# ── Tesseract path (Windows) ──────────────────────────────────────────────────
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__)

# 5 MB upload limit — rejects oversized files before processing
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

DATABASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "database",
    "mediguide.db"
)

# File types accepted for image upload
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff", "tif"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_db_connection():
    """Return a SQLite connection with row-dict access."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def allowed_file(filename):
    """Return True only if the filename has an accepted image extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def tokenize_ocr_text(text):
    """
    Split raw OCR output into individual, meaningful lowercase words.

    OCR returns a multi-line blob such as:
        'PARACETAMOL 500mg\\nTablet IP\\nCrocin\\nBatch No. XYZ\\nMfg: ...'

    We split on whitespace and common punctuation, then keep only tokens
    that are at least 3 characters long, are not pure numbers, and are not
    common packaging words that appear on almost every medicine box.
    """
    # Words that appear on almost every medicine pack and would cause
    # false matches across unrelated medicines — ignore them.
    STOPWORDS = {
        "tablets", "tablet", "capsules", "capsule", "syrup", "solution",
        "injection", "cream", "lotion", "drops", "ointment", "suspension",
        "oral", "use", "only", "each", "contains", "composition",
        "india", "limited", "pvt", "ltd", "llp", "corp",
        "batch", "bno", "mfd", "mfg", "exp", "expiry", "manufactured",
        "store", "cool", "dry", "place", "below", "above",
        "keep", "reach", "children", "away", "from",
        "read", "insert", "leaflet", "carefully", "before",
        "prescription", "drug", "medicine", "dosage", "dose",
        "warning", "caution", "schedule", "license", "lic",
        "mrp", "incl", "taxes", "tax", "gst", "for", "tabs",
        "pack", "packing", "strip", "blister", "box",
        "marketed", "manufactured", "distributed", "imported",
        "phone", "fax", "email", "website", "www",
        "enter", "name", "ingredient", "scan", "analyze", "ask",
        "voice", "selected", "image",
        "date", "year", "month", "jan", "feb", "mar", "apr",
        "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    }

    raw = re.split(r"[\s\n\r,.\-/|:;()\[\]@#&*+=<>\"']+", text)
    tokens = []
    seen = set()
    for value in raw:
        token = value.strip().lower()
        if (
            len(token) >= 3
            and not token.isdigit()
            and token not in STOPWORDS
            and token not in seen
        ):
            tokens.append(token)
            seen.add(token)

    return tokens


def search_by_tokens(tokens, ocr_text=""):
    """
    Return a single medicine only when OCR contains a unique, strong match
    for its name, ingredient, or an explicitly listed brand.
    """
    if not tokens:
        return []

    connection = get_db_connection()
    try:
        medicines = connection.execute(
            "SELECT * FROM medicines ORDER BY name"
        ).fetchall()
    finally:
        connection.close()

    phrases = set()
    normalized_tokens = [
        re.sub(r"[^a-z0-9]", "", token.lower())
        for token in tokens
    ]
    normalized_tokens = [token for token in normalized_tokens if token]
    for start in range(len(normalized_tokens)):
        for length in range(1, min(3, len(normalized_tokens) - start) + 1):
            phrases.add("".join(normalized_tokens[start:start + length]))

    for line in ocr_text.splitlines():
        line_tokens = [
            re.sub(r"[^a-z0-9]", "", token.lower())
            for token in re.findall(r"\S+", line)
        ]
        line_tokens = [token for token in line_tokens if token]
        for start in range(len(line_tokens)):
            for length in range(1, min(6, len(line_tokens) - start) + 1):
                phrases.add("".join(line_tokens[start:start + length]))

    def normalize(value):
        return re.sub(r"[^a-z0-9]", "", value.lower())

    matches = []
    for medicine in medicines:
        identifiers = [
            (normalize(medicine["name"] or ""), 1.0),
            (normalize(medicine["generic_name"] or ""), 0.9),
            (normalize(medicine["active_ingredient"] or ""), 0.9),
        ]
        brand_info = medicine["brand_info"] or ""
        brand_list = re.search(
            r"examples?\s*:\s*(.*)",
            brand_info,
            flags=re.IGNORECASE
        )
        brands = []
        if brand_list:
            brands = [
                normalize(brand.split("(", 1)[0].strip())
                for brand in brand_list.group(1).split(",")
            ]

        best_score = 0.0
        for identifier, exact_score in identifiers:
            if not identifier:
                continue
            if identifier in phrases:
                best_score = max(best_score, exact_score)
            elif len(identifier) >= 6 and any(
                len(phrase) >= 8
                and (phrase in identifier or identifier in phrase)
                for phrase in phrases
            ):
                best_score = max(best_score, exact_score * 0.9)
            elif len(identifier) >= 6:
                similarity = max(
                    (SequenceMatcher(None, identifier, phrase).ratio()
                     for phrase in phrases),
                    default=0.0
                )
                if similarity >= 0.82:
                    best_score = max(
                        best_score,
                        similarity * exact_score * 0.9
                    )

        for brand in brands:
            if not brand:
                continue
            if brand in phrases:
                normalized_name = normalize(medicine["name"] or "")
                brand_score = (
                    1.1 if normalized_name.startswith(brand) else 0.95
                )
                best_score = max(best_score, brand_score)
            elif len(brand) >= 6:
                similarity = max(
                    (SequenceMatcher(None, brand, phrase).ratio()
                     for phrase in phrases),
                    default=0.0
                )
                if similarity >= 0.82:
                    best_score = max(best_score, similarity * 0.85)

        if best_score:
            matches.append((best_score, medicine))

    if not matches:
        return []

    highest_score = max(score for score, _ in matches)
    best_matches = [
        medicine
        for score, medicine in matches
        if score == highest_score
    ]
    return best_matches if len(best_matches) == 1 else []


def preprocess_image(image):
    """
    Preprocess a PIL image to improve Tesseract accuracy on medicine packaging.

    Medicine packs — especially foil blister packs — are shiny and metallic,
    which causes glare and makes OCR fail. Steps applied:
      1. Convert to grayscale (removes colour noise).
      2. Scale up small images (Tesseract is more accurate on larger text).
      3. Boost contrast (makes text stand out from background).
      4. Sharpen edges (clearer character outlines).
    """
    # 1. Grayscale
    gray = image.convert("L")

    # 2. Scale up if the image is small — Tesseract works best at ~300 DPI
    width, height = gray.size
    if width < 1000:
        scale = 1000 / width
        gray = gray.resize(
            (int(width * scale), int(height * scale)),
            Image.LANCZOS
        )

    # 3. Boost contrast
    gray = ImageEnhance.Contrast(gray).enhance(2.5)

    # 4. Sharpen
    gray = gray.filter(ImageFilter.SHARPEN)
    gray = gray.filter(ImageFilter.SHARPEN)  # apply twice for stronger effect

    return gray


def run_ocr(image):
    """
    Run Tesseract OCR on a PIL image using multiple page-segmentation modes.

    Tries three different modes and returns the longest result, because
    different layouts (blister pack, cardboard box, label) respond better
    to different PSM settings:
      - psm 6: uniform block of text (standard medicine box)
      - psm 11: sparse text with no specific layout (foil/blister pack)
      - psm 3: automatic page layout detection (general fallback)

    The preprocessed grayscale version is tried first; if it produces less
    text than the colour version, the colour version is used as a fallback.
    """
    configs = [
        r"--oem 3 --psm 6",   # uniform block
        r"--oem 3 --psm 11",  # sparse text — best for blister packs
        r"--oem 3 --psm 3",   # auto layout detection
    ]
    processed = preprocess_image(image)
    best_text = ""

    for config in configs:
        result = pytesseract.image_to_string(processed, config=config).strip()
        result_colour = pytesseract.image_to_string(image, config=config).strip()
        candidate = result if len(result) >= len(result_colour) else result_colour
        if len(candidate) > len(best_text):
            best_text = candidate

    crop_boxes = [
        (
            int(image.width * 0.1),
            int(image.height * 0.2),
            int(image.width * 0.92),
            int(image.height * 0.55)
        ),
        (
            int(image.width * 0.02),
            int(image.height * 0.3),
            int(image.width * 0.48),
            int(image.height * 0.85)
        ),
    ]
    crop_texts = []
    for box in crop_boxes:
        processed_crop = preprocess_image(image.crop(box))
        crop_texts.extend(
            pytesseract.image_to_string(
                processed_crop,
                config=f"--oem 3 --psm {psm}"
            ).strip()
            for psm in (6, 7, 13)
        )

    additional_text = list(dict.fromkeys(
        text for text in crop_texts
        if text and text not in best_text
    ))
    return "\n".join([best_text, *additional_text]).strip()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search")
def search_medicine():
    """Text-based medicine search by name, generic name, or active ingredient."""
    query = request.args.get("q", "").strip()

    if not query:
        return render_template(
            "medicine.html",
            medicines=[],
            query="",
            scan_mode=False
        )

    connection = get_db_connection()
    try:
        medicines = connection.execute(
            """
            SELECT * FROM medicines
            WHERE LOWER(name) = LOWER(?)
               OR LOWER(generic_name) = LOWER(?)
               OR LOWER(active_ingredient) = LOWER(?)
            ORDER BY name
            """,
            (query,) * 3
        ).fetchall()

        if not medicines:
            medicines = connection.execute(
                """
                SELECT * FROM medicines
                WHERE LOWER(name)              LIKE LOWER(?)
                   OR LOWER(generic_name)      LIKE LOWER(?)
                   OR LOWER(active_ingredient) LIKE LOWER(?)
                   OR LOWER(brand_info)        LIKE LOWER(?)
                ORDER BY name
                """,
                (f"%{query}%",) * 4
            ).fetchall()
    finally:
        connection.close()

    return render_template(
        "medicine.html",
        medicines=medicines,
        query=query,
        scan_mode=False
    )


@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    """
    Receive an uploaded medicine package image, run Tesseract OCR on it,
    tokenize the extracted text, and search the database for matches.
    """

    # ── 1. Validate that a file was uploaded ──────────────────────────────────
    uploaded_file = request.files.get("medicineImage")

    if not uploaded_file or not uploaded_file.filename:
        return render_template(
            "medicine.html",
            medicines=[],
            query="",
            scan_mode=True,
            message="No image was received. Please select a medicine package photo and try again."
        )

    # ── 2. Validate file extension (server-side) ──────────────────────────────
    if not allowed_file(uploaded_file.filename):
        return render_template(
            "medicine.html",
            medicines=[],
            query="",
            scan_mode=True,
            message="Unsupported file type. Please upload a JPG, PNG, or similar image."
        )

    # ── 3. Open, preprocess, and run OCR with multiple fallback modes ────────
    try:
        # image.verify() reads the stream to the end; seek back before re-opening.
        image = Image.open(uploaded_file.stream)
        image.verify()

        uploaded_file.stream.seek(0)
        image = Image.open(uploaded_file.stream).convert("RGB")

        images_to_scan = [image]
        if image.height > image.width:
            images_to_scan.append(image.rotate(270, expand=True))
        extracted_texts = [
            text for text in (run_ocr(candidate) for candidate in images_to_scan)
            if text
        ]

    except Exception:
        # Do not expose internal tracebacks to users
        return render_template(
            "medicine.html",
            medicines=[],
            query="",
            scan_mode=True,
            message=(
                "The image could not be read. "
                "Please try a clearer, well-lit photo of the medicine package."
            )
        )

    # ── 4. Handle empty OCR output ────────────────────────────────────────────
    if not extracted_texts:
        return render_template(
            "medicine.html",
            medicines=[],
            query="",
            scan_mode=True,
            ocr_text="",
            message=(
                "No text could be read from this image. "
                "Try a clearer photo with good lighting, "
                "or type the medicine name in the search box."
            )
        )

    # ── 5. Tokenize OCR output and search the database ────────────────────────
    if not any(tokenize_ocr_text(text) for text in extracted_texts):
        extracted_text = max(extracted_texts, key=len)
        return render_template(
            "medicine.html",
            medicines=[],
            query="",
            scan_mode=True,
            ocr_text=extracted_text[:300],
            message=(
                "Text was found but no recognisable medicine words could be extracted. "
                "Please type the medicine name in the search box."
            )
        )

    matching_results = []
    for text in extracted_texts:
        tokens = tokenize_ocr_text(text)
        matches = search_by_tokens(tokens, text)
        if matches:
            matching_results.append((text, matches))

    matched_names = {
        medicine["name"]
        for _, matches in matching_results
        for medicine in matches
    }
    if len(matched_names) == 1:
        extracted_text, matching_medicines = max(
            (
                (text, matches)
                for text, matches in matching_results
                if matches[0]["name"] in matched_names
            ),
            key=lambda result: len(result[0])
        )
        medicines = matching_medicines
    else:
        extracted_text = max(extracted_texts, key=len)
        medicines = []

    # ── 6. Build a tidy display string from the OCR output ───────────────────
    # Show only the first non-empty line so the heading stays readable.
    first_line = next(
        (ln.strip() for ln in extracted_text.splitlines() if ln.strip()),
        "Scanned image"
    )
    query_display = first_line[:80] + ("..." if len(first_line) > 80 else "")

    return render_template(
        "medicine.html",
        medicines=medicines,
        query=query_display,
        scan_mode=True,
        ocr_text=extracted_text[:600],   # raw OCR preview (capped for display)
        message=(
            "OCR found one likely medicine match based on the package text. "
            "Image recognition can misread labels, so verify the name on the "
            "packaging or ask a pharmacist."
            if medicines
            else (
                "No database match was found for the text on this image. "
                "You can type the medicine name in the search box to search manually."
            )
        )
    )


# ── Error handlers ────────────────────────────────────────────────────────────

@app.errorhandler(413)
def file_too_large(error):
    """Handle uploads that exceed the 5 MB limit."""
    return render_template(
        "medicine.html",
        medicines=[],
        query="",
        scan_mode=True,
        message="The uploaded file is too large. Please use an image smaller than 5 MB."
    ), 413


@app.errorhandler(404)
def page_not_found(error):
    return render_template("index.html"), 404


# ── Entry point ───────────────────────────────────────────────────────────────

def open_browser():
    """Open the app in Chrome (or Edge / default browser as fallback)."""
    url = "http://127.0.0.1:5000"

    # Try Chrome first, then Edge, then the system default browser
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\DEEPIKA\AppData\Local\Google\Chrome\Application\chrome.exe",
    ]
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]

    for path in chrome_paths:
        if os.path.exists(path):
            webbrowser.register(
                "chrome",
                None,
                webbrowser.BackgroundBrowser(path)
            )
            webbrowser.get("chrome").open(url)
            return

    for path in edge_paths:
        if os.path.exists(path):
            webbrowser.register(
                "edge",
                None,
                webbrowser.BackgroundBrowser(path)
            )
            webbrowser.get("edge").open(url)
            return

    # Fallback: open whatever browser Windows has set as default
    webbrowser.open(url)


if __name__ == "__main__":
    # Open the browser after a short delay so Flask has time to start
    threading.Timer(1.2, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
