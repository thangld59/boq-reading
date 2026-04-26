import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, ImageOps, ImageEnhance
import io

st.set_page_config(page_title="BoQ Pro Extractor", layout="wide")
st.title("⚡ BoQ Wire Extractor - Phiên bản Chia Cột")

def preprocess_image(image):
    # Chuyển sang ảnh xám và tăng độ tương phản để không sót chữ
    image = ImageOps.grayscale(image)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    return image

def extract_to_columns(text_line):
    # Thay thế các ký tự ngăn cách phổ biến thành dấu '|' để dễ tách
    line = text_line.replace('!', '|').replace('_', '|')
    # Tách dòng thành các phần dựa trên dấu '|'
    parts = [p.strip() for p in line.split('|') if p.strip()]
    return parts

uploaded_file = st.file_uploader("Tải lên BoQ (Ảnh hoặc PDF)", type=["pdf", "png", "jpg"])

if uploaded_file:
    all_rows = []
    with st.spinner("Đang phân tích cấu trúc bảng..."):
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.read())
        else:
            images = [Image.open(uploaded_file)]
        
        for img in images:
            processed_img = preprocess_image(img)
            # Dùng cấu hình psm 6 (Giả định ảnh là một khối văn bản dạng bảng)
            custom_config = r'--oem 3 --psm 6'
            raw_text = pytesseract.image_to_string(processed_img, lang='vie', config=custom_config)
            
            for line in raw_text.split('\n'):
                if any(k in line.lower() for k in ['dây', 'cáp', 'cu/', 'pvc', 'mm2']):
                    column_data = extract_to_columns(line)
                    if len(column_data) > 1: # Chỉ lấy dòng có nhiều thông tin
                        all_rows.append(column_data)

    if all_rows:
        # Tìm số cột lớn nhất để tạo bảng không bị lệch
        max_cols = max(len(row) for row in all_rows)
        headers = [f"Cột {i+1}" for i in range(max_cols)]
        
        df = pd.DataFrame(all_rows, columns=headers[:max_cols])
        
        st.subheader("Kết quả đã phân tách:")
        st.dataframe(df, use_container_width=True)
        
        # Xuất Excel
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button(label="📥 Tải Excel đã chia cột", data=towrite.getvalue(), file_name="BoQ_Pro.xlsx")
    else:
        st.error("Không tìm thấy dữ liệu. Hãy thử file có độ phân giải cao hơn.")
