@echo off
setlocal
set "LUMINA_STATE_ROOT=%LOCALAPPDATA%\Lumina\state\ship_of_ethereon_v2"
"%LOCALAPPDATA%\Lumina\runtime\python\python.exe" "%LOCALAPPDATA%\Lumina\app\EthereonLabs\LuminaOS\bootstrap\Ship_of_Ethereon_V2\bin\lumina" %*
exit /b %ERRORLEVEL%
