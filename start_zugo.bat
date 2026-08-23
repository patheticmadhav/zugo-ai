@echo off
title Zugo.ai
cd /d "%~dp0"
echo Starting Zugo.ai...
echo Make sure Ollama is running in the background.
echo.
py -3.12 agent.py
pause