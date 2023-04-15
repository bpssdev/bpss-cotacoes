call venv_win/Scripts/activate.bat
call pyinstaller --onefile --paths "venv_win/Lib" --paths="src" src/test/cli.py
