import subprocess
import json
import os
import csv

def create_csv():
    # フォルダ内のJPGファイルを再取得
    files = [f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.jpeg', '.JPG', '.JPEG'))]
    
    if not files:
        print("エラー: 写真が見つかりません。")
        return

    with open('metadata_import.csv', 'w', newline='', encoding='utf-8') as csvfile:
        # Resolveが最も認識しやすい「File Name」と「Description」
        fieldnames = ['File Name', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for file in files:
            try:
                # パスを含まない「ファイル名のみ」を取得
                pure_name = os.path.basename(file)
                
                cmd = ["exiftool", "-j", "-FilmMode", "-FNumber", "-ExposureTime", "-ISO", file]
                result = subprocess.run(cmd, capture_output=True, text=True)
                data = json.loads(result.stdout)[0]

                film = data.get("FilmMode", "STD").upper()
                f_val = f"f/{data.get('FNumber', '??')}"
                ss = data.get('ExposureTime', '??')
                iso = f"ISO {data.get('ISO', '??')}"
                
                info_text = f"{film}  |  {f_val}  |  {ss}  |  {iso}"
                
                writer.writerow({'File Name': pure_name, 'Description': info_text})
                print(f"解析中: {pure_name}")
            except Exception as e:
                print(f"エラー: {e}")

    print("\n✅ 最新の 'metadata_import.csv' を作成しました。")

if __name__ == "__main__":
    create_csv()
