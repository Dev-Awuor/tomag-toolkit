# tomag-toolkit
# tomag-toolkit

A lightweight Python toolkit for mining insights out of your email archives and meeting transcripts.  
It provides utilities to:

- **Extract** email metadata and message bodies from `.eml` files into a CSV.  
- **Generate** Markdown snippets from your CSV data for quick reporting.  
- **Manage** meeting transcripts alongside your email analysis pipeline.

---

## Features

1. **`extract_emails.py`**  
   - Parses one or more `.eml` files  
   - Outputs a tidy `emails.csv` of senders, recipients, dates, subjects, and bodies  
   - Generates a verbose log (`extract_emails.log`) for audit or troubleshooting  

2. **`generate_snippet_md.py`**  
   - Reads your `emails.csv` and/or other CSV data  
   - Produces a Markdown file of “snippets” or bite-sized summaries  
   - Ideal for embedding in reports, wikis, or slide decks  

3. **`tomag_toolkit.py`**  
   - A wrapper CLI that chains extraction → snippet generation  
   - Use it to run your end-to-end pipeline with a single command  

4. **Meeting Transcript Support**  
   - Drop your `meeting_transcript.docx` in the working folder  
   - Use the toolkit to pull out action items or callouts into your CSV/Markdown flow  

---

## Getting Started

### Prerequisites

- Python 3.10 or newer  
- `pip` package manager  

### Installation

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-org/tomag-toolkit.git
   cd tomag-toolkit

Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
⚙️ Usage
1. Extract Emails to CSV
bash
Copy
Edit
python extract_emails.py \
  --input-folder path/to/.eml/files \
  --output-file emails.csv
Options

Flag	Description
--input-folder	Directory containing one or more .eml files
--output-file	Name/location for the generated emails.csv
--log-file	(Optional) Path to write verbose extraction logs

2. Generate Markdown Snippets
bash
Copy
Edit
python generate_snippet_md.py \
  --csv-file emails.csv \
  --template templates/snippet_template.md \
  --output-file snippets.md
Options

Flag	Description
--csv-file	Path to your source CSV (e.g. emails.csv)
--template	(Optional) Jinja-style Markdown template for customization
--output-file	Destination Markdown file (default: snippets.md)

3. Run the Full Toolkit
bash
Copy
Edit
python tomag_toolkit.py \
  --emails-dir path/to/emails \
  --transcript meeting_transcript.docx \
  --out-csv analysis/emails.csv \
  --out-md analysis/snippets.md
This will:

Extract emails from --emails-dir into analysis/emails.csv

Parse your --transcript for highlights (if implemented)

Generate analysis/snippets.md from the combined data

📁 Project Structure
pgsql
Copy
Edit
.
├── LICENSE
├── README.md
├── extract_emails.py        ← EML → CSV
├── generate_snippet_md.py   ← CSV → Markdown
├── tomag_toolkit.py         ← All-in-one CLI
├── meeting_transcript.docx  ← Example transcript
└── requirements.txt         ← Python dependencies
🤝 Contributing
Fork the repository

Create your feature branch (git checkout -b feature/XYZ)

Commit your changes (git commit -m "Add XYZ")

Push to your branch (git push origin feature/XYZ)

Open a Pull Request

Please follow the existing code style and include tests where appropriate.

📝 License
This project is released under the MIT License.
Feel free to use, modify, and distribute as you see fit!

📬 Contact
Have feedback or need help?
Create an issue or reach out to the maintainers at lloydawuor.dev@gmail.com.
