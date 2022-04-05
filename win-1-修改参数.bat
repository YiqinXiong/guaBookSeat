@echo off
:1
if "%1"=="h" goto :2
mshta vbscript:createobject("wscript.shell").run("""%~nx0"" h",0)(window.close)&&exit
:2
python3 %~dp0\src\create_config.py