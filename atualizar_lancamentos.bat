@echo off
rem Busca os proximos lancamentos no IGDB e grava no banco do JogoTeca.
rem As chaves sao digitadas aqui e NAO ficam salvas em nenhum arquivo.
cd /d "%~dp0backend"

if not exist .venv\Scripts\python.exe (
  echo Rode o iniciar.bat ao menos uma vez antes.
  pause
  exit /b 1
)

echo Chaves do IGDB (crie em https://dev.twitch.tv/console)
set /p TWITCH_CLIENT_ID=Client ID: 
set /p TWITCH_CLIENT_SECRET=Client Secret: 
echo.
.venv\Scripts\python.exe -m app.rotina_lancamentos
echo.
pause
