@echo off
echo Icon Extractor Utility
echo ---------------------
set /p exe_path=Enter path to executable: 

set /p output_path=Enter output icon path (e.g., output.ico) [default: extracted_icon.ico]: 
if "%output_path%"=="" set output_path=extracted_icon.ico

echo Searching for extraction utilities...

if exist modules\extract_icon.py (
    echo Found extract_icon.py in modules folder
    python modules\extract_icon.py "%exe_path%" "%output_path%"
) else if exist extract_icon.py (
    echo Found extract_icon.py in current folder
    python extract_icon.py "%exe_path%" "%output_path%"
) else if exist modules\icon_extractor.exe (
    echo Found icon_extractor.exe in modules folder
    modules\icon_extractor.exe "%exe_path%" "%output_path%"
) else if exist icon_extractor.exe (
    echo Found icon_extractor.exe in current folder
    icon_extractor.exe "%exe_path%" "%output_path%"
) else (
    echo Error: No extraction utility found.
    echo Checked locations:
    echo - modules\extract_icon.py
    echo - extract_icon.py
    echo - modules\icon_extractor.exe
    echo - icon_extractor.exe
    echo.
    echo Please copy extract_icon.py or icon_extractor.exe to one of these locations.
    pause
    exit /b 1
)

if exist "%output_path%" (
    echo Success! Icon saved to %output_path%
    echo.
    echo Running binder.py with the extracted icon...
    echo.
    
    if exist modules\binder.py (
        python modules\binder.py
    ) else if exist binder.py (
        python binder.py
    ) else (
        echo Error: binder.py not found in modules folder or current directory.
        pause
        exit /b 1
    )
) else (
    echo Failed to extract icon.
    pause
    exit /b 1
)



