import streamlit as st
from paddleocr import PaddleOCR
import cv2
import numpy as np
from PIL import Image
import pdf2image
import pandas as pd
import io

# Cấu hình trang
st.set_page_config(page_title="BoQ Wire Matching Tool", layout="wide")
st.title("⚡ Công cụ trích xuất BoQ Dây Điện")
st.write("Tải lên bản scan hoặc PDF để chuyển thành Excel")

# Khởi tạo OCR
@st.cache_resource
def load_ocr():
    return PaddleOCR(use_angle_cls=True, lang='vi', show_log=False)

ocr = load_ocr()

def process_and_filter(img):
    img_array = np.array(img)
    img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    result = ocr.ocr(img_cv, cls=True)
    
    extracted_rows = []
    if result and result[0]:
        for line in result[0]:
            text = line[1][0] # Lấy nội dung chữ
            # Lọc các từ khóa liên quan đến dây điện
            keywords = ['dây', 'cáp', 'cu/', 'pvc', 'mm2', 'x', 'x1', 'x2', 'x4', 'x6']
            if any(key in text.lower() for key in keywords):
                extracted_rows.append(text)
    return extracted_rows

uploaded_file = st.file_uploader("Chọn file BoQ (PDF, JPG, PNG)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    all_data = []
    
    with st.status("Đang xử lý dữ liệu... vui lòng đợi trong giây lát", expanded=True) as status:
        # Chuyển PDF/Ảnh thành danh sách ảnh
        if uploaded_file.type == "application/pdf":
            images = pdf2image.convert_from_bytes(uploaded_file.read())
        else:
            images = [Image.open(uploaded_file)]
        
        # Chạy OCR từng trang
        for i, img in enumerate(images):
            st.write(f"Đang quét trang {i+1}...")
            rows = process_and_filter(img)
            all_data.extend(rows)
        status.update(label="Đã quét xong!", state="complete", expanded=False)

    if all_data:
        # Tạo bảng dữ liệu
        df = pd.DataFrame(all_data, columns=["Nội dung trích xuất (Dây điện)"])
        st.subheader("Kết quả tạm tính")
        st.dataframe(df, use_container_width=True)

        # Chuyển dữ liệu sang Excel để tải về
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='BoQ_Day_Dien')
        
        st.download_button(
            label="📥 Tải file Excel kết quả",
            data=buffer.getvalue(),
            file_name="BoQ_Extract_Result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Không tìm thấy dòng nào chứa từ khóa dây điện. Hãy thử file rõ nét hơn.")

