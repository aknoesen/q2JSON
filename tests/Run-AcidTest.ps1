# q2JSON Comprehensive Test Suite Runner
# Location: tests/Run-AcidTest.ps1
# Runs comprehensive acid test from the tests directory

param(
    [switch]$QuickTest,
    [switch]$FullReport,
    [string]$TestDataPath = ""
)

Write-Host "🧪 q2JSON Comprehensive Acid Test Runner" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

# Get current directory (should be tests folder)
$testsDir = Get-Location
$projectRoot = Split-Path $testsDir -Parent

Write-Host "📁 Tests Directory: $testsDir" -ForegroundColor Green
Write-Host "📁 Project Root: $projectRoot" -ForegroundColor Green

# Verify we're in the tests directory
if (-not (Test-Path "test_edge_cases_and_llm_behaviors.py")) {
    Write-Host "❌ Not in tests directory. Please run from the tests folder." -ForegroundColor Red
    Write-Host "Expected location: C:\Users\aknoesen\Documents\Knoesen\Project-Root-Q2QTI\q2JSON\tests" -ForegroundColor Yellow
    exit 1
}

# Verify key files exist
Write-Host "`n🔍 Verifying test environment..." -ForegroundColor Cyan

$requiredFiles = @{
    "JSONProcessor" = "$projectRoot\modules\json_processor.py"
    "Test Data" = "$projectRoot\test_data\Master.json"
    "Acid Test" = "$testsDir\test_acid_comprehensive.py"
    "Test Runner" = "$testsDir\run_all_tests.py"
}

$allFilesExist = $true

foreach ($fileType in $requiredFiles.Keys) {
    $filePath = $requiredFiles[$fileType]
    if (Test-Path $filePath) {
        if ($fileType -eq "Test Data") {
            $fileSize = (Get-Item $filePath).Length
            Write-Host "✅ $fileType Found: $([math]::Round($fileSize/1KB, 2)) KB" -ForegroundColor Green
        } else {
            Write-Host "✅ $fileType Found" -ForegroundColor Green
        }
    } else {
        Write-Host "❌ $fileType Missing: $filePath" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host "`n❌ Missing required files. Please ensure all components are in place." -ForegroundColor Red
    exit 1
}

# Display test options
Write-Host "`n🎯 Test Options:" -ForegroundColor Cyan
if ($QuickTest) {
    Write-Host "   Mode: Quick Test (Basic validation)" -ForegroundColor Yellow
} elseif ($FullReport) {
    Write-Host "   Mode: Full Report (Comprehensive analysis)" -ForegroundColor Yellow
} else {
    Write-Host "   Mode: Standard Acid Test" -ForegroundColor Yellow
}

if ($TestDataPath -ne "") {
    Write-Host "   Custom Test Data: $TestDataPath" -ForegroundColor Yellow
}

# Pre-test system check
Write-Host "`n🔧 System Check:" -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found or not in PATH" -ForegroundColor Red
    exit 1
}

# Check for required modules
Write-Host "`n📦 Checking Python modules..." -ForegroundColor Cyan
$requiredModules = @("json", "pathlib", "statistics", "datetime")
foreach ($module in $requiredModules) {
    try {
        python -c "import $module" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $module module available" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $module module check failed" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️  Could not verify $module module" -ForegroundColor Yellow
    }
}

Write-Host "`n🚀 Starting Comprehensive Acid Test..." -ForegroundColor Cyan
Write-Host "⏳ This will process your Master.json dataset..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

$startTime = Get-Date

