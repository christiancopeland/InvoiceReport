import streamlit as st # data app development
import subprocess # process in the os
from subprocess import STDOUT, check_call #os process manipuation
import os #os process manipuation
import base64 # byte object into a pdf file 
import tabula.io as tb
import convertapi
import numpy as np
convertapi.api_secret = 'ySP84j1dHZ0L4j3w'

st.title("PDF Table Extractor dashboard thing")

# file uploader on streamlit 

input_pdf = st.file_uploader(label = "upload your pdf here", type = 'pdf')

st.markdown("### Page Number")

page_number = st.text_input("Enter the page # from where you want to extract the PDF eg: 3", value = 1)

# run this only when a PDF is uploaded
if input_pdf is not None:
    'Please Wait'
    with open("input.pdf", "wb") as f:
        base64_pdf = base64.b64encode(input_pdf.read()).decode('utf-8')
        f.write(base64.b64decode(base64_pdf))
    f.close()
    convertapi.convert('ocr', {
    'File': 'input.pdf'
    }, 
    from_format = 'pdf').save_files(r'C:\Users\hp\Desktop\pythonProject\InvoiceReport\streamlit')
    tables = tb.read_pdf('input.pdf', pages=page_number)
    
    st.write(tables)