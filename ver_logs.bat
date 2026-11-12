@echo off
rem Mostra o que a API registrou. Duplo clique.
cd /d "%~dp0"
echo ===== ERROS (nivel ERROR) =====
docker compose logs --no-log-prefix api 2>nul | findstr /C:"\"nivel\": \"ERROR\""
echo.
echo ===== AVISOS (logins errados, acessos negados, limite excedido) =====
docker compose logs --no-log-prefix api 2>nul | findstr /C:"\"nivel\": \"WARNING\""
echo.
echo ===== ULTIMOS 15 EVENTOS =====
docker compose logs --no-log-prefix --tail 15 api
echo.
pause
