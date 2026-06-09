@echo off
cd /d "C:\Users\SOHHAM\codes\PL2_Project"
call .\.venv\Scripts\activate.bat
streamlit run Dashboard\app.py
pause