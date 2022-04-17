@echo off
python3 %~dp0\src\guaBookSeat.py
echo Program will quit in 10 seconds...
ping 127.0.0.1 -n 11 > nul