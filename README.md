# JogoTeca

Nostalgia para quem ama games: cadastre os jogos que marcaram época (ano, gênero, consoles, história, capa),
avalie, e veja os próximos lançamentos do mercado.

## Como rodar (Windows)

Dê dois cliques em **`iniciar.bat`**. Ele prepara tudo na primeira vez, liga a API e o front-end e abre
`http://localhost:5173`. Precisa de **Python 3.11+** e **Node.js (LTS)** instalados.

### Ou manualmente (dois terminais)

```
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload       # API em http://localhost:8000  (documentação em /docs)
```
```
cd frontend
npm install
npm run dev                          # http://localhost:5173
```

## Testes

```
cd backend && pytest
```

## O que o sistema faz

Usuário: cadastrar, entrar, sair, escolher idioma (PT/EN).
Usuário logado: cadastrar, editar, excluir (marcada) e restaurar jogo; enviar capa; listar e filtrar; avaliar (nota 1–5 + comentário); ver lançamentos do mercado.
Qualquer usuário logado pode editar/excluir qualquer jogo; o sistema guarda quem cadastrou, alterou e excluiu.

## Estrutura

```
backend/app   dominio/ · casos_de_uso/ · portas/ · adaptadores/ · rotas/   (Arquitetura Limpa)
backend/tests testes do núcleo (sem banco) e da API
frontend/     React + TypeScript (Vite)
docs/         decisões e diagramas
```

| Pasta do back-end | Papel | Pode conhecer |
| --- | --- | --- |
| `dominio/` | Entidades e regras (Usuario, Jogo...) | só ele mesmo |
| `casos_de_uso/` | O que o sistema faz | dominio, portas |
| `portas/` | Contratos que o núcleo exige | dominio, casos_de_uso (formatos de leitura) |
| `adaptadores/` | Implementações: SQL, hash, JWT, pasta de capas, RAWG | portas, dominio |
| `rotas/` | Entrada HTTP (FastAPI) e ligação dos casos de uso aos adaptadores | tudo |

Regra de ouro: `dominio` e `casos_de_uso` nunca importam FastAPI, SQL nem arquivos.

## Segurança

Veja `docs/seguranca.md`: defesas implementadas, riscos aceitos e o que fazer na entrega.

## Configuração (variáveis de ambiente)

| Variável | Padrão | Para quê |
| --- | --- | --- |
| `AMBIENTE` | `desenvolvimento` | Use `producao` no servidor real: a API então se recusa a subir com configuração insegura |
| `DATABASE_URL` | `sqlite:///./jogoteca.db` | Banco. MySQL: `mysql+pymysql://usuario:senha@localhost:3306/jogoteca` (veja `docker-compose.yml`) |
| `JWT_SEGREDO` | valor de desenvolvimento | **Troque em produção** (mínimo 32 caracteres) |
| `JWT_MINUTOS` | `60` | Duração do login |
| `COOKIE_SEGURO` | `false` | `true` quando usar HTTPS |
| `ORIGENS_FRONT` | `http://localhost:5173,...` | Endereços do front liberados (CORS) |
| `PASTA_CAPAS` | `armazenamento/capas` | Onde as capas são guardadas |
| `TWITCH_CLIENT_ID` / `TWITCH_CLIENT_SECRET` | vazio | Chaves do IGDB, para a rotina de lançamentos |
| `RAWG_API_KEY` | vazio | Alternativa ao IGDB |

## Lançamentos do mercado

A tela "Lançamentos" mostra o que a **rotina de lançamentos** gravou no banco. Ela é um processo separado e usa o **IGDB** (da Twitch).

1. Em https://dev.twitch.tv/console crie um aplicativo (a conta Twitch precisa de verificação em duas etapas) e copie o **Client ID** e o **Client Secret**.
2. Dê dois cliques em **`atualizar_lancamentos.bat`**, cole as duas chaves quando pedir e aguarde `N lançamentos atualizados.`
3. Abra a aba Lançamentos no JogoTeca e recarregue.

Pela linha de comando: defina `TWITCH_CLIENT_ID` e `TWITCH_CLIENT_SECRET` e rode `python -m app.rotina_lancamentos` dentro de `backend`.
Alternativa: se só `RAWG_API_KEY` estiver definida, a rotina usa o RAWG.

A rotina busca os **20 jogos mais aguardados** dos próximos 12 meses (pelo número de seguidores no IGDB) e os mostra por data de lançamento. Os cartões mostram a capa do jogo quando o IGDB tem uma (senão, um ícone). Depois de atualizar o sistema, rode a rotina de novo para trazer as capas.

Agende para rodar uma vez por dia (Agendador de Tarefas do Windows ou cron). Se a fonte estiver fora do ar, os
lançamentos anteriores são mantidos.


## Página inicial
`/` é só uma tela de abertura (sem dados do sistema). Tudo o que o sistema mostra exige login. Quem já está logado vai direto para `/jogos`.

## Rodando com Docker
1. Instale o Docker Desktop e deixe-o aberto ("Engine running").
2. (Opcional) copie `.env.example` para `.env` e preencha.
3. Na pasta do projeto: `docker compose up --build`. Site em http://localhost:5173, API em http://localhost:8000/docs.
4. Lançamentos (precisa das chaves da Twitch no `.env`): `docker compose run --rm rotina`.
5. Parar: `docker compose down` (os dados ficam nos volumes; para apagar tudo: `docker compose down -v`).
