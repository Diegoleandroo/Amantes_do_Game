@echo off
rem Faz o backup do JogoTeca: banco de dados + capas. Duplo clique para rodar.
rem Salva em backups\AAAA-MM-DD_HH-MM\  (a pasta backups nunca vai para o GitHub)
cd /d "%~dp0"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm"') do set DATA=%%i
set PASTA=backups\%DATA%
mkdir "%PASTA%"

echo.
echo [1/2] Salvando o banco de dados...
docker compose exec -T mysql sh -c "mariadb-dump -ujogoteca -p$MARIADB_PASSWORD --single-transaction jogoteca" > "%PASTA%\banco.sql"
if errorlevel 1 goto erro

echo [2/2] Salvando as capas...
docker compose cp api:/srv/armazenamento/capas "%PASTA%\capas"
if errorlevel 1 goto erro

echo.
echo Backup concluido em: %PASTA%
for %%f in ("%PASTA%\banco.sql") do echo Tamanho do banco: %%~zf bytes
echo.
pause
exit /b 0

:erro
echo.
echo ERRO: o backup nao foi concluido. O sistema esta ligado? (docker compose up -d)
rmdir /s /q "%PASTA%" 2>nul
echo.
pause
exit /b 1
