# Q2Validate Usage Guide

**Quick Reference for Running q2validate**

## Running q2validate

### Standard Startup Process
```powershell
# 1. Navigate to q2validate directory
cd C:\Users\aknoesen\Documents\Knoesen\q2validate

# 2. Activate virtual environment (you'll see (venv) in prompt)
.\venv\Scripts\Activate.ps1

# 3. Run q2validate
streamlit run q2validate.py
```

### Expected Output
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

The app will automatically open in your default browser at `http://localhost:8501`

## Using q2validate

### Input Methods
1. **Upload JSON File**: Use file browser to select q2prompt output
2. **Paste JSON Text**: Copy/paste JSON directly into text area

### Key Features
- **Auto-fix Unicode → LaTeX**: Converts Ω, π, °, ² etc. to LaTeX notation
- **Schema Validation**: Checks required fields and question formats
- **Visual Preview**: See how questions will appear to students
- **Export Options**: Download corrected JSON for Q2LMS import

### Typical Workflow
1. Generate questions with q2prompt
2. Upload/paste JSON into q2validate
3. Review validation results and question previews
4. Export corrected JSON
5. Import to Q2LMS

## Stopping q2validate

### To Stop the App
- **In PowerShell**: Press `Ctrl+C`
- **In Browser**: Simply close the browser tab

### To Deactivate Virtual Environment
```powershell
deactivate
```
(Prompt will change from `(venv)` back to normal)

## Project Location
- **Main Directory**: `C:\Users\aknoesen\Documents\Knoesen\q2validate`
- **Virtual Environment**: `C:\Users\aknoesen\Documents\Knoesen\q2validate\venv`
- **GitHub Repository**: `https://github.com/aknoesen/q2validate`

## Troubleshooting

### If Streamlit Command Not Found
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Check if streamlit is installed
pip list | findstr streamlit
```

### If Virtual Environment Activation Fails
```powershell
# Check execution policy
Get-ExecutionPolicy

# If needed, set execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### If Port Already in Use
```powershell
# Run on different port
streamlit run q2validate.py --server.port 8502
```

## File Structure
```
q2validate/
├── q2validate.py          # Main application
├── venv/                  # Virtual environment (DO NOT DELETE)
├── modules/               # Core functionality
│   ├── q2lms_adapter.py
│   ├── unicode_converter.py
│   └── schema_validator.py
├── templates/             # Example files
├── scripts/               # PowerShell scripts
├── docs/                  # Documentation
└── shared/q2lms/         # Q2LMS submodule
```

## Quick Commands Reference

```powershell
# Navigate and run (complete sequence)
cd C: