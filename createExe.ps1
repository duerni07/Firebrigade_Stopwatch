#This file creates an exe file from the python script Bewerbstimer.py.
#IMPORTANT: The script must be executed in the same directory as the Bewerbstimer.py file.
#Otherwise the paths to the media, static and templates folder is wrong!!

#delete everything fron the dist folder
Remove-Item -Recurse -Force "dist\*"

#remove the folder build if it exists
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
}

# Install virtualenv and pyinstaller
pip install virtualenv
pip install pyinstaller

# Create virtual environment
python -m venv venv

# Activate the virtual environment
./venv/Scripts/Activate.ps1

# Install requirements
pip install -r requirements.txt

# Run pyinstaller
pyinstaller --onefile --add-data="./templates/*;./templates/" --add-data="./static/*;./static/" --add-data="media;media" Bewerbstimer.py

# Copy the media, static and templates folder to the dist folder
Copy-Item -Recurse -Force media dist
Copy-Item -Recurse -Force "static" dist
Copy-Item -Recurse -Force templates dist

#remove the build folder
Remove-Item -Recurse -Force "build"

# Deactivate the virtual environment
deactivate
