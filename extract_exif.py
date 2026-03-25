import subprocess
import json
import os

image_path = "DSCF8426.JPG"

def get_exif_with_exiftool(path):
    try:
        cmd = ["exiftool", "-j", "-FilmMode", "-Model", "-FNumber", "-ExposureTime", "-ISO", "-FocalLength", path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)[0]

        # デザインを意識した変数割り当て
        model = data.get("Model", "X100VI").upper()
        film = data.get("FilmMode", "STD").upper()
        f_val = f"f/{data.get('FNumber')}"
        ss = data.get('ExposureTime')
        iso = f"ISO {data.get('ISO')}"
        focal = data.get("FocalLength", "23mm")

        # 🔗 リンク先のデザインに近い、セパレーター（|）を使った並び
        # 例: FUJIFILM X100VI  //  CLASSIC NEG.  //  23MM  f/2.0  1/500  ISO 125
        line1 = f"{model}  //  {film}"
        line2 = f"{focal}   {f_val}   {ss}   {iso}"
        display_full = f"{line1}\n{line2}"

        print(f"\n✨ デザイン確認用表示:\n")
        print(display_full)

        with open("exif_data.srt", "w", encoding="utf-8") as f:
            f.write(f"1\n00:00:00,000 --> 00:00:05,000\n{display_full}\n")
        
        print(f"\n📂 'exif_data.srt' を更新しました。")

    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    get_exif_with_exiftool(image_path)
