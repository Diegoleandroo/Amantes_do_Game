export const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export interface Usuario { id: number; nome: string; email: string; idioma: 'pt' | 'en' }
export interface Genero { id: number; nome: string }
export interface Faixa { id: number; descricao: string }
export interface Console { id: number; nome: string }
export interface Referencias { generos: Genero[]; faixas_etarias: Faixa[]; consoles: Console[] }
export interface Jogo {
  id: number; nome: string; ano: number; historia: string | null; capa_url: string | null
  genero: Genero; faixa_etaria: { id: number; descricao: string }; consoles: Console[]
  cadastrado_por: string; cadastrado_em: string | null; alterado_por: string | null
  excluido: boolean; excluido_em: string | null; excluido_por: string | null
  nota_media: number | null; total_avaliacoes: number
}
export interface Avaliacao { usuario_id: number; usuario: string; nota: number; comentario: string | null; criada_em: string | null }
export interface Lancamento { id: number; nome: string; capa_url: string | null; plataformas: string; origem: string; data_lancamento: string | null; atualizado_em: string | null }

export class ApiErro extends Error {
  status: number
  codigo: string
  constructor(status: number, codigo: string, mensagem: string) {
    super(mensagem)
    this.status = status
    this.codigo = codigo
  }
}

export async function req<T>(caminho: string, opcoes: RequestInit = {}): Promise<T> {
  let resposta: Response
  try {
    resposta = await fetch(API + caminho, { credentials: 'include', ...opcoes })
  } catch {
    throw new ApiErro(0, 'sem_conexao', 'Sem conexão com a API.')
  }
  if (resposta.status === 204) return null as T
  const corpo = await resposta.json().catch(() => null)
  if (!resposta.ok) {
    const detalhe = typeof corpo?.detalhe === 'string' ? corpo.detalhe : 'Erro inesperado.'
    throw new ApiErro(resposta.status, corpo?.codigo ?? 'erro', detalhe)
  }
  return corpo as T
}

export const json = (metodo: string, dados: unknown): RequestInit => ({
  method: metodo,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(dados),
})

export const capaUrl = (j: { capa_url: string | null }) => (j.capa_url ? API + j.capa_url : null)
