#!/usr/bin/env python3
"""
Generate markdown rows from snippet CSVs.
"""
import os
import glob
import pandas as pd
import argparse
import sys
from datetime import datetime

# Setup logging
date = datetime.fromisoformat(str(row['Date'])).date().isoformat()


# Force stdout to UTF-8 so emojis & non-ASCII symbols won’t error out
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Validate CSV folder exists
def validate_csv_folder(path):
    if not os.path.isdir(path):
        raise FileNotFoundError(f"CSV folder not found: {path}")

# Generate markdown rows
def generate_rows(csv_folder):
    validate_csv_folder(csv_folder)
    for path in glob.glob(os.path.join(csv_folder, 'snippets_*.csv')):
        topic = os.path.basename(path).split('snippets_')[1].rsplit('.csv',1)[0]
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            date = str(row['Date'])[:10]
            sender = row.get('From', '')
            subj = row.get('Subject', '')
            snippet = row.get('Body', '').splitlines()[:2]
            excerpt = (
                f"**[{date}]** / **{sender}** / “{subj}”<br>“{' '.join(snippet)}”"
            )
            print(f"| {excerpt} | [thinking] on {topic} |")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate markdown rows from CSVs')
    parser.add_argument('-c','--csv', default='./csv', help='CSV folder')
    args = parser.parse_args()
    generate_rows(args.csv)