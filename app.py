
import streamlit as st
import pandas as pd
import io
from timetable_engine import generate_timetables

st.title("📘 School Timetable Generator")
st.write("Upload your Excel file in the specified format to generate class-wise and teacher-wise timetables.")

uploaded_file = st.file_uploader("Upload Excel File (e.g., Format A.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    if st.button("Generate Timetable"):
        unified, classwise, teacherwise = generate_timetables(uploaded_file)

        # Write to a BytesIO stream
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            unified.to_excel(writer, index=False, sheet_name="Unified Timetable")
            for cls, df in classwise.items():
                df.to_excel(writer, index=True, sheet_name=f"Class_{cls[:20]}")
            for i, (teacher, df) in enumerate(teacherwise.items()):
                df.to_excel(writer, index=True, sheet_name=f"Teacher_{i+1}")

        st.success("✅ Timetable Generated!")
        st.download_button(
            label="📥 Download Excel File",
            data=output.getvalue(),
            file_name="Generated_Timetable.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
