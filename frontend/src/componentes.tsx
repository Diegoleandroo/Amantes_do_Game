import type { ReactNode } from 'react'
import { Link, NavLink, Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './auth'
import { useIdioma } from './i18n'

export function SeletorIdioma() {
  const { idioma, trocar } = useIdioma()
  return (
    <div className="idioma" role="group" aria-label="Idioma / Language">
      {(['pt', 'en'] as const).map((i) => (
        <button key={i} className={idioma === i ? 'ativo' : ''} onClick={() => trocar(i)}>{i.toUpperCase()}</button>
      ))}
    </div>
  )
}

const FLUTUANTES = [['🕹️', 6, 62, 4.2], ['👾', 88, 55, 3.6], ['🎮', 14, 22, 5], ['🏆', 80, 18, 4.6], ['🚀', 92, 80, 3.9], ['⭐', 4, 84, 4.4], ['💾', 70, 70, 5.2]] as const

export function Palco({ children, inicio = false }: { children: ReactNode; inicio?: boolean }) {
  const { t } = useIdioma()
  return (
    <div className="palco">
      <div className="chao" aria-hidden />
      <div className="flutuantes" aria-hidden>
        {FLUTUANTES.map(([ic, x, y, d], i) => <span key={i} style={{ left: `${x}%`, top: `${y}%`, animationDuration: `${d}s`, animationDelay: `${i * -0.7}s` }}>{ic}</span>)}
      </div>
      {!inicio && <Link className="voltar-inicio" to="/">◀ {t('voltar_inicio')}</Link>}
      <SeletorIdioma />
      {children}
    </div>
  )
}

export function Layout() {
  const { usuario, sair } = useAuth()
  const { t } = useIdioma()
  const { pathname } = useLocation()
  // Visitante: só a tela de abertura, o login e o cadastro (nada do sistema aparece)
  if (!usuario) return <Palco inicio={pathname === '/'}><Outlet /></Palco>
  return (
    <>
      <header className="topo">
        <Link to="/" className="logo">JogoTeca</Link>
        {usuario && (
          <nav>
            <NavLink to="/jogos" end>{t('nav_jogos')}</NavLink>
            <NavLink to="/lancamentos">{t('nav_lancamentos')}</NavLink>
          </nav>
        )}
        <div className="topo-direita">
          <SeletorIdioma />
          {usuario && (
            <>
              <span className="quem">{usuario.nome}</span>
              <button className="btn secundario" onClick={sair}>{t('sair')}</button>
            </>
          )}
        </div>
      </header>
      <main className="conteudo"><Outlet /></main>
    </>
  )
}

export function Protegida({ children }: { children: ReactNode }) {
  const { usuario, carregando } = useAuth()
  const { t } = useIdioma()
  if (carregando) return <p className="aviso">{t('carregando')}</p>
  return usuario ? <>{children}</> : <Navigate to="/login" replace />
}

export function Estrelas({ nota }: { nota: number | null }) {
  const n = Math.round(nota ?? 0)
  return <span className="estrelas" aria-label={nota ? `${nota}/5` : ''}>{'★'.repeat(n)}<i>{'★'.repeat(5 - n)}</i></span>
}

export function Erro({ texto }: { texto: string | null }) {
  return texto ? <p className="erro" role="alert">{texto}</p> : null
}
