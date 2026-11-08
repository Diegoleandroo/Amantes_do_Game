import { createContext, useContext, useState, type ReactNode } from 'react'

type Idioma = 'pt' | 'en'

const textos = {
  pt: {
    nav_jogos: 'Jogos', nav_lancamentos: 'Lançamentos', sair: 'Sair', entrar: 'Entrar', cadastrar_se: 'Criar conta',
    lema: 'Nostalgia para quem ama games.', aperte_start: 'JOGADOR 1', palavras: 'DIVERSÃO|DESAFIO|LAZER|PRÓXIMA FASE', pergunta: 'Pronto para o próximo desafio?', nivel: 'NÍVEL', voltar_inicio: 'Voltar ao início',
    nome: 'Nome', email: 'E-mail', senha: 'Senha', senha_dica: 'Mínimo de 8 caracteres.',
    login_titulo: 'Entrar no JogoTeca', login_sem_conta: 'Ainda não tem conta?', cadastro_titulo: 'Criar conta',
    cadastro_com_conta: 'Já tem conta?', salvar: 'Salvar', cancelar: 'Cancelar', carregando: 'Carregando...',
    jogos_titulo: 'Meus jogos de ontem e de sempre', novo_jogo: 'Cadastrar jogo', buscar: 'Buscar por nome',
    todos_generos: 'Todos os gêneros', todas_faixas: 'Todas as faixas', todos_consoles: 'Todos os consoles', ano: 'Ano',
    mostrar_excluidos: 'Mostrar excluídos', nenhum_jogo: 'Nenhum jogo encontrado. Que tal cadastrar o primeiro?',
    editar: 'Editar', excluir: 'Excluir', restaurar: 'Restaurar', excluido: 'Excluído',
    confirmar_excluir: 'Excluir este jogo? Você poderá restaurá-lo depois.',
    genero: 'Gênero', faixa: 'Faixa etária', consoles: 'Consoles', historia: 'História do jogo', capa: 'Capa (JPG, PNG ou WEBP, até 2 MB)',
    escolha: 'Escolha...', editar_jogo: 'Editar jogo', sem_avaliacao: 'Sem avaliações', avaliacoes: 'avaliações', avaliacao: 'avaliação',
    voltar: 'Voltar', cadastrado_por: 'Cadastrado por', alterado_por: 'Última alteração por', excluido_por: 'Excluído por',
    avaliar: 'Avaliar este jogo', sua_nota: 'Sua nota', comentario: 'Comentário (opcional)', enviar_avaliacao: 'Enviar avaliação',
    sem_avaliacoes_ainda: 'Ninguém avaliou ainda. Já jogou? Seja o primeiro!',
    lancamentos_titulo: 'Chegando ao mercado', lancamentos_sub: 'Os jogos mais aguardados dos próximos 12 meses', lancamentos_vazio: 'Ainda não há lançamentos. A rotina de lançamentos precisa rodar (veja o README).',
    plataformas: 'Plataformas', data_a_definir: 'Data a definir', fonte_dados: 'Dados de',
    atualizado_em: 'Atualizado em', salvo: 'Salvo!',
    'erro.sem_conexao': 'Não consegui falar com a API. Ela está rodando?',
    'erro.credenciais_invalidas': 'E-mail ou senha incorretos.', 'erro.email_em_uso': 'Já existe uma conta com este e-mail.',
    'erro.email_invalido': 'E-mail inválido.', 'erro.senha_curta': 'A senha precisa ter pelo menos 8 caracteres.',
    'erro.nome_invalido': 'O nome deve ter entre 2 e 80 caracteres.', 'erro.jogo_nome_repetido': 'Já existe um jogo com este nome.',
    'erro.jogo_console': 'Escolha pelo menos um console.', 'erro.capa_tipo': 'A capa deve ser JPG, PNG ou WEBP.',
    'erro.capa_grande': 'A capa deve ter no máximo 2 MB.', 'erro.jogo_ano': 'Ano inválido.',
    'erro.nao_autenticado': 'Faça login para continuar.',
    'erro.muitas_tentativas': 'Muitas tentativas de login. Aguarde alguns minutos e tente de novo.',
    'erro.origem_invalida': 'Pedido recusado por segurança.', 'erro.requisicao_grande': 'Arquivo grande demais.',
  },
  en: {
    nav_jogos: 'Games', nav_lancamentos: 'Upcoming', sair: 'Log out', entrar: 'Log in', cadastrar_se: 'Sign up',
    lema: 'Nostalgia for game lovers.', aperte_start: 'PLAYER 1', palavras: 'FUN|CHALLENGE|LEISURE|NEXT LEVEL', pergunta: 'Ready for the next challenge?', nivel: 'LEVEL', voltar_inicio: 'Back to start',
    nome: 'Name', email: 'E-mail', senha: 'Password', senha_dica: 'At least 8 characters.',
    login_titulo: 'Log in to JogoTeca', login_sem_conta: "Don't have an account?", cadastro_titulo: 'Create account',
    cadastro_com_conta: 'Already have an account?', salvar: 'Save', cancelar: 'Cancel', carregando: 'Loading...',
    jogos_titulo: 'My games, then and now', novo_jogo: 'Add game', buscar: 'Search by name',
    todos_generos: 'All genres', todas_faixas: 'All ratings', todos_consoles: 'All consoles', ano: 'Year',
    mostrar_excluidos: 'Show deleted', nenhum_jogo: 'No games found. Why not add the first one?',
    editar: 'Edit', excluir: 'Delete', restaurar: 'Restore', excluido: 'Deleted',
    confirmar_excluir: 'Delete this game? You can restore it later.',
    genero: 'Genre', faixa: 'Age rating', consoles: 'Consoles', historia: 'Game story', capa: 'Cover (JPG, PNG or WEBP, up to 2 MB)',
    escolha: 'Choose...', editar_jogo: 'Edit game', sem_avaliacao: 'No reviews', avaliacoes: 'reviews', avaliacao: 'review',
    voltar: 'Back', cadastrado_por: 'Added by', alterado_por: 'Last changed by', excluido_por: 'Deleted by',
    avaliar: 'Review this game', sua_nota: 'Your rating', comentario: 'Comment (optional)', enviar_avaliacao: 'Send review',
    sem_avaliacoes_ainda: 'No reviews yet. Played it? Be the first!',
    lancamentos_titulo: 'Coming to the market', lancamentos_sub: 'The most anticipated games of the next 12 months', lancamentos_vazio: 'No upcoming games yet. The releases routine needs to run (see the README).',
    plataformas: 'Platforms', data_a_definir: 'Date to be announced', fonte_dados: 'Data from',
    atualizado_em: 'Updated on', salvo: 'Saved!',
    'erro.sem_conexao': "Couldn't reach the API. Is it running?",
    'erro.credenciais_invalidas': 'Wrong e-mail or password.', 'erro.email_em_uso': 'An account with this e-mail already exists.',
    'erro.email_invalido': 'Invalid e-mail.', 'erro.senha_curta': 'The password needs at least 8 characters.',
    'erro.nome_invalido': 'The name must be 2 to 80 characters.', 'erro.jogo_nome_repetido': 'A game with this name already exists.',
    'erro.jogo_console': 'Choose at least one console.', 'erro.capa_tipo': 'The cover must be JPG, PNG or WEBP.',
    'erro.capa_grande': 'The cover must be at most 2 MB.', 'erro.jogo_ano': 'Invalid year.',
    'erro.nao_autenticado': 'Please log in to continue.',
    'erro.muitas_tentativas': 'Too many login attempts. Wait a few minutes and try again.',
    'erro.origem_invalida': 'Request refused for security reasons.', 'erro.requisicao_grande': 'File too large.',
  },
} as const

type Chave = keyof (typeof textos)['pt']

interface Ctx { idioma: Idioma; trocar: (i: Idioma) => void; t: (k: Chave) => string; erro: (codigo: string, padrao: string) => string }
const I18n = createContext<Ctx>(null!)

export function IdiomaProvider({ children }: { children: ReactNode }) {
  const [idioma, setIdioma] = useState<Idioma>(() => {
    try { return localStorage.getItem('idioma') === 'en' ? 'en' : 'pt' } catch { return 'pt' }
  })
  const trocar = (i: Idioma) => {
    setIdioma(i)
    try { localStorage.setItem('idioma', i) } catch { /* sem armazenamento: tudo bem */ }
  }
  const t = (k: Chave) => textos[idioma][k]
  const erro = (codigo: string, padrao: string) => (textos[idioma] as Record<string, string>)['erro.' + codigo] ?? padrao
  return <I18n.Provider value={{ idioma, trocar, t, erro }}>{children}</I18n.Provider>
}

export const useIdioma = () => useContext(I18n)
