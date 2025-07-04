# Q2JSON Codebase Analysis Script
# Following Copilot Efficiency Guide: "Fresh Analysis First" Pattern
# 
# This script captures comprehensive codebase analysis for LaTeX corrector integration
# Output: Multiple analysis files for systematic review

param(
    [string]$OutputDir = "analysis_output",
    [switch]$Verbose
)

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
    Write-Host "✅ Created analysis output directory: $OutputDir" -ForegroundColor Green
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

Write-Host "🔍 Q2JSON Codebase Analysis - Strategic Phase" -ForegroundColor Magenta
Write-Host "=" * 50 -ForegroundColor Magenta
Write-Host "Following Copilot Efficiency Guide: Fresh Analysis First Pattern" -ForegroundColor Yellow
Write-Host "Output directory: $OutputDir" -ForegroundColor Cyan
Write-Host ""

# Analysis 1: Project Structure Overview
Write-Host "📁 Analysis 1: Project Structure Overview..." -ForegroundColor Yellow
$structureFile = "$OutputDir/01_project_structure_$timestamp.txt"

@"
Q2JSON PROJECT STRUCTURE ANALYSIS
Generated: $(Get-Date)
Directory: $(Get-Location)
Branch: $(git branch --show-current 2>$null)

=== ROOT LEVEL FILES ===
"@ | Out-File $structureFile

Get-ChildItem -File | Sort-Object Name | ForEach-Object {
    "$($_.Name) ($($_.Length) bytes)"
} | Out-File $structureFile -Append

@"

=== PYTHON FILES IN ROOT ===
"@ | Out-File $structureFile -Append

Get-ChildItem -Filter "*.py" | Sort-Object Name | ForEach-Object {
    "$($_.Name) - $(Get-Date $_.LastWriteTime -Format 'yyyy-MM-dd HH:mm')"
} | Out-File $structureFile -Append

@"

=== DIRECTORY STRUCTURE ===
"@ | Out-File $structureFile -Append

