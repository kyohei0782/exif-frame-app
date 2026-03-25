import subprocess
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

def get_exif_with_exiftool(path):
    try:
        cmd = ["exiftool", "-j", "-FilmMode", "-Model", "-FNumber", "-ExposureTime", "-ISO", path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)[0]
    except Exception as e:
        print(f"Exif取得エラー ({path}): {e}")
        return None

def format_exif_text(exif_data):
    if not exif_data:
        return ["SHOT ON ??", "?? // f/?? // ?? // ISO ??"]
    film = exif_data.get("FilmMode", "STD").upper()
    f_num = f"f/{exif_data.get('FNumber', '??')}"
    ss = exif_data.get('ExposureTime', '??')
    iso = f"ISO {exif_data.get('ISO', '??')}"
    model = exif_data.get("Model", "X100VI").upper()
    return [f"SHOT ON {model}", f"{film} // {f_num} // {ss} // {iso}"]

def get_font(canvas_h, color):
    font_size = int(canvas_h * 0.03) 
    try:
        # Mac標準の Courier New.ttf
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Courier New.ttf", font_size)
    except:
        return ImageFont.load_default()

def draw_text_centered(draw, canvas_w, y_start, text_lines, font, color):
    y = y_start
    for line in text_lines:
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        text_w = right - left
        text_h = bottom - top
        x = (canvas_w - text_w) // 2
        draw.text((x, y), line, font=font, fill=color)
        y += text_h * 1.5

# --- プリセット 1：チェキ風（ポラロイド型） ---
def preset_polaroid(img, exif_text, output_path):
    w, h = img.size
    top_margin = int(h * 0.1)
    bottom_margin = int(h * 0.25)
    side_margin = int(w * 0.1)
    canvas_w = w + (side_margin * 2)
    canvas_h = h + top_margin + bottom_margin
    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
    canvas.paste(img, (side_margin, top_margin))
    draw = ImageDraw.Draw(canvas)
    font = get_font(canvas_h, (0, 0, 0))
    y_text = h + top_margin + int(bottom_margin * 0.2)
    draw_text_centered(draw, canvas_w, y_text, exif_text, font, (0, 0, 0))
    canvas.save(output_path, quality=95)

# --- プリセット 2：背景ブラー ---
def preset_background_blur(img, exif_text, output_path):
    w, h = img.size
    # キャンバスサイズを元画像より少し大きくする（余白用）
    margin_w = int(w * 0.1)
    margin_h = int(h * 0.15)
    canvas_w = w + (margin_w * 2)
    canvas_h = h + margin_h + int(h * 0.2) # 下の文字用余白を多めに

    # 背景ブラー画像を作成
    bg = img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=50))
    
    # 元画像を中央に貼り付ける
    bg.paste(img, (margin_w, margin_h))
    
    # 文字を描画
    draw = ImageDraw.Draw(bg)
    font = get_font(canvas_h, (255, 255, 255))
    y_text = h + margin_h + int(h * 0.05)
    draw_text_centered(draw, canvas_w, y_text, exif_text, font, (255, 255, 255))
    bg.save(output_path, quality=95)

# --- プリセット 3：ドロップシャドウ（白い余白付き） ---
def preset_shadow(img, exif_text, output_path):
    w, h = img.size
    margin = int(min(w, h) * 0.1)
    canvas_w = w + (margin * 2)
    canvas_h = h + (margin * 2) + int(h * 0.15) # 下の文字用余白

    # 白いキャンバス
    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))

    # 影を作成
    shadow_offset = int(min(w, h) * 0.02)
    shadow_blur = int(min(w, h) * 0.03)
    # 影用のキャンバス（少し大きくしてぼかし用）
    shadow_canvas = Image.new("RGBA", (w + shadow_blur * 2, h + shadow_blur * 2), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_canvas)
    # 影を描画（黒い矩形）
    shadow_draw.rectangle([shadow_blur, shadow_blur, w + shadow_blur, h + shadow_blur], fill=(0, 0, 0, 100))
    shadow_canvas = shadow_canvas.filter(ImageFilter.GaussianBlur(shadow_blur))
    
    # キャンバスに影を貼り付ける
    canvas.paste(shadow_canvas, (margin - shadow_blur + shadow_offset, margin - shadow_blur + shadow_offset), shadow_canvas)

    # 元画像を貼り付ける
    canvas.paste(img, (margin, margin))

    # 文字を描画
    draw = ImageDraw.Draw(canvas)
    font = get_font(canvas_h, (0, 0, 0))
    y_text = h + (margin * 2)
    draw_text_centered(draw, canvas_w, y_text, exif_text, font, (0, 0, 0))
    canvas.save(output_path, quality=95)

def process_all_photos():
    # フォルダ内のJPGファイルをリストアップ
    files = [f for f in os.listdir('.') if f.lower().endswith(('.jpg', '.jpeg')) and not f.startswith(('polaroid_', 'blur_', 'shadow_'))]
    
    if not files:
        print("JPGファイルが見つかりません。")
        return

    print(f"合計 {len(files)} 枚の写真を解析＆加工中...")

    for file in files:
        try:
            exif = get_exif_with_exiftool(file)
            exif_text = format_exif_text(exif)

            # 元画像を開き、向きを修正
            img = Image.open(file)
            if hasattr(img, '_getexif') and img._getexif():
                img = ImageOps.exif_transpose(img)

            # 各プリセットを実行
            preset_polaroid(img, exif_text, f"polaroid_{file}")
            preset_background_blur(img, exif_text, f"blur_{file}")
            preset_shadow(img, exif_text, f"shadow_{file}")
            
            print(f"  [完了] {file} (3プリセット生成)")
        except Exception as e:
            print(f"  [失敗] {file}: {e}")

    print(f"\n✅ 成功！ 全ての加工済み画像が生成されました。")

if __name__ == "__main__":
    process_all_photos()
