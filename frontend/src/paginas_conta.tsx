import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { ApiErro } from './api'
import { useAuth } from './auth'
import { Erro } from './componentes'
import { useIdioma } from './i18n'

export function Login() {
  const { usuario, entrar } = useAuth()
  const { t, erro } = useIdioma()
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [msg, setMsg] = useState<string | null>(null)
  if (usuario) return <Navigate to="/jogos" replace />

  const enviar = async (e: FormEvent) => {
    e.preventDefault()
    setMsg(null)
    try { await entrar(email, senha); nav('/jogos') }
    catch (x) { setMsg(x instanceof ApiErro ? erro(x.codigo, x.message) : String(x)) }
  }
  return (
    <form className="cartao formulario estreito" onSubmit={enviar}>
      <h1>{t('login_titulo')}</h1>
      <p className="lema">{t('lema')}</p>
      <label>{t('email')}<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoFocus /></label>
      <label>{t('senha')}<input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required /></label>
      <Erro texto={msg} />
      <button className="btn" type="submit">{t('entrar')}</button>
      <p className="rodape-form">{t('login_sem_conta')} <Link to="/cadastro">{t('cadastrar_se')}</Link></p>
    </form>
  )
}

export function Cadastro() {
  const { usuario, cadastrar } = useAuth()
  const { t, erro } = useIdioma()
  const nav = useNavigate()
  const [nome, setNome] = useState('')
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [msg, setMsg] = useState<string | null>(null)
  if (usuario) return <Navigate to="/jogos" replace />

  const enviar = async (e: FormEvent) => {
    e.preventDefault()
    setMsg(null)
    try { await cadastrar(nome, email, senha); nav('/jogos') }
    catch (x) { setMsg(x instanceof ApiErro ? erro(x.codigo, x.message) : String(x)) }
  }
  return (
    <form className="cartao formulario estreito" onSubmit={enviar}>
      <h1>{t('cadastro_titulo')}</h1>
      <label>{t('nome')}<input value={nome} onChange={(e) => setNome(e.target.value)} required minLength={2} maxLength={80} autoFocus /></label>
      <label>{t('email')}<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
      <label>{t('senha')}<input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required minLength={8} maxLength={128} />
        <small>{t('senha_dica')}</small></label>
      <Erro texto={msg} />
      <button className="btn" type="submit">{t('cadastrar_se')}</button>
      <p className="rodape-form">{t('cadastro_com_conta')} <Link to="/login">{t('entrar')}</Link></p>
    </form>
  )
}
