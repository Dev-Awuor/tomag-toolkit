#!/usr/bin/env python3
"""
TOMAG Toolkit: CLI for emails & transcripts with config support.
"""
import os
import sys
import yaml
import argparse
import logging
import pandas as pd
import glob
from email import policy
from email.parser import BytesParser
from docx import Document

# Setup logging
def setup_logging():
    logging.basicConfig(
        filename='tomag_toolkit.log', level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s'
    )

# Parse emails

def parse_emails(folder, topics, num):
    import os, glob
    from email import policy
    from email.parser import BytesParser
    from bs4 import BeautifulSoup
    import pandas as pd

    records = []
    pattern = os.path.join(folder, '**', '*.eml')
    for filepath in glob.glob(pattern, recursive=True):
        try:
            msg = BytesParser(policy=policy.default).parse(open(filepath, 'rb'))
        except Exception as e:
            print(f"Failed to parse {filepath}: {e}")
            continue

        # Headers
        date = pd.to_datetime(msg['Date']) if msg['Date'] else pd.NaT
        sender  = msg.get('From', '')
        subject = msg.get('Subject', '')

        # Body extraction
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain' and not part.is_attachment():
                    body = part.get_content()
                    break
            if not body:
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        html = part.get_content()
                        body = BeautifulSoup(html, 'html.parser').get_text(separator=' ')
                        break
        else:
            body = msg.get_content() or ''

        records.append({
            'Date':    date,
            'From':    sender,
            'Subject': subject,
            'Body':    body
        })

    df = pd.DataFrame(records)

    # Tag by topic
    for topic, kws in topics.items():
        regex = '|'.join(kws)
        df[topic] = df['Body'].str.contains(regex, case=False, na=False)

    # Top-N per topic
    results = {}
    for topic in topics:
        df_t = df[df[topic]].sort_values('Date', ascending=False).head(num)
        results[topic] = df_t

    return results

# Parse .docx transcript
def parse_transcript(path, keywords):
    if path.lower().endswith('.docx'):
        doc = Document(path)
        lines = [p.text.strip() for p in doc.paragraphs if any(kw.lower() in p.text.lower() for kw in keywords)]
    else:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if any(kw.lower() in line.lower() for kw in keywords)]
    return lines

# Main entry
def main_interactive():
    print("\nWelcome to the TOMAG Toolkit!\n")
    mode = input("Select mode (1=Email Snippets, 2=Transcript Scan): ").strip()
    if mode == '1':
        folder = input("Email folder path: ").strip()
        tp = input("Topics (name:kw1,kw2;...): ").strip()
        topics = {pair.split(':')[0].strip(): [k.strip() for k in pair.split(':')[1].split(',')] for pair in tp.split(';')}
        num = int(input("Top N emails per topic: ").strip())
        res = parse_emails(folder, topics, num)
        for name, df in res.items():
            csv_dir = os.path.join(folder, 'csv')
            os.makedirs(csv_dir, exist_ok=True)
            out = os.path.join(csv_dir, f'snippets_{name}.csv')
            df.to_csv(out, index=False)
            print(f"Wrote {len(df)} rows to {out}")
            print(f"Wrote {len(df)} rows to {out}")
    elif mode == '2':
        path = input("Transcript file path: ").strip()
        kws = [k.strip() for k in input("Keywords (comma-separated): ").split(',')]
        lines = parse_transcript(path, kws)
        out = os.path.splitext(path)[0] + '_excerpts.txt'
        with open(out, 'w', encoding='utf-8') as f:
            for line in lines:
                f.write(line + '\n')
        print(f"Extracted {len(lines)} lines to {out}")
    else:
        print("Invalid selection. Exiting.")
        sys.exit(1)

def main_headless(config_file):
    cfg = yaml.safe_load(open(config_file))
    if 'email_snippets' in cfg:
        e = cfg['email_snippets']
        res = parse_emails(e['folder'], e['topics'], e['num'])
        for t, df in res.items():
            out = os.path.join(e['folder'], f'snippets_{t}.csv')
            df.to_csv(out, index=False)
            logging.info(f"Wrote {len(df)} rows to {out}")
    if 'transcript_scan' in cfg:
        t = cfg['transcript_scan']
        lines = parse_transcript(t['file'], t['keywords'])
        out = t['file'].replace('.docx','_excerpts.txt')
        with open(out, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        logging.info(f"Extracted {len(lines)} lines to {out}")

if __name__ == '__main__':
    setup_logging()
    parser = argparse.ArgumentParser(description='TOMAG Toolkit')
    parser.add_argument('--config', help='Path to config.yaml for headless mode')
    args = parser.parse_args()

    if args.config:
        main_headless(args.config)
    else:
        main_interactive()