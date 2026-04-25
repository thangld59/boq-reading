import streamlit as st
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io

st.title("⚡ BoQ Wire Extractor (Lite)")

# Hàm xử lý OCR
def extract_wire_data(image):
    # Chuyển ảnh sang dạng đen trắng để AI đọc tốt hơn
    text = pytesseract.image_to_string(image, lang='vie')
    lines = text.split('\n')
    
    # Lọc từ khóa dây điện
    keywords = ['dây', 'cáp', 'cu/', 'pvc', 'mm2', 'x1', 'x2', 'x4', 'x6']
    filtered = [l.strip() for l in lines if any(k in l.lower() for k in keywords) and len(l.strip()) > 5]
    return filtered

uploaded_file = st.file_uploader("Tải lên file BoQ", type=["pdf", "png", "jpg"])

if uploaded_file:
    results = []
    with st.spinner("Đang xử lý..."):
        if uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.read())
        else:
            images = [Image.open(uploaded_file)]
        
        for img in images:
            data = extract_wire_data(img)
            results.extend(data)

    if results:
        df = pd.DataFrame(results, columns=["Dữ liệu dây điện"])
        st.table(df)
        
        # Xuất Excel
        towrite = io.BytesIO()
        df.to_excel(towrite, index=False, header=True)
        st.download_button(label="📥 Tải Excel", data=towrite.getvalue(), file_name="BoQ.xlsx")
    else:
        st.info("Chưa tìm thấy dữ liệu. Hãy thử file rõ nét hơn.")
