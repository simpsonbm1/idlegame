@echo off
rem Starts the local web server the game needs for sprites (http, not file://)
rem and opens the game. Keep this window open while playing; close it to stop
rem the server. Double-clicking index.html directly still runs the game, but
rem sprite art needs http (canvas pixel access is blocked on file://).
rem The game is at:             http://localhost:8321/index.html
rem The scene prototype is at:  http://localhost:8321/tools/scene-prototype.html
cd /d "%~dp0"
start "" "http://localhost:8321/index.html"
py -m http.server 8321
