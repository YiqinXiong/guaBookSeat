@echo off
chcp 936
schtasks /create /tn "booking" /xml %~dp0\booking.xml /F
pause