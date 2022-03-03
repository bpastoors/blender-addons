@echo off
if [%1]==[] goto :eof

:loop
set targetpath=%~1
set targetname=%~nx1

mklink /D "%APPDATA%\Blender Foundation\Blender\3.0\scripts\addons\%targetname%" "%targetpath%"

shift
if not [%1]==[] goto loop