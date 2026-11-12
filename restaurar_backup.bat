@echo off
rem Restaura um backup do JogoTeca (banco + capas). Substitui os dados atuais pelos do backup.
rem Antes de restaurar, faz um backup de seguranca do estado atual.
cd /d "%~dp0"

echo Backups disponiveis:
echo.
dir /b /ad backups 2>nul
echo.
set /p NOME=Digite o nome da pasta do backup a restaurar (ex: 2026-11-12_17-30): 
if "%NOME%"=="" goto cancelar
if not exist "backups\%NOME%\banco.sql" (
  echo.
  echo Nao encontrei backups\%NOME%\banco.sql
  goto cancelar
)

echo.
echo ATENCAO: os dados atuais serao SUBSTITUIDOS pelos do backup %NOME%.
set /p OK=Digite SIM para continuar: 
if /i not "%OK%"=="SIM" goto cancelar

echo.
echo [0/3] Backup de seguranca do estado atual...
call fazer_backup.bat

echo [1/3] Restaurando o banco de dados...
docker compose exec -T mysql sh -c "mariadb -ujogoteca -p$MARIADB_PASSWORD jogoteca" < "backups\%NOME%\banco.sql"
if errorlevel 1 goto erro

echo [2/3] Restaurando as capas...
if exist "backups\%NOME%\capas" (
  docker compose cp "backups\%NOME%\capas" api:/srv/armazenamento/
  if errorlevel 1 goto erro
  docker compose exec -u root api chown -R jogoteca /srv/armazenamento/capas
)

echo [3/3] Reiniciando a API...
docker compose restart api

echo.
echo Restauracao concluida.
echo.
pause
exit /b 0

:cancelar
echo.
echo Cancelado. Nada foi alterado.
echo.
pause
exit /b 1

:erro
echo.
echo ERRO durante a restauracao. Seus dados anteriores estao no backup de seguranca mais recente em backups\.
echo.
pause
exit /b 1
