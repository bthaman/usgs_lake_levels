@echo off
color 1f
REM Hard code the exe path, or use %~dp0 to refer to the relative path
REM %~dp0\dist\res.volume.1943.lcragage\res.volume.1943.lcragage.exe
call .\env\scripts\python.exe res.volume.1943.lcragage.py
