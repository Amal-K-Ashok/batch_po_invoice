
________________________________________
🧾 Batch PO vs Invoice Comparator (Streamlit + Gemini)
📘 Overview
This project is a Streamlit web application that compares Purchase Orders (POs) and Invoices automatically.
It uses pdfplumber to extract text from PDFs and Google Gemini AI to interpret the content into structured JSON.
Then, it performs intelligent item-by-item matching between PO and Invoice entries to highlight matches, mismatches, or partial matches.
________________________________________
🚀 Key Features
•	📄 Upload multiple Purchase Orders and Invoices (PDF format).
•	🤖 Automatic extraction of structured data using Gemini AI.
•	🔍 Smart fuzzy matching of item descriptions, prices, and totals.
•	🎨 Color-coded comparison tables using Streamlit and pandas.
•	⚙️ Adjustable similarity threshold for item matching.
•	🧮 Summary of matched and mismatched items for each pair.
________________________________________
🧰 Tech Stack
Component	Purpose
Python	Core language
Streamlit	Web UI framework
pdfplumber	PDF text extraction
pandas	Data organization & table display
dotenv	Load environment variables
google-generativeai (Gemini)	AI-powered document understanding
difflib, re, json, os	Core utilities for text matching & data parsing
________________________________________
📦 Setup Instructions
1. Clone the Repository
git clone https://github.com/Amal-K-Ashok/batch_po_invoice.git
cd po-invoice-comparator
2. Create a Virtual Environment (Recommended)
python -m venv venv
source venv/bin/activate       # On macOS/Linux
venv\Scripts\activate          # On Windows
3. Install Dependencies
pip install -r requirements.txt
Example requirements.txt:
streamlit
pdfplumber
pandas
python-dotenv
google-generativeai
________________________________________
🔑 4. Set Up Your Gemini API Key
Create a .env file in the project root with your Google Gemini API key:
touch .env
Then add:
GEMINI_API_KEY=your_gemini_api_key_here
________________________________________

▶️ 5. Run the App
Start the Streamlit server:
streamlit run app.py
Then open the local URL shown (e.g. http://localhost:8501) in your browser.
________________________________________
📄 6. Usage
1.	Upload one or more Purchase Orders (PDF).
2.	Upload one or more Invoices (PDF).
3.	Adjust the item match threshold slider in the sidebar (default: 0.7).
4.	Click “Compare All Documents”.
5.	View the color-coded table:
o	🟩 Green = Match
o	🟥 Red = Mismatch
o	🟨 Partial Match (if totals differ)
6.	Click Clear All to reset and upload new files.
________________________________________
📊 7. Output Example
PO Item	PO Qty	PO Total	Invoice Item	Invoice Qty	Invoice Total	Status	Match Score
Solenoid Valve DN45 PTFE	6	6750	Solenoid Valve DN45 PTFE Model: 10005	6	6750	✅ Match	0.73
PLC Module DN90 EPDM	3	9600	PLC Module DN90 EPDM Model: 10002	3	9600	✅ Match	0.71
________________________________________
🧩 8. How It Works (Internally)
1.	PDF Extraction:
pdfplumber reads uploaded PDFs and extracts text.
2.	AI-Powered Structuring:
The extracted text is sent to Gemini 2.5 Flash, which converts it into structured JSON with item-level details.
3.	Comparison Logic:
o	token_similarity() computes both token overlap and character similarity.
o	Each PO item is compared against invoice items to find the best match.
o	Items are marked as Match, Partial Match, or Mismatch based on description and total.
4.	Result Display:
The final comparison is presented in a Streamlit DataFrame with color highlights and match summaries.
________________________________________
⚠️ Notes
•	Large PDFs may take longer due to Gemini API processing.
•	Make sure your .env file is correctly set with the API key before running.
•	Works best when PO and Invoice texts are clear and not image-scanned PDFs.
________________________________________
💡 Future Enhancements
•	OCR support for scanned PDFs (using pytesseract or Gemini Vision API).
•	Export comparison results to Excel or CSV.
•	Multi-threaded API calls for faster batch processing.
•	Vendor-specific parsing improvements.
________________________________________
👨‍💻 Author
Amal K.
📧 Email:
💬 Built using Python, Streamlit, and Gemini AI
________________________________________