Get-ChildItem -Directory | Sort-Object Name | ForEach-Object {
    $dirName = $_.Name
    $fileCount = (Get-ChildItem $_.FullName -File -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
    "$dirName/ ($fileCount files)"
} | Out-File $structureFile -Append

Write-Host "   ✅ Saved to: $structureFile" -ForegroundColor Green

# Analysis 2: Pipeline and Main Files
Write-Host "🚀 Analysis 2: Pipeline and Main Files..." -ForegroundColor Yellow
$pipelineFile = "$OutputDir/02_pipeline_files_$timestamp.txt"

@"
PIPELINE AND MAIN FILES ANALYSIS
Generated: $(Get-Date)

=== MAIN/PIPELINE CANDIDATES ===
"@ | Out-File $pipelineFile

$mainFiles = Get-ChildItem -Filter "*.py" | Where-Object { 
    $_.Name -like "*main*" -or 
    $_.Name -like "*pipeline*" -or 
    $_.Name -like "*enhanced*" -or
    $_.Name -like "*app*" -or
    $_.Name -like "*run*"
}

if ($mainFiles) {
    $mainFiles | ForEach-Object {
        @"

=== FILE: $($_.Name) ===
Size: $($_.Length) bytes
Modified: $(Get-Date $_.LastWriteTime -Format 'yyyy-MM-dd HH:mm:ss')

First 30 lines:
"@ | Out-File $pipelineFile -Append
        
        Get-Content $_.FullName -TotalCount 30 -ErrorAction SilentlyContinue | Out-File $pipelineFile -Append
        
        @"

Last 10 lines:
"@ | Out-File $pipelineFile -Append
        
        Get-Content $_.FullName -Tail 10 -ErrorAction SilentlyContinue | Out-File $pipelineFile -Append
    }
} else {
    "No main/pipeline files found matching common patterns." | Out-File $pipelineFile -Append
}

Write-Host "   ✅ Saved to: $pipelineFile" -ForegroundColor Green

# Analysis 3: LaTeX References Search
Write-Host "📄 Analysis 3: LaTeX References Search..." -ForegroundColor Yellow
$latexFile = "$OutputDir/03_latex_references_$timestamp.txt"

@"
LATEX REFERENCES ANALYSIS
Generated: $(Get-Date)

=== SEARCHING FOR LATEX PATTERNS ===
Patterns: latex, LaTeX, corrector, correction

"@ | Out-File $latexFile

try {
    $latexRefs = Get-ChildItem -Recurse -Include "*.py" -ErrorAction SilentlyContinue | 
                 Select-String -Pattern "latex|LaTeX|corrector|correction" -Context 2 -ErrorAction SilentlyContinue

    if ($latexRefs) {
        $latexRefs | ForEach-Object {
            @"

=== $($_.Filename):$($_.LineNumber) ===
$($_.Context.PreContext -join "`n")
>>> $($_.Line) <<<
$($_.Context.PostContext -join "`n")
"@ | Out-File $latexFile -Append
        }
    } else {
        "No LaTeX references found in Python files." | Out-File $latexFile -Append
    }
} catch {
    "Error searching for LaTeX references: $($_.Exception.Message)" | Out-File $latexFile -Append
}

Write-Host "   ✅ Saved to: $latexFile" -ForegroundColor Green

# Analysis 4: Stage 3 Human Review Analysis
Write-Host "👥 Analysis 4: Stage 3 Human Review Analysis..." -ForegroundColor Yellow
$stage3File = "$OutputDir/04_stage3_analysis_$timestamp.txt"

@"
STAGE 3 HUMAN REVIEW ANALYSIS
Generated: $(Get-Date)

"@ | Out-File $stage3File

if (Test-Path "stages/stage_3_human_review.py") {
    @"
=== STAGE 3 FILE FOUND ===
File: stages/stage_3_human_review.py
Size: $((Get-Item "stages/stage_3_human_review.py").Length) bytes
Modified: $(Get-Date (Get-Item "stages/stage_3_human_review.py").LastWriteTime -Format 'yyyy-MM-dd HH:mm:ss')

=== FULL CONTENT ===
"@ | Out-File $stage3File -Append
    
    Get-Content "stages/stage_3_human_review.py" -ErrorAction SilentlyContinue | Out-File $stage3File -Append
} else {
    "stages/stage_3_human_review.py not found." | Out-File $stage3File -Append
}

# Check for other stage files
@"

=== OTHER STAGE FILES ===
"@ | Out-File $stage3File -Append

if (Test-Path "stages") {
    Get-ChildItem "stages" -Filter "*.py" | ForEach-Object {
        "Found: stages/$($_.Name)"
    } | Out-File $stage3File -Append
} else {
    "stages/ directory not found." | Out-File $stage3File -Append
}

Write-Host "   ✅ Saved to: $stage3File" -ForegroundColor Green

# Analysis 5: Import Patterns and Dependencies
Write-Host "📦 Analysis 5: Import Patterns and Dependencies..." -ForegroundColor Yellow
$importsFile = "$OutputDir/05_import_patterns_$timestamp.txt"

@"
IMPORT PATTERNS AND DEPENDENCIES ANALYSIS
Generated: $(Get-Date)

=== PYTHON FILE IMPORTS ANALYSIS ===
"@ | Out-File $importsFile

Get-ChildItem -Filter "*.py" | ForEach-Object {
    $fileName = $_.Name
    @"

=== $fileName ===
"@ | Out-File $importsFile -Append
    
    try {
        $imports = Get-Content $_.FullName -ErrorAction SilentlyContinue | 
                   Select-String -Pattern "^(import|from).*" | 
                   Select-Object -First 20
        
        if ($imports) {
            $imports.Line | Out-File $importsFile -Append
        } else {
            "No imports found." | Out-File $importsFile -Append
        }
    } catch {
        "Error reading imports: $($_.Exception.Message)" | Out-File $importsFile -Append
    }
}

Write-Host "   ✅ Saved to: $importsFile" -ForegroundColor Green

# Analysis 6: Test Data and Configuration
Write-Host "🧪 Analysis 6: Test Data and Configuration..." -ForegroundColor Yellow
$testDataFile = "$OutputDir/06_test_data_config_$timestamp.txt"

@"
TEST DATA AND CONFIGURATION ANALYSIS
Generated: $(Get-Date)

=== TEST DATA DIRECTORY ===
"@ | Out-File $testDataFile

if (Test-Path "test_data") {
    @"
test_data/ directory found.

Files in test_data/:
"@ | Out-File $testDataFile -Append
    
    Get-ChildItem "test_data" | ForEach-Object {
        "$($_.Name) - $($_.Length) bytes - $(Get-Date $_.LastWriteTime -Format 'yyyy-MM-dd HH:mm')"
    } | Out-File $testDataFile -Append
    
    # Check MOSFET test data specifically
    if (Test-Path "test_data/MosfetQQDebug.json") {
        @"

=== MOSFET TEST DATA SAMPLE ===
First 50 lines of MosfetQQDebug.json:
"@ | Out-File $testDataFile -Append
        
        Get-Content "test_data/MosfetQQDebug.json" -TotalCount 50 -ErrorAction SilentlyContinue | Out-File $testDataFile -Append
    }
} else {
    "test_data/ directory not found." | Out-File $testDataFile -Append
}

@"

=== CONFIGURATION FILES ===
"@ | Out-File $testDataFile -Append

$configFiles = Get-ChildItem -Filter "*config*" -Recurse | Select-Object -First 10
if ($configFiles) {
    $configFiles | ForEach-Object {
        "$($_.FullName) - $($_.Length) bytes"
    } | Out-File $testDataFile -Append
} else {
    "No configuration files found." | Out-File $testDataFile -Append
}

Write-Host "   ✅ Saved to: $testDataFile" -ForegroundColor Green

# Analysis 7: Git Status and Branch Information
Write-Host "📊 Analysis 7: Git Status and Branch Information..." -ForegroundColor Yellow
$gitFile = "$OutputDir/07_git_status_$timestamp.txt"

@"
GIT STATUS AND BRANCH ANALYSIS
Generated: $(Get-Date)

=== CURRENT GIT STATUS ===
"@ | Out-File $gitFile

try {
    git status 2>&1 | Out-File $gitFile -Append
    
    @"

=== BRANCH INFORMATION ===
"@ | Out-File $gitFile -Append
    
    git branch -a 2>&1 | Out-File $gitFile -Append
    
    @"

=== RECENT COMMITS ===
"@ | Out-File $gitFile -Append
    
    git log --oneline -10 2>&1 | Out-File $gitFile -Append
} catch {
    "Git not available or not a git repository." | Out-File $gitFile -Append
}

Write-Host "   ✅ Saved to: $gitFile" -ForegroundColor Green

# Analysis 8: Modules Directory Analysis
Write-Host "🔧 Analysis 8: Modules Directory Analysis..." -ForegroundColor Yellow
$modulesFile = "$OutputDir/08_modules_analysis_$timestamp.txt"

@"
MODULES DIRECTORY ANALYSIS
Generated: $(Get-Date)

"@ | Out-File $modulesFile

if (Test-Path "modules") {
    @"
=== MODULES DIRECTORY STRUCTURE ===
"@ | Out-File $modulesFile -Append
    
    Get-ChildItem "modules" -Recurse | ForEach-Object {
        if ($_.PSIsContainer) {
            "DIR:  $($_.FullName.Replace((Get-Location).Path, ''))"
        } else {
            "FILE: $($_.FullName.Replace((Get-Location).Path, '')) ($($_.Length) bytes)"
        }
    } | Out-File $modulesFile -Append
    
    @"

=== PYTHON FILES IN MODULES ===
"@ | Out-File $modulesFile -Append
    
    Get-ChildItem "modules" -Filter "*.py" -Recurse | ForEach-Object {
        @"

--- $($_.FullName.Replace((Get-Location).Path, '')) ---
First 20 lines:
"@ | Out-File $modulesFile -Append
        
        Get-Content $_.FullName -TotalCount 20 -ErrorAction SilentlyContinue | Out-File $modulesFile -Append
    }
} else {
    "modules/ directory not found." | Out-File $modulesFile -Append
}

Write-Host "   ✅ Saved to: $modulesFile" -ForegroundColor Green

# Summary Report
Write-Host "📋 Generating Summary Report..." -ForegroundColor Yellow
$summaryFile = "$OutputDir/00_ANALYSIS_SUMMARY_$timestamp.txt"

@"
Q2JSON CODEBASE ANALYSIS SUMMARY
Generated: $(Get-Date)
Analysis Session: $timestamp

=== PURPOSE ===
Strategic analysis for LaTeX auto-correction integration
Following Copilot Efficiency Guide: "Fresh Analysis First" Pattern

=== FILES GENERATED ===
01_project_structure_$timestamp.txt    - Overall project layout
02_pipeline_files_$timestamp.txt       - Main execution files  
03_latex_references_$timestamp.txt     - Existing LaTeX code
04_stage3_analysis_$timestamp.txt      - Human review stage code
05_import_patterns_$timestamp.txt      - Dependencies and imports
06_test_data_config_$timestamp.txt     - Test cases and config
07_git_status_$timestamp.txt           - Repository state
08_modules_analysis_$timestamp.txt     - Module structure

=== NEXT STEPS ===
1. Review analysis files systematically
2. Identify LaTeX corrector integration point
3. Start fresh Copilot session with strategic context
4. Implement LaTeX corrector using proven patterns

=== KEY QUESTIONS TO RESOLVE ===
- What is the main pipeline entry point?
- Where does validation currently happen?
- How does Stage 3 human review integrate?
- What's the data flow through the system?

Review these files to answer strategic questions before implementation.
"@ | Out-File $summaryFile

Write-Host "   ✅ Saved to: $summaryFile" -ForegroundColor Green

# Final Summary
Write-Host ""
Write-Host "✅ ANALYSIS COMPLETE" -ForegroundColor Green -BackgroundColor DarkGreen
Write-Host ""
Write-Host "📁 Output Location: $OutputDir" -ForegroundColor Cyan
Write-Host "📊 Files Generated: 9 analysis files" -ForegroundColor Cyan
Write-Host "🕒 Timestamp: $timestamp" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Review $summaryFile first" -ForegroundColor White
Write-Host "2. Examine pipeline files (02_pipeline_files_*.txt)" -ForegroundColor White  
Write-Host "3. Check LaTeX references (03_latex_references_*.txt)" -ForegroundColor White
Write-Host "4. Understand Stage 3 integration (04_stage3_analysis_*.txt)" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Following Copilot Efficiency Guide principles:" -ForegroundColor Magenta
Write-Host "   - Fresh analysis before implementation ✅" -ForegroundColor Green
Write-Host "   - Strategic understanding first ✅" -ForegroundColor Green  
Write-Host "   - Clear context for Copilot session ✅" -ForegroundColor Green
Write-Host ""
Write-Host "Ready for systematic LaTeX corrector integration!" -ForegroundColor Green

if ($Verbose) {
    Write-Host ""
    Write-Host "=== VERBOSE: File Sizes ===" -ForegroundColor Gray
    Get-ChildItem $OutputDir -Filter "*$timestamp*" | ForEach-Object {
        Write-Host "$($_.Name): $($_.Length) bytes" -ForegroundColor Gray
    }
}