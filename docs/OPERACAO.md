# JogoTeca: guia de operação

Para quem vai ligar, atualizar, proteger e consertar o sistema. Os comandos são para o Prompt de Comando do Windows, dentro da pasta do projeto (a que tem o `docker-compose.yml`).

## 1. Visão geral

| Peça | O que é | Onde |
| --- | --- | --- |
| `web` | Site (React servido pelo Nginx) | http://localhost:5173 |
| `api` | API (FastAPI) | http://localhost:8000/docs |
| `mysql` | Banco MariaDB (sem porta aberta ao computador) | só entre os containers |
| `rotina` | Busca dos lançamentos (IGDB), roda e termina | sob demanda |

Dados que precisam sobreviver: o banco (volume `mysql_dados`) e as capas (volume `capas`). Tudo o mais se recria a partir do código.

## 2. Requisitos

- Windows com **Docker Desktop** instalado e com **Engine running** (verde, canto inferior esquerdo).
- Pelo menos **10 GB livres no disco C:** (o disco cheio causa erros estranhos no Docker).
- Arquivo **`.env`** na pasta do projeto (veja a seção 4). Ele nunca vai para o GitHub.

## 3. Rotina do dia a dia

| Quero | Faço |
| --- | --- |
| Ligar | Docker Desktop aberto, depois `docker compose up -d` (ou **Start** no Docker Desktop) |
| Desligar | **Stop** no Docker Desktop, ou `docker compose stop` |
| Ver se está de pé | `docker compose ps` (mysql `healthy`, api `healthy`, web `running`) |
| Atualizar o código | Veja a seção 5 |
| Atualizar os lançamentos | `docker compose run --rm rotina` |
| Backup | duplo clique em `fazer_backup.bat` |
| Restaurar | duplo clique em `restaurar_backup.bat` |
| Ver o que aconteceu | duplo clique em `ver_logs.bat` |

**Nunca use `docker compose down -v`.** O `-v` apaga os volumes: todos os usuários, jogos e capas somem. O `down` sem o `-v` é seguro.

## 4. Configuração (`.env`)

Copie `.env.example` para `.env` e preencha. Use **só letras, números e hífen** nas senhas: símbolos como `@ : / # %` quebram o endereço de conexão do banco.

| Variável | Para que serve |
| --- | --- |
| `MYSQL_PASSWORD` | Senha do usuário do banco |
| `MYSQL_ROOT_PASSWORD` | Senha de administrador do banco (diferente da anterior) |
| `JWT_SEGREDO` | Segredo que assina o login. 32+ caracteres, aleatório, único |
| `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET` | Chaves da IGDB, só para a rotina de lançamentos |
| `LOG_NIVEL` | `INFO` (padrão), `DEBUG`, `WARNING` ou `ERROR` |

**As senhas do banco só valem na primeira criação do volume.** Mudar o `.env` depois não muda a senha que o banco já guardou: a API passa a tentar uma senha que o banco não conhece (`Access denied`). Para trocar, restaure por backup em um banco novo (seção 6).

Os valores das chaves da Twitch e as senhas **nunca** vão em e-mail, chat, print ou commit. Se uma chave vazar, gere outra no painel da Twitch.

## 5. Atualizar o sistema

1. Faça um **backup** antes (`fazer_backup.bat`).
2. Traga o código novo (`git pull`, ou extraia a versão nova por cima).
3. `docker compose up -d --build`
4. Confira `docker compose ps` e abra o site.

O banco se atualiza sozinho: a API aplica as **migrações** (Alembic) ao iniciar, só o que falta, sem apagar dados.

Para criar uma migração nova depois de mudar `modelos.py` (dentro de `backend/`): `alembic revision --autogenerate -m "o que mudou"`. Revise o arquivo gerado. Há um teste que falha se o modelo e as migrações divergirem.

## 6. Backup e restauração

