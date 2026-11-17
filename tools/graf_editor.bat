@echo off
rem Abre el editor grafico de AVENTUR.DAT (doble clic para lanzarlo).
rem Opcional: pasar otro fichero, p.ej.  tools\graf_editor.bat otro.dat
cd /d "%~dp0.."
python tools\graf_editor.py %*
if errorlevel 1 pause
