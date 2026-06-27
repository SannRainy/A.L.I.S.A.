@echo off
chcp 65001 > nul
title TVJP - Backend Test Suite
cd /d "%~dp0..\.."
call run_tests.bat
