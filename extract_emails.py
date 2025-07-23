#!/usr/bin/env python3
"""
Extract email snippets from .eml files and .docx transcripts with validation, logging, and metadata.
"""
import os
import glob
import argparse
import logging
from bs4 import BeautifulSoup
import pandas as pd
from email import policy
from email.parser import BytesParser
from docx import Document

# Setup logging
logging.basicConfig(
    filename='extract_emails.log', level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Validate folder
def validate_folder(path):
    if not os.path.isdir(path):
        logging.error(f"Invalid folder path: {path}")
        raise FileNotFoundError(f"Folder not found: {path}")

# Parse .eml files
def parse_emails(folder, topics, num):
    import os, glob, re
    from bs4 import BeautifulSoup
    from email import policy
    from email.parser import BytesParser
    import pandas as pd

    records = []
    for filepath in glob.glob(os.path.join(folder, '**', '*.eml'), recursive=True):
        try:
            msg = BytesParser(policy=policy.default).parse(open(filepath,'rb'))
        except Exception as e:
            continue

        # Headers
        date    = pd.to_datetime(msg['Date']) if msg['Date'] else pd.NaT
        sender  = msg.get('From','')
        subject = msg.get('Subject','')

        # Extract plain or HTML
        if msg.is_multipart():
            # Prefer text/plain parts
            part = next((p for p in msg.walk()
                         if p.get_content_type()=='text/plain' and not p.is_attachment()), None)
            body = part.get_content() if part else ''
        else:
            body = msg.get_content() or ''

        # Strip all HTML tags
        body = BeautifulSoup(body, 'html.parser').get_text(separator='\n')

        # Remove boilerplate and collapse lines
        body = '\n'.join(
            l for l in body.splitlines()
            if l.strip() and 'view this email' not in l.lower()
        )
        # Collapse duplicates and long URLs
        body = re.sub(r'^(https?://\S+)\n\1$', r'\1', body, flags=re.MULTILINE)
        body = re.sub(r'\n{2,}', '\n', body).strip()

        records.append({
            'Date': date, 'From': sender,
            'Subject': subject, 'Body': body
        })

    df = pd.DataFrame(records)

    # Tag topics
    for topic, kws in topics.items():
        pattern = '|'.join(kws)
        df[topic] = df['Body'].str.contains(pattern, case=False, na=False)

    # Return top-N per topic
    return {
        topic: df[df[topic]].sort_values('Date', ascending=False).head(num)
        for topic in topics
    }

# Parse .docx transcript
def parse_transcript_docx(path, keywords):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    doc = Document(path)
    records = []
    for i, para in enumerate(doc.paragraphs, 1):
        text = para.text.strip()
        if any(kw.lower() in text.lower() for kw in keywords):
            records.append({'LineNo': i, 'Text': text})
    return pd.DataFrame(records)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract email & transcript snippets')
    parser.add_argument('-f','--folder', default='.', help='Root folder for .eml files')
    parser.add_argument('-t','--topics', required=True,
                        help='Topics as name:kw1,kw2;...')
    parser.add_argument('-n','--num', type=int, default=5, help='Top N per topic')
    parser.add_argument('-x','--transcript', help='Path to .docx transcript file')
    parser.add_argument('-k','--keywords', help='Comma-separated keywords for transcript')
    args = parser.parse_args()

    # Validate and parse emails
    validate_folder(args.folder)
    # ─── Ensure CSV output folder exists ─────────────────────────────
    output_dir = os.path.join(args.folder, 'csv')
    os.makedirs(output_dir, exist_ok=True)
    print(f"Writing all snippets into: {output_dir}")
    topics = {name: val.split(',') for name,val in (pair.split(':',1) for pair in args.topics.split(';'))}
    email_results = parse_emails(args.folder, topics, args.num)
    for topic, df in email_results.items():
        out = os.path.join(output_dir, f'snippets_{topic}.csv')
        
        df.to_csv(out, index=False)
        logging.info(f'Wrote {len(df)} rows to {out}')
        print(f'Wrote {len(df)} rows to {out}')

    # Parse transcript if provided
    if args.transcript and args.keywords:
        df_tx = parse_transcript_docx(args.transcript, args.keywords.split(','))
        out_tx = args.transcript.replace('.docx','_excerpts.csv')
        df_tx.to_csv(out_tx, index=False)
        print(f'Extracted {len(df_tx)} lines to {out_tx}')