@echo off
schtasks /create /tn "booking" /tr %~dp0\win-2-ԤԼλ��.bat /sc DAILY /st 22:00
pause