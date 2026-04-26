import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, ImageOps, ImageEnhance
import io
import re

st.set_page_config(page_title="BoQ Wire Pro", layout="wide")
st.title("⚡ Trích xuất BoQ Dây Điện - Bản Chính Xác Cao")

def clean_and_split(line):
    # Quy trình tách cột thông minh dựa trên khoảng trắng lớn hoặc dấu gạch
    parts = re.split(r'\s{2,}|[|!]', line)
    parts = [p.strip() for p in parts if p.strip()]
    return parts

def extract_logic(text):
    rows = []
    lines = text.split('\n')
    for line in lines:
        # Tìm các dòng có chứa tiết diện (sqmm hoặc mm2) hoặc từ khóa dây/cáp
        if re.search(r'(sqmm|mm2|cu/|pvc|cáp|dây)', line, re.IGNORECASE):
            data = clean_and_split(line)
            # Một dòng BoQ chuẩn thường có ít nhất 4 thông tin (STT, Tên, ĐVT, SL)
            if len(data) >= 3:
                rows.append(data)
    return rows

uploaded_file = st.file_uploader("Tải lên file báo giá", type=["pdf", "png", "jpg"])

if uploaded_file:
    all_results = []
    with st.spinner("Đang quét dữ liệu chuyên sâu..."):
        if uploaded_file.type == "application/pdf":
            # PDF gốc quét sẽ cực nhanh và chính xác
            images = convert_from_bytes(uploaded_file.read(), dpi=300)
        else:
            images = [Image.open(uploaded_file)]
        
        for img in images:
            # Tiền xử lý để AI đọc không sót hàng đầu
            img = ImageOps.grayscale(img)
            img = ImageEnhance.Contrast(img).enhance(2.5)
            
            # Quét với chế độ ưu tiên bảng biểu
            raw_text = pytesseract.image_to_string(img, lang='vie', config='--psm 6')
            all_results.extend(extract_logic(raw_text))

    if all_results:
        # Chuẩn hóa số cột
        df = pd.DataFrame(all_results)
        
        # Đặt tên cột tạm thời để người dùng dễ nhìn
        st.subheader("Dữ liệu đã trích xuất:")
        st.dataframe(df, use_container_width=True)
        
        # Xuất Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
        
        st.download_button(label="📥 Tải Excel kết quả", data=output.getvalue(), file_name="BoQ_Chuan_Hoa.xlsx")
    else:
        st.warning("Không tìm thấy dữ liệu. Hãy thử file có độ phân giải cao hơn.")
