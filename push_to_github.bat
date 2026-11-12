@echo off
title HireNova - GitHub Deploy
echo ==========================================================
echo   HireNova - Push to GitHub (chethan-0427/HireNova)
echo ==========================================================
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0push_to_github.ps1"
pause

