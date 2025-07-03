@echo off
echo Running Stage 4 Integration Tests...
echo.

cd /d "%~dp0\.."
python tests\test_stage4_integration.py

echo.
echo Test execution completed.
echo Check tests\stage4_test_report.json for detailed results.
pause
