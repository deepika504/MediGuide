/**
 * MediGuide — script.js
 *
 * Handles:
 *  1. Scan Medicine button → opens file picker
 *  2. Image file validation (client-side, type + size)
 *  3. Image preview after selection
 *  4. Show/hide Analyze Image button
 *  5. Loading state + duplicate-submit guard during upload
 *  6. Voice search using Web Speech API
 */

/* ── Constants ──────────────────────────────────────────────────────────── */

const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_BYTES   = MAX_FILE_SIZE_MB * 1024 * 1024;

const ALLOWED_TYPES = [
    "image/jpeg", "image/jpg", "image/png", "image/gif",
    "image/bmp", "image/webp", "image/tiff"
];

/* ── Scan Medicine: open the file picker ────────────────────────────────── */

function scanMedicine() {
    const imageInput = document.getElementById("medicineImage");
    if (imageInput) {
        imageInput.click();
    } else {
        alert("Medicine image upload is not available on this page.");
    }
}

/* ── Main DOMContentLoaded block ────────────────────────────────────────── */

document.addEventListener("DOMContentLoaded", function () {

    const imageInput    = document.getElementById("medicineImage");
    const analyzeButton = document.getElementById("analyzeButton");
    const scanButton    = document.getElementById("scanButton");
    const scanForm      = document.getElementById("scanForm");
    const scanArea      = document.getElementById("scanArea");
    const scanStatus    = document.getElementById("scanStatus");

    // Elements are only present on the homepage; bail silently on other pages.
    if (!imageInput) return;

    /* ── File selected ─────────────────────────────────────────────────── */

    imageInput.addEventListener("change", function () {
        const file = imageInput.files[0];

        // Clear any previous preview
        if (scanArea) scanArea.innerHTML = "";

        // Hide the Analyze button until we confirm the file is valid
        if (analyzeButton) {
            analyzeButton.hidden = true;
            analyzeButton.style.display = "none";
        }

        if (!file) return;

        // ── Client-side type check ──────────────────────────────────────
        if (!ALLOWED_TYPES.includes(file.type)) {
            alert(
                "Please select a valid image file " +
                "(JPG, PNG, GIF, BMP, WebP, or TIFF)."
            );
            imageInput.value = "";
            return;
        }

        // ── Client-side size check ──────────────────────────────────────
        if (file.size > MAX_FILE_BYTES) {
            alert(
                "The selected image is larger than " + MAX_FILE_SIZE_MB +
                " MB. Please choose a smaller image."
            );
            imageInput.value = "";
            return;
        }

        // ── Show preview ────────────────────────────────────────────────
        const objectURL = URL.createObjectURL(file);
        const preview   = document.createElement("img");

        preview.src             = objectURL;
        preview.alt             = "Selected medicine package image";
        preview.className       = "scan-preview";
        preview.style.maxWidth  = "280px";
        preview.style.maxHeight = "220px";
        preview.style.display   = "block";
        preview.style.marginTop = "16px";
        preview.style.borderRadius = "12px";
        preview.style.border    = "1px solid #cfe5da";
        preview.style.boxShadow = "0 4px 14px rgba(17,87,66,0.08)";

        // Release object URL after image loads to free memory
        preview.onload = function () {
            URL.revokeObjectURL(objectURL);
        };

        if (scanArea) {
            const label = document.createElement("p");
            label.textContent = "Selected image:";
            label.style.cssText =
                "margin-top:16px;font-size:13px;color:#687d77;font-weight:600;";
            scanArea.appendChild(label);
            scanArea.appendChild(preview);
        }

        // ── Show Analyze Image button ───────────────────────────────────
        if (analyzeButton) {
            analyzeButton.hidden = false;
            analyzeButton.style.display = "inline-block";
        }
    });

    /* ── Form submit: loading state + duplicate-submit guard ───────────── */

    if (scanForm) {
        scanForm.addEventListener("submit", function (event) {

            const file = imageInput.files[0];

            if (!file) {
                event.preventDefault();
                alert("Please select a medicine package image first.");
                return;
            }

            // Prevent double-clicks while the upload is in progress
            if (analyzeButton) {
                analyzeButton.disabled = true;
                analyzeButton.textContent = "Analyzing…";
            }
            if (scanButton) {
                scanButton.disabled = true;
            }

            // Show the processing indicator
            if (scanStatus) {
                scanStatus.hidden = false;
                scanStatus.style.display = "flex";
            }
        });
    }
});

/* ── Voice search ───────────────────────────────────────────────────────── */

function startVoiceSearch() {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert(
            "Voice search is not supported by this browser. " +
            "Please use the search box, or try Chrome on desktop."
        );
        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang            = "en-IN";
    recognition.continuous      = false;
    recognition.interimResults  = false;
    recognition.maxAlternatives = 1;

    // Fill the search box with the recognised text, then submit automatically
    recognition.onresult = function (event) {
        const spokenText = event.results[0][0].transcript.trim();

        if (spokenText) {
            const searchInput = document.getElementById("searchInput");
            if (searchInput) {
                searchInput.value = spokenText;
                // Small delay so the user can see what was recognised
                setTimeout(function () {
                    searchInput.form.submit();
                }, 600);
            } else {
                // Fallback: navigate directly
                window.location.href =
                    "/search?q=" + encodeURIComponent(spokenText);
            }
        }
    };

    recognition.onerror = function (event) {
        if (event.error === "not-allowed") {
            alert(
                "Microphone access was denied. " +
                "Please allow microphone permission in your browser and try again."
            );
        } else {
            alert(
                "Voice search could not be completed. " +
                "Please check microphone permission and try again."
            );
        }
    };

    recognition.onstart = function () {
        // Subtle visual cue; alert() would block the recogniser on some browsers
        const btn = document.querySelector('[onclick="startVoiceSearch()"]');
        if (btn) btn.textContent = "🎙 Listening…";

        setTimeout(function () {
            if (btn) btn.textContent = "♫ Ask by Voice";
        }, 5000);
    };

    recognition.start();
}