- `fazer_backup.bat` salva `banco.sql` e `capas\` em `backups\AAAA-MM-DD_HH-MM\`. O sistema precisa estar ligado.
- `restaurar_backup.bat` lista os backups, pede o nome da pasta e a palavra `SIM`, faz antes um backup de segurança do estado atual, e restaura.
- A pasta `backups` não vai para o GitHub (tem dados de usuários). **Copie-a também para outro lugar** (pen drive, nuvem pessoal): backup só no mesmo computador não protege contra perda do computador.
- **Teste a restauração de vez em quando.** Backup nunca restaurado não é garantia.

Frequência sugerida: antes de cada atualização e uma vez por semana.

## 7. Logs

A API escreve uma linha JSON por evento. Cada requisição tem um `id` (também no cabeçalho de resposta `X-Request-ID`), método, caminho, status e tempo em ms.

- `ver_logs.bat` mostra erros, avisos e os últimos eventos. Ao vivo: `docker compose logs -f api`.
- Senha, token, e-mail, cookie e o conteúdo enviado nunca entram nos logs. O IP só aparece em eventos de segurança (401, 403, 429).
- Hoje o IP registrado é o do Docker (`172.18.0.1`). Atrás de um servidor na frente, o IP real virá por `X-Forwarded-For` e o código precisará lê-lo.

O que observar:

| Sinal | Significa | O que fazer |
| --- | --- | --- |
| `"nivel": "ERROR"` | Algo quebrou | Procure o `id` e a linha `erro_nao_tratado` com o detalhe |
| Muitos `401` do mesmo `ip` | Alguém tentando adivinhar senha | O limitador já barra; vigie se continuar |
| `429` | O limitador barrou alguém | Normal em pequena quantidade |
| `rotina_lancamentos_falhou` | A rotina não atualizou | Veja o motivo; os lançamentos antigos foram mantidos |
| Container `unhealthy` | A API parou de responder | `docker compose logs api`, depois `docker compose restart api` |

## 8. Problemas conhecidos e soluções

| Sintoma | Causa | Solução |
| --- | --- | --- |
| `service "mysql" is not running` | Sistema desligado | `docker compose up -d` |
| `Cannot connect to the Docker daemon` | Docker Desktop fechado | Abra o Docker Desktop e espere o **Engine running** verde |
| `bus error`, `input/output error`, `read-only file system` ao baixar imagens | Disco C: cheio | Libere espaço (veja a seção 2); depois feche o Docker, rode `wsl --shutdown` e abra de novo |
| Banco em loop de reinício, sem mensagem | O MySQL 8.4 não roda em alguns processadores | Por isso usamos MariaDB (`mariadb:11.4`) |
| `Access denied for user 'jogoteca'` | Senha do `.env` diferente da que o banco guardou | Seção 4: senhas só valem na criação do volume |
| `Can't connect to MySQL server on '@mysql'` | Símbolo (`@`) na senha do banco | Use só letras, números e hífen |
| Site abre, mas login não funciona | Abriu por `127.0.0.1` em vez de `localhost` | Use sempre http://localhost:5173 |
| Lançamentos vazios | A rotina nunca rodou ou faltam as chaves | Preencha as chaves no `.env`, depois `docker compose up -d` e `docker compose run --rm rotina` |
| `docker compose` diz que falta `.env` ou variável vazia | Arquivo ausente | `copy .env.example .env` e preencha |
| Git mostra `Dockerfile`/`.dockerignore` alterados sem você mexer | Diferença de quebra de linha Windows/Linux | `git restore backend/.dockerignore` (só se você não alterou o conteúdo) |

## 9. Segurança: checklist antes de colocar na internet

- [ ] `AMBIENTE=producao` (o sistema se recusa a subir com segredo padrão, cookie sem `Secure` ou origem `http://`)
- [ ] `COOKIE_SEGURO=true` e site servido por **HTTPS**
- [ ] `ORIGENS_FRONT` com o endereço `https://` real
- [ ] `JWT_SEGREDO` próprio, longo e único; senhas do banco próprias
- [ ] Banco **sem** porta aberta para a internet
- [ ] Ler o IP real do cliente (`X-Forwarded-For`) para o limitador e para os logs
- [ ] Backup agendado e copiado para fora do servidor
- [ ] 2FA ativo na conta do GitHub, na da hospedagem e na da Twitch
- [ ] CI verde antes de cada atualização

## 10. Mapa do repositório

| Caminho | Conteúdo |
| --- | --- |
| `backend/app/` | API em camadas (`dominio`, `casos_de_uso`, `rotas`, `adaptadores`) |
| `backend/app/adaptadores/persistencia/migracoes/` | Histórico da estrutura do banco (Alembic) |
| `backend/tests/` | Testes automáticos |
| `frontend/` | Site React |
| `docs/diagramas/` | 13 diagramas do projeto |
| `.github/workflows/ci.yml` | Robô de verificação (testes, auditorias, build, Docker) |
| `*.bat` | Atalhos: `iniciar`, `atualizar_lancamentos`, `fazer_backup`, `restaurar_backup`, `ver_logs` |
