import sys
import os
import re
import urllib.parse
import pandas as pd

def parse_m3u(file_path):
    channels = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
            try:
                next_line = lines[i + 1].strip()
            except IndexError:
                print(f"[WARNING] Missing URL for line: {line}")
                continue

            match = re.search(r'tvg-id="(.*?)".*?tvg-name="(.*?)".*?tvg-logo="(.*?)".*?group-title="(.*?)",(.*)', line)
            if match:
                tvg_id, tvg_name, logo, group, display_name = match.groups()
            else:
                print(f"[WARNING] Could not parse EXTINF line: {line}")
                continue

            if not (tvg_name and display_name and next_line):
                print(f"[WARNING] Missing critical fields in line: {line}")
                group = "UNKNOWN"

            channels.append({
                "tvg-id": tvg_id.strip(),
                "tvg-name": tvg_name.strip(),
                "tvg-logo": logo.strip(),
                "group-title": group.strip() if group else "UNKNOWN",
                "display-name": display_name.strip(),
                "url": next_line.strip()
            })

    return pd.DataFrame(channels)

def extract_country_prefix(tvg_name):
    match = re.match(r'^([A-Z]{2,4})\|', tvg_name.strip(), re.IGNORECASE)
    return match.group(1).upper() if match else "OTHER"

def generate_dreambox_line(index, row):
    sid = 260 + index * 2
    serviceref = f"1:0:1:{sid:X}:0:0:0:0:0:0:{urllib.parse.quote(row['url'], safe='')}"
    return f"#SERVICE {serviceref}:{row['display-name']}\n#DESCRIPTION {row['display-name']}"

def export_all_dreambox_files(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    df['prefix'] = df['tvg-name'].apply(extract_country_prefix)
    df['prefix'] = df['prefix'].fillna('OTHER')

    counts = {}

    for country, group_df in df.groupby('prefix'):
        safe_country = re.sub(r'[^A-Za-z0-9]+', '', country)
        output_path = os.path.join(output_dir, f"userbouquet.{safe_country}.tv")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"#NAME {safe_country}\n")
            for i, row in group_df.reset_index(drop=True).iterrows():
                try:
                    line = generate_dreambox_line(i, row)
                    f.write(f"{line}\n")
                except Exception as e:
                    print(f"[ERROR] Failed writing channel: {row['display-name']} - {e}")

        count = len(group_df)
        counts[safe_country] = count
        print(f"[OK] {count} channels written to {output_path}")

    total = sum(counts.values())
    print(f"[SUMMARY] Total processed: {total} entries in {len(counts)} groups.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python m3utodream.py <input.m3u> <output_dir>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"[ERROR] File not found: {input_file}")
        sys.exit(1)

    df = parse_m3u(input_file)
    if df.empty:
        print("[ERROR] No valid channels found.")
        sys.exit(1)

    export_all_dreambox_files(df, output_dir)

if __name__ == "__main__":
    main()
