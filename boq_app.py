import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
import pdf2image
import pandas as pd
import io

st.set_page_config(page_title="BoQ Wire Matching Tool", layout="wide")
st.title("⚡ Công cụ trích xuất BoQ Dây Điện (Bản ổn định)")

# Khởi tạo EasyOCR cho tiếng Việt và tiếng Anh
@st.cache_resource
def load_reader():
    return easyocr.Reader(['vi', 'en'])

reader = load_reader()

def process_and_filter(img):
    img_array = np.array(img)
    # Nhận diện chữ
    results = reader.readtext(img_array)
    
    extracted_rows = []
    keywords = ['dây', 'cáp', 'cu/', 'pvc', 'mm2', 'x1', 'x2', 'x4', 'x6']
    
    for (bbox, text, prob) in results:
        if any(key in text.lower() for key in keywords):
            extracted_rows.append(text)
    return extracted_rows

uploaded_file = st.file_uploader("Chọn file BoQ (PDF, JPG, PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    all_data = []
    with st.status("Đang đọc dữ liệu... lần đầu có thể mất 1-2 phút", expanded=True) as status:
        if uploaded_file.type == "application/pdf":
            # Cần lưu ý: Nếu file PDF nhiều trang, chỉ nên thử 1-2 trang đầu trước
            images = pdf2image.convert_from_bytes(uploaded_file.read())
        else:
            images = [Image.open(uploaded_file)]
        
        for i, img in enumerate(images):
            st.write(f"Đang xử lý trang {i+1}...")
            rows = process_and_filter(img)
            all_data.extend(rows)
        status.update(label="Hoàn thành!", state="complete", expanded=False)

    if all_data:
        df = pd.DataFrame(all_data, columns=["Dòng dữ liệu dây điện tìm thấy"])
        st.dataframe(df, use_container_width=True)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Tải file Excel kết quả",
            data=buffer.getvalue(),
            file_name="BoQ_Day_Dien.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Không tìm thấy dữ liệu dây điện hoặc file cần rõ nét hơn.")
