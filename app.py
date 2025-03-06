import streamlit as st
import pandas as pd
import os
import io
from io import BytesIO
import PyPDF2
from PIL import Image
import docx
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Set Streamlit page config
st.set_page_config(page_title="📀 Data Sweeper Pro", layout='wide')
st.title("📀 Data Sweeper Pro")
st.write("Convert, clean, and visualize your data with ease!")

# File Upload
uploaded_files = st.file_uploader("Upload Files (CSV, Excel, PDF, Word, Images):", 
                                  type=["csv", "xlsx", "pdf", "docx", "jpg", "png"], 
                                  accept_multiple_files=True)

processing_status = []

# Process each file
for file in uploaded_files:
    file_ext = os.path.splitext(file.name)[-1].lower()
    
    try:
        if file_ext in [".csv", ".xlsx"]:
            df = pd.read_csv(file) if file_ext == ".csv" else pd.read_excel(file, engine="openpyxl")
            df.dropna(how='all', inplace=True)
            st.write(f"**File Name:** {file.name}")
            st.write(f"**File Size:** {file.size/1024:.2f} KB")
            st.dataframe(df.head())
            
            # Data Cleaning Options
            st.subheader("🛠️ Data Cleaning")
            cleaning_option = st.selectbox(f"Select cleaning option for {file.name}", 
                                           ["None", "Remove Duplicates", "Fill Missing Values"])
            if cleaning_option == "Remove Duplicates":
                df.drop_duplicates(inplace=True)
                st.write("✅ Duplicates Removed!")
            elif cleaning_option == "Fill Missing Values":
                df.fillna(method='ffill', inplace=True)
                st.write("✅ Missing Values Filled!")
            
            # Visualization
            st.subheader("📊 Data Visualization")
            chart_type = st.selectbox(f"Choose chart for {file.name}", 
                                      ["None", "Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])
            
            if chart_type != "None":
                col_x, col_y = st.columns(2)
                x_axis = col_x.selectbox("Select X-axis:", df.columns)
                y_axis = col_y.selectbox("Select Y-axis:", df.select_dtypes(include='number').columns)
                
                fig, ax = plt.subplots()
                if chart_type == "Bar Chart":
                    df.plot(kind='bar', x=x_axis, y=y_axis, ax=ax)
                elif chart_type == "Line Chart":
                    df.plot(kind='line', x=x_axis, y=y_axis, ax=ax)
                elif chart_type == "Pie Chart":
                    df[y_axis].value_counts().plot.pie(autopct='%1.1f%%', ax=ax)
                elif chart_type == "Scatter Plot":
                    df.plot(kind='scatter', x=x_axis, y=y_axis, ax=ax)
                st.pyplot(fig)
            
            # File Conversion
            st.subheader("🔄 Convert & Download")
            convert_to = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"])
            
            buffer = BytesIO()
            if convert_to == "CSV":
                df.to_csv(buffer, index=False)
                mime_type = "text/csv"
            else:
                df.to_excel(buffer, index=False, engine="openpyxl")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            buffer.seek(0)
            st.download_button(f"⬇️ Download {file.name} as {convert_to}", buffer, file_name=f"converted_{file.name}", mime=mime_type)
        
        elif file_ext == ".pdf":
            st.subheader("📝 PDF File Processing")
            pdf_reader = PyPDF2.PdfReader(file)
            text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
            st.text_area("Extracted Text:", text, height=300)
        
        elif file_ext == ".docx":
            st.subheader("📚 Word File Processing")
            if st.button(f"Convert {file.name} to PDF"):
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=letter)
                c.drawString(100, 750, "Converted from Word Document")
                doc = docx.Document(file)
                y_position = 730
                for para in doc.paragraphs:
                    c.drawString(100, y_position, para.text[:90])  # Avoids overflow
                    y_position -= 20
                c.save()
                buffer.seek(0)
                st.download_button("⬇️ Download as PDF", buffer, file_name=f"{file.name.replace('.docx', '.pdf')}", mime="application/pdf")
        
        elif file_ext in [".jpg", ".png"]:
            st.image(Image.open(file), caption=f"Uploaded Image: {file.name}", use_column_width=True)
            
            if st.button(f"Convert {file.name} to PDF"):
                image = Image.open(file)
                buffer = BytesIO()
                image.convert('RGB').save(buffer, format="PDF")
                buffer.seek(0)
                st.download_button("⬇️ Download as PDF", buffer, file_name=f"{file.name.replace(file_ext, '.pdf')}", mime="application/pdf")
        
        processing_status.append(f"✅ {file.name} processed successfully!")
    except Exception as e:
        processing_status.append(f"❌ Error processing {file.name}: {str(e)}")

# Show processing status
for status in processing_status:
    st.write(status)

if all("✅" in status for status in processing_status):
    st.success("🎉 All files processed successfully!")

# Footer
st.markdown("### Developed by Rizwan")