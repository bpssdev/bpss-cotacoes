call venv_win/Scripts/activate.bat
call pyinstaller --onefile --paths "venv_win/Lib" --paths="src" --add-binary="src/assets/icon.ico;assets" --add-binary="src/assets/logo.jpg;assets"  src/init.py
