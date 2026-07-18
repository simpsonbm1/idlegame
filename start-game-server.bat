@echo off
rem Starts the local web server the game needs for sprites (http, not file://)
rem and opens the scene prototype. Keep this window open while playing;
rem close it to stop the server.
rem The game itself is at:      http://localhost:8321/
rem The scene prototype is at:  http://localhost:8321/tools/scene-prototype.html
cd /d "%~dp0"
start "" "http://localhost:8321/tools/scene-prototype.html"
py -m http.server 8321
