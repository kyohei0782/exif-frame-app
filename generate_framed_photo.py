import subprocess
import json
import os
from PIL import Image, ImageDraw, ImageFont

# 対象の画像ファイル（とりあえず1枚で試す）
input_path = "DSCF8426.JPG"
# 出力するファイル名
output_path = "design_DSCF8426.JPG"

def get_exif_with_exiftool(path):
    if not os.path.exists(path):
        print(f"エラー: {path} が見つかりません。")
        return None

    try:
        # ExifToolで必要な情報を取得
        cmd = ["exiftool", "-j", "-FilmMode", "-Model", "-FNumber", "-ExposureTime", "-ISO", path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)[0]
    except Exception as e:
        print(f"Exif取得エラー: {e}")
        return None

# --- プリセット関数 1：チェキ風（ポラロイド型） ---
def preset_polaroid(img_path, output_path, exif_data):
    if not exif_data:
        return

    # 1. 元画像を開く
    img = Image.open(img_path)
    # JPEGの回転情報を反映させて正しい向きにする
    if hasattr(img, '_getexif') and img._getexif():
        from PIL import ImageOps
        img = ImageOps.exif_transpose(img)
    
    w, h = img.size

    # 2. デザインの計算（キャンバスサイズ）
    # 元画像の15%を上の余白、20%を下、10%を左右にする
    top_margin = int(h * 0.1)
    bottom_margin = int(h * 0.25)
    side_margin = int(w * 0.1)

    canvas_w = w + (side_margin * 2)
    canvas_h = h + top_margin + bottom_margin

    # 3. 白いキャンバスを作成（【背景・フレーム効果】紙背景の基礎）
    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))

    # 4. 元画像を貼り付ける（【写真へのボーダー追加】白いキャンバスの上に置くことで実現）
    canvas.paste(img, (side_margin, top_margin))

    # 5. 文字の描画準備
    draw = ImageDraw.Draw(canvas)
    
    # フォント設定（Mac標準の等幅フォント Courier を使用。オシャレ）
    # サイズはキャンバスの高さに合わせて自動調整
    font_size = int(canvas_h * 0.035) 
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # 6. EXIF情報を整形（【レイアウト調整】）
    film = exif_data.get("FilmMode", "STD").upper()
    f_num = f"f/{exif_data.get('FNumber', '??')}"
    ss = exif_data.get('ExposureTime', '??')
    iso = f"ISO {exif_data.get('ISO', '??')}"
    model = exif_data.get("Model", "X100VI").upper()

    # 表示する文字列のリスト
    text_lines = [
        f"SHOT ON {model}",
        f"{film} // {f_num} // {ss} // {iso}"
    ]

    # 7. 文字を下の余白に描画（【文字のデザイン・サイズ・色の自由変更】）
    # 中央揃えにするための計算
    y_text = h + top_margin + int(bottom_margin * 0.2)
    
    for line in text_lines:
        # textbbox で文字列の幅を取得 (Pillow 10以上)
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        text_w = right - left
        text_h = bottom - top
        
        # キャンバスの中央に配置
        x_text = (canvas_w - text_w) // 2
        
        # 黒い文字で描画
        draw.text((x_text, y_text), line, font=font, fill=(0, 0, 0))
        y_text += text_h * 1.5 # 行間を空ける

    # 8. 保存（【プリセット機能】）
    canvas.save(output_path, quality=95)
    print(f"\n✅ チェキ風画像を作成しました: {output_path}")

if __name__ == "__main__":
    # Exif情報を取得
    print(f"{input_path} のExif情報を解析中...")
    exif = get_exif_with_exiftool(input_path)
    
    if exif:
        # チェキ風プリセットを実行
        print(f"デザイン加工を適用中...")
        preset_polaroid(input_path, output_path, exif)
