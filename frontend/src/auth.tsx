import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { json, req, type Usuario } from './api'
import { useIdioma } from './i18n'

interface Ctx {
  usuario: Usuario | null
  carregando: boolean
  entrar: (email: string, senha: string) => Promise<void>
  cadastrar: (nome: string, email: string, senha: string) => Promise<void>
  sair: () => Promise<void>
}
const Auth = createContext<Ctx>(null!)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null)
  const [carregando, setCarregando] = useState(true)
  const { idioma, trocar } = useIdioma()

  useEffect(() => {
    req<Usuario>('/auth/eu')
      .then((u) => { setUsuario(u); trocar(u.idioma) })
      .catch(() => setUsuario(null))
      .finally(() => setCarregando(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Quando o usuário logado troca o idioma, guarda a escolha no servidor.
  useEffect(() => {
    if (usuario && usuario.idioma !== idioma) {
      req<Usuario>('/usuarios/eu/idioma', json('PUT', { idioma })).then(setUsuario).catch(() => {})
    }
  }, [idioma, usuario])

  const entrar = async (email: string, senha: string) => {
    const u = await req<Usuario>('/auth/login', json('POST', { email, senha }))
    setUsuario(u)
    trocar(u.idioma)
  }
  const cadastrar = async (nome: string, email: string, senha: string) => {
    await req('/usuarios', json('POST', { nome, email, senha, idioma }))
    await entrar(email, senha)
  }
  const sair = async () => {
    await req('/auth/logout', { method: 'POST' })
    setUsuario(null)
  }
  return <Auth.Provider value={{ usuario, carregando, entrar, cadastrar, sair }}>{children}</Auth.Provider>
}

export const useAuth = () => useContext(Auth)
