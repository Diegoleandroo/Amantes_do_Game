# Segurança do JogoTeca

O que protege o sistema, onde está no código e o que ainda depende da entrega.

## Já implementado (com teste)

| Ameaça | Defesa | Onde |
| --- | --- | --- |
| Senha vazada do banco | Hash scrypt com sal aleatório; a senha nunca é guardada nem devolvida | `adaptadores/hash_senha`, `rotas/formatos.py` |
| Adivinhar senhas (força bruta) | 5 falhas seguidas do mesmo IP + e-mail bloqueiam por 15 min (HTTP 429), mesmo com a senha certa | `adaptadores/limitador`, `casos_de_uso/usuarios.py` |
| Descobrir quais e-mails existem pelo login | Mesma mensagem para e-mail ou senha errados, e mesmo tempo de resposta | `FazerLogin`, `HashScrypt.simular` |
| Roubo do token por script malicioso (XSS) | Token em cookie `HttpOnly`; o React não usa HTML cru | `rotas/api.py`, front sem `dangerouslySetInnerHTML` |
| Pedidos forjados por outro site (CSRF) | Cookie `SameSite=Lax`, CORS só para o front permitido e conferência do cabeçalho `Origin` | `main.py` |
| Token adulterado ou expirado | Assinatura HS256 verificada; expira em 60 min | `adaptadores/token_jwt` |
| Arquivo malicioso disfarçado de capa | Tipo conferido pelo conteúdo (JPG/PNG/WEBP), máximo 2 MB, nome do arquivo gerado pelo servidor; `nosniff` | `dominio/regras.py`, `armazenamento_capas` |
| Upload gigante para derrubar o servidor | Recusa acima de 3 MB antes de processar (HTTP 413) | `main.py` |
| Injeção de SQL | Todas as consultas usam parâmetros (SQLAlchemy) | `persistencia/repositorios.py` |
| Embutir a API em outra página, adivinhação de tipo | Cabeçalhos `X-Frame-Options`, `X-Content-Type-Options`, `CSP`, `Referrer-Policy` | `main.py` |
| Subir em produção com configuração fraca | Com `AMBIENTE=producao`, a API recusa subir sem segredo próprio (32+), cookie seguro e origens `https` | `config.py` |
| Biblioteca com falha conhecida | `pip-audit` e `npm audit` sem vulnerabilidades na data da entrega | rodar de novo antes de cada entrega |

## Riscos conhecidos e aceitos por enquanto

- **Logout não invalida o token já emitido** (JWT não guarda estado). Mitigação: duração curta de 60 min. Para invalidar de verdade, é preciso uma lista de tokens revogados.
- **O limitador de tentativas fica na memória de um processo.** Com várias instâncias da API, troque por um adaptador com Redis (a porta é a mesma).
- **Atrás de um proxy ou balanceador, o IP visto é o do proxy.** Será preciso configurar os cabeçalhos `X-Forwarded-For` de um proxy confiável.
- **O cadastro revela se um e-mail já existe** (409). É uma escolha comum para dar boa experiência; o login não revela.
- **Qualquer usuário logado pode editar e excluir qualquer jogo**: é regra de negócio decidida, com auditoria de quem fez.
- **As tabelas são criadas automaticamente**, sem migrações versionadas. Antes de ter dados reais, adotar Alembic.

## Para a fase de entrega

1. HTTPS obrigatório (certificado) e `COOKIE_SEGURO=true`, `AMBIENTE=producao`.
2. `JWT_SEGREDO` único e guardado no cofre de segredos da hospedagem, nunca no código.
3. Chaves da Twitch/IGDB também como segredos; gerar de novo qualquer chave que já tenha sido exibida em tela ou conversa.
4. Banco MySQL com usuário de permissões mínimas e backup automático.
5. Capas em armazenamento em nuvem, com acesso de leitura pública só aos arquivos.
6. Registro (logs) de erros e de bloqueios de login; alertas simples.
7. Rodar `pip-audit` e `npm audit` no pipeline a cada alteração.
