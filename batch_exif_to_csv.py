import subprocess
import json
import os
import csv

def create_resolve_csv():
    # python_work内にある全JPGファイルを対象にする
    files = [f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.jpeg'))]
    
    with open('resolve_metadata.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['File Name', 'Keywords']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for file in files:
            try:
                cmd = ["exiftool", "-j", "-FilmMode", "-FNumber", "-ExposureTime", "-ISO", file]
                result = subprocess.run(cmd, capture_output=True, text=True)
                data = json.loads(result.stdout)[0]

                film = data.get("FilmMode", "STD").upper()
                f_val = f"f/{data.get('FNumber')}"
                ss = data.get('ExposureTime')
                iso = f"ISO {data.get('ISO')}"
                
                # Resolveの画面に表示したい文字列を作成
                display_text = f"{film}  |  {f_val}  |  {ss}  |  {iso}"
                
                writer.writerow({'File Name': file, 'Keywords': display_text})
                print(f"処理完了: {file}")
            except:
                print(f"スキップ: {file}")

if __name__ == "__main__":
    create_resolve_csv()
