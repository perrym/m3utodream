import sys
import os
#PAM 2025

def convert_m3u_to_userbouquet(m3u_file_path, output_file_path):
    if not os.path.isfile(m3u_file_path):
        print(f'Fout: Het bestand {m3u_file_path} bestaat niet.')
        return

    try:
        with open(m3u_file_path, 'r', encoding='utf-8') as m3u_file:
            lines = m3u_file.readlines()

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write('#NAME IPTV\n')
            channel_name = 'Onbekend Kanaal'
            for line in lines:
                line = line.strip()
                if line.startswith('#EXTINF:'):
                    channel_name = line.split(',')[-1]
                elif line.startswith('http'):
                    url_encoded = line.replace(':', '%3a').replace('/', '%2f')
                    output_file.write(f'#SERVICE 1:0:1:0:0:0:0:0:0:0:{url_encoded}\n')
                    output_file.write(f'#DESCRIPTION {channel_name}\n')
        print(f'Conversie voltooid! Het bestand is opgeslagen als: {output_file_path}')
    except Exception as e:
        print(f'Fout tijdens conversie: {e}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Gebruik: python m3u_to_dreambox_converter.py [pad naar M3U-bestand] [pad naar uitvoerbestand]')
    else:
        convert_m3u_to_userbouquet(sys.argv[1], sys.argv[2])
