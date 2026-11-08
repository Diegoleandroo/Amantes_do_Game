@echo off
rem Liga o back-end e o front-end do JogoTeca, cada um em sua janela.
cd /d "%~dp0"

if not exist backend\.venv (
  echo Criando ambiente do back-end, so na primeira vez...
  python -m venv backend\.venv
  backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
)
if not exist frontend\node_modules (
  echo Instalando o front-end, so na primeira vez...
  pushd frontend
  call npm install
  popd
)

start "JogoTeca - API" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload"
start "JogoTeca - Front" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 6 >nul
start http://localhost:5173
