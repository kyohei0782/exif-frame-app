import streamlit as st
import subprocess
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import io

# --- ページの設定 ---
st.set_page_config(page_title="My Photo Frame App", layout="centered")
st.title("📷 シネマティック Exif フレーム作成")

# --- Exif取得関数 ---
def get_exif_with_exiftool(path):
    try:
        cmd = ["exiftool", "-j", "-FilmMode", "-Model", "-FNumber", "-ExposureTime", "-ISO", path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)[0]
    except:
        return None

def format_exif_text(exif_data):
    if not exif_data:
        return ["SHOT ON ??", "?? // f/?? // ?? // ISO ??"]
    film = exif_data.get("FilmMode", "STD").upper()
    f_num = f"f/{exif_data.get('FNumber', '??')}"
    ss = exif_data.get('ExposureTime', '??')
    iso = f"ISO {exif_data.get('ISO', '??')}"
    model = exif_data.get("Model", "CAMERA").upper()
    return [f"SHOT ON {model}", f"{film} // {f_num} // {ss} // {iso}"]

def get_font(canvas_h):
    font_size = int(canvas_h * 0.03) 
    try:
        # おすすめNo.1の DIN Alternate Bold を使用
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf", font_size)
    except:
        return ImageFont.load_default()

def draw_text_centered(draw, canvas_w, y_start, text_lines, font):
    y = y_start
    for line in text_lines:
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        text_w = right - left
        text_h = bottom - top
        x = (canvas_w - text_w) // 2
        draw.text((x, y), line, font=font, fill=(30, 30, 30)) # 少し柔らかい黒
        y += text_h * 1.5

# --- プリセット処理（Streamlit用に「保存」ではなく「画像を返す」ように変更） ---
def preset_polaroid(img, exif_text):
    w, h = img.size
    top_margin, bottom_margin, side_margin = int(h * 0.1), int(h * 0.25), int(w * 0.1)
    canvas_w, canvas_h = w + (side_margin * 2), h + top_margin + bottom_margin
    canvas = Image.new("RGB", (canvas_w, canvas_h), (250, 250, 250)) # 少しオフホワイト
    canvas.paste(img, (side_margin, top_margin))
    draw = ImageDraw.Draw(canvas)
    y_text = h + top_margin + int(bottom_margin * 0.2)
    draw_text_centered(draw, canvas_w, y_text, exif_text, get_font(canvas_h))
    return canvas

def preset_background_blur(img, exif_text):
    w, h = img.size
    margin_w, margin_h = int(w * 0.1), int(h * 0.15)
    canvas_w, canvas_h = w + (margin_w * 2), h + margin_h + int(h * 0.2)
    bg = img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=60))
    bg.paste(img, (margin_w, margin_h))
    draw = ImageDraw.Draw(bg)
    y_text = h + margin_h + int(h * 0.05)
    
    # ブラーの時は文字を白にするため、ここだけ個別に描画
    font = get_font(canvas_h)
    y = y_text
    for line in exif_text:
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
        x = (canvas_w - (right - left)) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += (bottom - top) * 1.5
    return bg

# --- アプリの画面UI ---
# 画像アップローダー
uploaded_file = st.file_uploader("X100VIなどの写真をアップロードしてください、enjoy! (JPG)", type=['jpg', 'jpeg'])

if uploaded_file is not None:
    # 1. 一時的に画像を保存してExifToolで読み込めるようにする
    temp_path = "temp_upload.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 2. Exif情報を取得
    exif_data = get_exif_with_exiftool(temp_path)
    exif_text = format_exif_text(exif_data)

    # 3. 画面のレイアウト（2カラム）
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ 設定")
        # プリセットの選択プルダウン
        preset_choice = st.selectbox("デザインプリセットを選択", ["チェキ風 (Polaroid)", "背景ブラー (Blur)"])
        
        # 取得したデータをこっそり表示
        st.write("▼ 検出されたデータ")
        for line in exif_text:
            st.caption(line)

    with col2:
        st.subheader("✨ プレビュー")
        # 元画像を開く
        img = Image.open(temp_path)
        if hasattr(img, '_getexif') and img._getexif():
            img = ImageOps.exif_transpose(img)

        # 選択されたプリセットを適用
        with st.spinner('画像を処理中...'):
            if preset_choice == "チェキ風 (Polaroid)":
                result_img = preset_polaroid(img, exif_text)
            else:
                result_img = preset_background_blur(img, exif_text)

        # 画面に表示
        st.image(result_img, width='stretch')

        # ダウンロード用に画像を変換
        buf = io.BytesIO()
        result_img.save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()

        # ダウンロードボタン
        st.download_button(
            label="📥 この画像を保存する",
            data=byte_im,
            file_name=f"processed_{uploaded_file.name}",
            mime="image/jpeg"
        )

# 適当な行に追加
st.write("Current Device: Fujifilm X100VI")