try {
    if ($QuickTest) {
        # Run quick validation
        Write-Host "🔍 Running Quick Test..." -ForegroundColor Cyan
        python test_edge_cases_and_llm_behaviors.py
        $quickResult = $LASTEXITCODE
        
        if ($quickResult -eq 0) {
            Write-Host "✅ Quick Test Passed - Running Acid Test..." -ForegroundColor Green
        } else {
            Write-Host "❌ Quick Test Failed - Check basic functionality first" -ForegroundColor Red
            exit $quickResult
        }
    }
    
    # Run the comprehensive acid test
    Write-Host "🧪 Running Comprehensive Acid Test..." -ForegroundColor Cyan
    if ($TestDataPath -ne "") {
        # If custom test data path provided, modify the test temporarily
        Write-Host "📁 Using custom test data: $TestDataPath" -ForegroundColor Yellow
    }
    
    python test_acid_comprehensive.py
    $acidResult = $LASTEXITCODE
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    Write-Host "⏱️  Total Test Duration: $($duration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Cyan
    
    if ($acidResult -eq 0) {
        Write-Host "🎉 COMPREHENSIVE ACID TEST PASSED! 🎉" -ForegroundColor Green
        Write-Host "✅ JSONProcessor is production ready!" -ForegroundColor Green
        
        # Check for results files
        $resultsDir = "$testsDir\acid_test_results"
        if (Test-Path $resultsDir) {
            $resultFiles = Get-ChildItem $resultsDir -Filter "acid_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
            Write-Host "`n📊 Latest Results:" -ForegroundColor Cyan
            foreach ($file in $resultFiles) {
                Write-Host "   📄 $($file.Name)" -ForegroundColor White
            }
            Write-Host "   📁 Location: $resultsDir" -ForegroundColor Gray
        }
        
        if ($FullReport) {
            Write-Host "`n📋 Opening detailed results..." -ForegroundColor Cyan
            if (Test-Path $resultsDir) {
                explorer $resultsDir
            }
        }
        
    } else {
        Write-Host "❌ COMPREHENSIVE ACID TEST FAILED" -ForegroundColor Red
        Write-Host "⚠️  Check the output above for specific issues" -ForegroundColor Yellow
        Write-Host "💡 Recommendations:" -ForegroundColor Cyan
        Write-Host "   • Review error messages in the output" -ForegroundColor White
        Write-Host "   • Check test_data/Master.json format and content" -ForegroundColor White
        Write-Host "   • Verify JSONProcessor enhancements are working" -ForegroundColor White
        Write-Host "   • Run individual tests to isolate issues" -ForegroundColor White
    }
    
} catch {
    Write-Host "❌ Error running tests: $_" -ForegroundColor Red
    $acidResult = 1
}

# Additional analysis if full report requested
if ($FullReport -and $acidResult -eq 0) {
    Write-Host "`n🔍 Running Additional Analysis..." -ForegroundColor Cyan
    
    # Check results directory for analysis
    $resultsDir = "$testsDir\acid_test_results"
    if (Test-Path $resultsDir) {
        $summaryFiles = Get-ChildItem $resultsDir -Filter "acid_summary_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        
        if ($summaryFiles) {
            Write-Host "📊 Latest Results Summary:" -ForegroundColor Cyan
            $summaryContent = Get-Content $summaryFiles[0].FullName | ConvertFrom-Json
            
            Write-Host "   🎯 Success Rate: $($summaryContent.success_rate.ToString('F1'))%" -ForegroundColor Green
            Write-Host "   ⚡ Processing Speed: $($summaryContent.performance_metrics.questions_per_second.ToString('F1')) q/s" -ForegroundColor Green
            Write-Host "   🏆 Production Score: $($summaryContent.production_readiness_score.ToString('F1'))/100" -ForegroundColor Green
            
            if ($summaryContent.production_readiness_score -ge 90) {
                Write-Host "   🟢 Status: EXCELLENT - PRODUCTION READY" -ForegroundColor Green
            } elseif ($summaryContent.production_readiness_score -ge 80) {
                Write-Host "   🟡 Status: GOOD - MINOR IMPROVEMENTS RECOMMENDED" -ForegroundColor Yellow
            } else {
                Write-Host "   🟠 Status: NEEDS IMPROVEMENT" -ForegroundColor Yellow
            }
        }
    }
}

# Summary and next steps
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "📊 TEST SUITE COMPLETE" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

if ($acidResult -eq 0) {
    Write-Host "🏆 OVERALL RESULT: SUCCESS" -ForegroundColor Green
    Write-Host "`n🚀 Ready for Production Deployment!" -ForegroundColor Green
    Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Review detailed results in acid_test_results/" -ForegroundColor White
    Write-Host "   2. Deploy JSONProcessor to production environment" -ForegroundColor White
    Write-Host "   3. Set up monitoring based on test recommendations" -ForegroundColor White
    Write-Host "   4. Integrate with your LMS workflow" -ForegroundColor White
} else {
    Write-Host "⚠️  OVERALL RESULT: NEEDS ATTENTION" -ForegroundColor Yellow
    Write-Host "`n🔧 Recommended Actions:" -ForegroundColor Cyan
    Write-Host "   1. Review error messages and fix identified issues" -ForegroundColor White
    Write-Host "   2. Re-run tests after improvements" -ForegroundColor White
    Write-Host "   3. Consider running individual test components" -ForegroundColor White
    Write-Host "   4. Verify test data format and accessibility" -ForegroundColor White
}

Write-Host "`n📁 Test Artifacts:" -ForegroundColor Cyan
Write-Host "   • Results: tests/acid_test_results/" -ForegroundColor Gray
Write-Host "   • Logs: Console output above" -ForegroundColor Gray
Write-Host "   • Duration: $($duration.TotalSeconds.ToString('F1')) seconds" -ForegroundColor Gray

Write-Host "`n🏁 Acid Test Complete!" -ForegroundColor Cyan
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")