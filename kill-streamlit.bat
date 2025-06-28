@echo off 
echo Killing Streamlit processes... 
for /f "tokens=5" %%%%a in ('netstat -ano ^| findstr :8501') do ( 
    taskkill /PID %%%%a /F 2>nul 
) 
echo Done! 
