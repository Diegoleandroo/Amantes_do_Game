import { useEffect, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useAuth } from './auth'
import { useIdioma } from './i18n'

const CORES = ['#5bff6b', '#ffd23f', '#ff4fa3', '#35e0d0']

// Controle de videogame: os botões acendem em sequência; clicar (ou tocar) solta um "+10".
function Controle() {
  const [pops, setPops] = useState<{ id: number; x: number; y: number; cor: string }[]>([])
  const botoes = [[236, 62], [262, 88], [236, 114], [210, 88]] as const
  const apertar = (x: number, y: number, cor: string) => {
    const id = Date.now() + Math.random()
    setPops((p) => [...p, { id, x, y, cor }])
    setTimeout(() => setPops((p) => p.filter((q) => q.id !== id)), 900)
  }
  return (
    <div className="controle" aria-hidden>
      <svg viewBox="0 0 320 200" role="img">
        <path d="M70 40H250C285 40 305 80 310 140C314 175 290 190 270 170L245 140H75L50 170C30 190 6 175 10 140C15 80 35 40 70 40Z" fill="#1b1535" stroke="#35e0d0" strokeWidth="4" />
        <path d="M70 50H250" stroke="#35e0d055" strokeWidth="3" />
        <g fill="#35e0d0"><rect x="70" y="80" width="14" height="46" rx="3" /><rect x="54" y="96" width="46" height="14" rx="3" /></g>
        <circle cx="128" cy="130" r="17" fill="#0c0a17" stroke="#ff4fa3" strokeWidth="3" /><circle cx="128" cy="130" r="8" fill="#ff4fa3" />
        <circle cx="192" cy="130" r="17" fill="#0c0a17" stroke="#ff4fa3" strokeWidth="3" /><circle cx="192" cy="130" r="8" fill="#ff4fa3" />
        <rect x="140" y="70" width="14" height="6" rx="3" fill="#a9a4d0" /><rect x="166" y="70" width="14" height="6" rx="3" fill="#a9a4d0" />
        {botoes.map(([x, y], i) => (
          <circle key={i} className="botao" cx={x} cy={y} r="12" fill={CORES[i]} style={{ animationDelay: `${i * 0.45}s`, color: CORES[i] }}
            onClick={() => apertar(x, y, CORES[i])} />))}
      </svg>
      {pops.map((p) => <span key={p.id} className="pop" style={{ left: `${p.x / 3.2}%`, top: `${p.y / 2}%`, color: p.cor }}>+10</span>)}
    </div>
  )
}

// Palavras que giram (diversão, desafio, lazer...) e a barra de experiência que enche.
function Palavras() {
  const { t } = useIdioma()
  const lista = t('palavras').split('|')
  const [i, setI] = useState(0)
  useEffect(() => { const id = setInterval(() => setI((x) => (x + 1) % lista.length), 1800); return () => clearInterval(id) }, [lista.length])
  return (
    <>
      <p className="palavra" key={i} style={{ color: CORES[i % CORES.length] }}>{lista[i]}</p>
      <div className="xp" aria-hidden><span>{t('nivel')} {i + 1}</span><div><i key={i} /></div></div>
    </>
  )
}

// Tela de abertura: só visual. Não carrega nenhum dado do sistema.
export function Inicio() {
  const { usuario, carregando } = useAuth()
  const { t } = useIdioma()
  if (carregando) return <p className="aviso">{t('carregando')}</p>
  if (usuario) return <Navigate to="/jogos" replace />
  return (
    <div className="abertura">
      <Controle />
      <p className="moeda">▶ {t('aperte_start')}</p>
      <h1 className="marca">Jogo<span>Teca</span></h1>
      <Palavras />
      <p className="pergunta">{t('pergunta')}</p>
      <div className="abertura-botoes">
        <Link className="btn-arcade" to="/cadastro">{t('cadastrar_se')}</Link>
        <Link className="btn-arcade alt" to="/login">{t('entrar')}</Link>
      </div>
    </div>
  )
}
