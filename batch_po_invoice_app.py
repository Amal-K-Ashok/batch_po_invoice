import os
import re
import json
import pdfplumber
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
from difflib import SequenceMatcher
from itertools import zip_longest

# Load .env
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    st.warning("Set GEMINI_API_KEY in .env or environment before running.")
else:
    genai.configure(api_key=GEMINI_KEY)

MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(page_title="Batch PO vs Invoice Comparator", layout="wide")

st.title("📄 Batch PO vs Invoice Comparator (Streamlit + Gemini)")

# ---- Helpers ----
def extract_text_from_pdf(file_obj):
    """Extract text from all pages of a PDF."""
    try:
        with pdfplumber.open(file_obj) as pdf:
            pages_text = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
        return "\n\n".join(pages_text).strip()
    except Exception as e:
        st.error(f"Could not read PDF: {e}")
        return ""

def call_gemini_for_structure(text, doc_type="Document"):
    """Use Gemini to extract structured JSON fields."""
    prompt = f"""
Extract the structured data from the following {doc_type} text.
Return only valid JSON with keys:
document_type, number, vendor, date, grand_total, items:[description, qty, unit_price, total].
Make sure the JSON is valid and complete.

Text:
\"\"\"{text[:15000]}\"\"\"
"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        resp = model.generate_content(prompt)
        raw = resp.text.strip()
        m = re.search(r"(\{[\s\S]*\})", raw)
        json_text = m.group(1) if m else raw
        parsed = json.loads(json_text)
        return parsed, None
    except Exception as e:
        return None, f"Gemini parsing failed: {e}"

def token_similarity(a, b):
    """Token-based similarity (handles extra words like HS Code)."""
    a_tokens = set(re.findall(r"\w+", a.lower()))
    b_tokens = set(re.findall(r"\w+", b.lower()))
    overlap = len(a_tokens & b_tokens) / max(len(a_tokens | b_tokens), 1)
    char_sim = SequenceMatcher(None, a.lower(), b.lower()).ratio()
    return (overlap + char_sim) / 2
def compare_structures(po_struct, inv_struct, item_match_threshold=0.7):
    import pandas as pd

    rows = []
    po_items = po_struct.get("items", []) if po_struct else []
    inv_items = inv_struct.get("items", []) if inv_struct else []
    inv_used = set()

    for po_it in po_items:
        best_match = None
        best_score = 0.0
        best_idx = None

        # ✅ Find best one-to-one match for each PO item
        for idx, inv_it in enumerate(inv_items):
            if idx in inv_used:
                continue
            score = token_similarity(
                po_it.get("description", ""), inv_it.get("description", "")
            )
            if score > best_score:
                best_score = score
                best_match = inv_it
                best_idx = idx

        # ✅ Only mark as used if above threshold
        if best_idx is not None and best_score >= item_match_threshold:
            inv_used.add(best_idx)

        inv_it = best_match
        po_qty = po_it.get("qty", "")
        inv_qty = inv_it.get("qty", "") if inv_it else ""
        po_price = po_it.get("unit_price", "")
        inv_price = inv_it.get("unit_price", "") if inv_it else ""
        po_total = po_it.get("total", "")
        inv_total = inv_it.get("total", "") if inv_it else ""

        # ✅ Determine match status
        if best_score >= item_match_threshold and str(po_total) == str(inv_total):
            status = "Match"
        elif best_score >= item_match_threshold:
            status = "Partial Match"
        else:
            status = "Mismatch"

        rows.append({
            "PO Item": po_it.get("description", ""),
            "PO Qty": po_qty,
            "PO Price": po_price,
            "PO Total": po_total,
            "Invoice Item": inv_it.get("description", "") if inv_it else "",
            "Invoice Qty": inv_qty,
            "Invoice Price": inv_price,
            "Invoice Total": inv_total,
            "Status": status,
            "Match Score": round(best_score, 2),
        })

    # ✅ Add any unmatched invoice items (still unused)
    for idx, inv_it in enumerate(inv_items):
        if idx not in inv_used:
            rows.append({
                "PO Item": "",
                "PO Qty": "",
                "PO Price": "",
                "PO Total": "",
                "Invoice Item": inv_it.get("description", ""),
                "Invoice Qty": inv_it.get("qty", ""),
                "Invoice Price": inv_it.get("unit_price", ""),
                "Invoice Total": inv_it.get("total", ""),
                "Status": "Mismatch",
                "Match Score": 0.0,
            })

    return pd.DataFrame(rows)

# ---- UI ----
st.sidebar.header("Options")
threshold = st.sidebar.slider("Item match threshold (similarity)", 50, 95, 70) / 100.0

po_files = st.file_uploader("📥 Upload one or more Purchase Orders (PDF)", type=["pdf"], accept_multiple_files=True)
inv_files = st.file_uploader("📥 Upload one or more Invoices (PDF)", type=["pdf"], accept_multiple_files=True)

if st.button("Compare All Documents"):
    if not po_files or not inv_files:
        st.error("Please upload at least one PO and one Invoice.")
    else:
        with st.spinner("Extracting and analyzing..."):
            po_data = []
            for f in po_files:
                text = extract_text_from_pdf(f)
                parsed, err = call_gemini_for_structure(text, "Purchase Order")
                po_data.append((f.name, parsed, err))

            inv_data = []
            for f in inv_files:
                text = extract_text_from_pdf(f)
                parsed, err = call_gemini_for_structure(text, "Invoice")
                inv_data.append((f.name, parsed, err))

        # Pair them by index (or name similarity)
        for (po_name, po_struct, po_err), (inv_name, inv_struct, inv_err) in zip_longest(po_data, inv_data, fillvalue=(None, None, None)):
            st.markdown(f"### 🧾 Comparison: **{po_name or 'N/A'}** ↔ **{inv_name or 'N/A'}**")

            if po_err:
                st.error(f"PO error: {po_err}")
                continue
            if inv_err:
                st.error(f"Invoice error: {inv_err}")
                continue

            df = compare_structures(po_struct, inv_struct, item_match_threshold=threshold)

            def color_status(val):
                return 'background-color: #d4f7dc' if val == "Match" else 'background-color: #f7d4d4'
            st.dataframe(df.style.applymap(color_status, subset=["Status"]), use_container_width=True)

            total_matches = sum(df["Status"]=="Match")
            st.success(f"✅ {total_matches}/{len(df)} items matched for this pair")

if st.button("Clear All"):
    st.experimental_rerun()

st.markdown("---")
st.caption("Batch comparison of POs and Invoices using pdfplumber + Gemini. Matches tolerate extra info like HS codes.")
