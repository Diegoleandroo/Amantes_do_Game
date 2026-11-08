import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ApiErro, capaUrl, json, req, type Avaliacao, type Jogo, type Lancamento, type Referencias } from './api'
import { useAuth } from './auth'
import { Erro, Estrelas } from './componentes'
import { useIdioma } from './i18n'

function useReferencias() {
  const [refs, setRefs] = useState<Referencias | null>(null)
  useEffect(() => { req<Referencias>('/referencias').then(setRefs).catch(() => {}) }, [])
  return refs
}

function Capa({ jogo }: { jogo: Jogo }) {
  const url = capaUrl(jogo)
  return url ? <img className="capa" src={url} alt={jogo.nome} /> : <div className="capa sem-capa" aria-hidden>🎮</div>
}

// ---------- lista + filtros ----------
export function ListaJogos() {
  const { t, erro } = useIdioma()
  const refs = useReferencias()
  const [jogos, setJogos] = useState<Jogo[] | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  const [f, setF] = useState({ texto: '', genero_id: '', faixa_etaria_id: '', console_id: '', ano: '', incluir_excluidos: false })

  const carregar = useCallback(() => {
    const p = new URLSearchParams()
    Object.entries(f).forEach(([k, v]) => { if (v !== '' && v !== false) p.set(k, String(v)) })
    req<Jogo[]>('/jogos?' + p).then((j) => { setJogos(j); setMsg(null) })
      .catch((x) => setMsg(x instanceof ApiErro ? erro(x.codigo, x.message) : String(x)))
  }, [f, erro])
  useEffect(() => { const id = setTimeout(carregar, 200); return () => clearTimeout(id) }, [carregar])

  const acao = async (jogo: Jogo, tipo: 'excluir' | 'restaurar') => {
    if (tipo === 'excluir' && !window.confirm(t('confirmar_excluir'))) return
    try {
      await (tipo === 'excluir' ? req(`/jogos/${jogo.id}`, { method: 'DELETE' }) : req(`/jogos/${jogo.id}/restaurar`, { method: 'POST' }))
      carregar()
    } catch (x) { setMsg(x instanceof ApiErro ? erro(x.codigo, x.message) : String(x)) }
  }
  const set = (campo: string, valor: string | boolean) => setF({ ...f, [campo]: valor })

  return (
    <>
      <div className="titulo-linha">
        <h1>{t('jogos_titulo')}</h1>
        <Link className="btn" to="/jogos/novo">+ {t('novo_jogo')}</Link>
      </div>
      <div className="filtros cartao">
        <input placeholder={t('buscar')} value={f.texto} onChange={(e) => set('texto', e.target.value)} />
        <select value={f.genero_id} onChange={(e) => set('genero_id', e.target.value)}>
          <option value="">{t('todos_generos')}</option>{refs?.generos.map((g) => <option key={g.id} value={g.id}>{g.nome}</option>)}
        </select>
        <select value={f.faixa_etaria_id} onChange={(e) => set('faixa_etaria_id', e.target.value)}>
          <option value="">{t('todas_faixas')}</option>{refs?.faixas_etarias.map((x) => <option key={x.id} value={x.id}>{x.descricao}</option>)}
        </select>
        <select value={f.console_id} onChange={(e) => set('console_id', e.target.value)}>
          <option value="">{t('todos_consoles')}</option>{refs?.consoles.map((c) => <option key={c.id} value={c.id}>{c.nome}</option>)}
        </select>
        <input type="number" placeholder={t('ano')} min={1950} value={f.ano} onChange={(e) => set('ano', e.target.value)} />
        <label className="check"><input type="checkbox" checked={f.incluir_excluidos} onChange={(e) => set('incluir_excluidos', e.target.checked)} /> {t('mostrar_excluidos')}</label>
      </div>
      <Erro texto={msg} />
      {jogos === null ? <p className="aviso">{t('carregando')}</p> : jogos.length === 0 ? <p className="aviso">{t('nenhum_jogo')}</p> : (
        <div className="grade">
          {jogos.map((j) => (
            <article key={j.id} className={'jogo cartao' + (j.excluido ? ' excluido' : '')}>
              <Link to={`/jogos/${j.id}`}><Capa jogo={j} /></Link>
              <div className="jogo-info">
                <h2><Link to={`/jogos/${j.id}`}>{j.nome}</Link></h2>
                <p className="meta">{j.ano} · {j.genero.nome} <span className="faixa">{j.faixa_etaria.descricao}</span></p>
                <p className="chips">{j.consoles.map((c) => <span key={c.id}>{c.nome}</span>)}</p>
                <p className="meta">{j.nota_media ? <><Estrelas nota={j.nota_media} /> {j.nota_media} ({j.total_avaliacoes})</> : t('sem_avaliacao')}</p>
                {j.excluido && <p className="selo">{t('excluido')}</p>}
              </div>
              <div className="acoes">
                {j.excluido
                  ? <button className="btn secundario" onClick={() => acao(j, 'restaurar')}>{t('restaurar')}</button>
                  : <><Link className="btn secundario" to={`/jogos/${j.id}/editar`}>{t('editar')}</Link>
                    <button className="btn perigo" onClick={() => acao(j, 'excluir')}>{t('excluir')}</button></>}
              </div>
            </article>
          ))}
        </div>
      )}
    </>
  )
}

// ---------- cadastrar / editar ----------
export function FormJogo() {
  const { id } = useParams()
  const editando = Boolean(id)
  const { t, erro } = useIdioma()
  const nav = useNavigate()
  const refs = useReferencias()
  const [msg, setMsg] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [c, setC] = useState({ nome: '', ano: '', historia: '', genero_id: '', faixa_etaria_id: '' })
  const [consoles, setConsoles] = useState<number[]>([])
  const [arquivo, setArquivo] = useState<File | null>(null)
  const [capaAtual, setCapaAtual] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    req<Jogo>(`/jogos/${id}`).then((j) => {
      setC({ nome: j.nome, ano: String(j.ano), historia: j.historia ?? '', genero_id: String(j.genero.id), faixa_etaria_id: String(j.faixa_etaria.id) })
      setConsoles(j.consoles.map((x) => x.id)); setCapaAtual(capaUrl(j))
    }).catch((x) => setMsg(x instanceof ApiErro ? erro(x.codigo, x.message) : String(x)))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const enviar = async (e: FormEvent) => {
    e.preventDefault()
    setMsg(null); setEnviando(true)
    const dados = new FormData()
    dados.set('nome', c.nome); dados.set('ano', c.ano); dados.set('genero_id', c.genero_id)
    dados.set('faixa_etaria_id', c.faixa_etaria_id); dados.set('historia', c.historia)
    consoles.forEach((x) => dados.append('console_ids', String(x)))
    if (arquivo) dados.set('capa', arquivo)
    try {
      const salvo = await req<Jogo>(editando ? `/jogos/${id}` : '/jogos', { method: editando ? 'PUT' : 'POST', body: dados })
      nav(`/jogos/${salvo.id}`)
    } catch (x) {
      setMsg(x instanceof ApiErro ? erro(x.codigo, x.message) : String(x))
    } finally { setEnviando(false) }
  }
  const alternar = (cid: number) => setConsoles(consoles.includes(cid) ? consoles.filter((x) => x !== cid) : [...consoles, cid])
  const previa = arquivo ? URL.createObjectURL(arquivo) : capaAtual

  return (
    <form className="cartao formulario" onSubmit={enviar}>
      <h1>{editando ? t('editar_jogo') : t('novo_jogo')}</h1>
      <label>{t('nome')}<input value={c.nome} onChange={(e) => setC({ ...c, nome: e.target.value })} required maxLength={120} autoFocus /></label>
      <div className="linha">
        <label>{t('ano')}<input type="number" min={1950} max={new Date().getFullYear() + 1} value={c.ano} onChange={(e) => setC({ ...c, ano: e.target.value })} required /></label>
        <label>{t('genero')}<select value={c.genero_id} onChange={(e) => setC({ ...c, genero_id: e.target.value })} required>
          <option value="">{t('escolha')}</option>{refs?.generos.map((g) => <option key={g.id} value={g.id}>{g.nome}</option>)}</select></label>
        <label>{t('faixa')}<select value={c.faixa_etaria_id} onChange={(e) => setC({ ...c, faixa_etaria_id: e.target.value })} required>
          <option value="">{t('escolha')}</option>{refs?.faixas_etarias.map((x) => <option key={x.id} value={x.id}>{x.descricao}</option>)}</select></label>
      </div>
      <fieldset><legend>{t('consoles')}</legend>
        <div className="consoles">{refs?.consoles.map((x) => (
          <label key={x.id} className="check"><input type="checkbox" checked={consoles.includes(x.id)} onChange={() => alternar(x.id)} /> {x.nome}</label>))}</div>
      </fieldset>
      <label>{t('historia')}<textarea rows={5} maxLength={5000} value={c.historia} onChange={(e) => setC({ ...c, historia: e.target.value })} /></label>
      <label>{t('capa')}<input type="file" accept="image/jpeg,image/png,image/webp" onChange={(e) => setArquivo(e.target.files?.[0] ?? null)} /></label>
      {previa && <img className="previa" src={previa} alt="" />}
      <Erro texto={msg} />
      <div className="acoes-form">
        <button className="btn" type="submit" disabled={enviando}>{t('salvar')}</button>
        <Link className="btn secundario" to={editando ? `/jogos/${id}` : '/'}>{t('cancelar')}</Link>
      </div>
    </form>
  )
}

// ---------- detalhe + avaliações ----------
export function DetalheJogo() {
  const { id } = useParams()
  const { usuario } = useAuth()
  const { t, erro } = useIdioma()
  const [jogo, setJogo] = useState<Jogo | null>(null)
  const [avals, setAvals] = useState<Avaliacao[]>([])
  const [nota, setNota] = useState(0)
  const [comentario, setComentario] = useState('')
  const [msg, setMsg] = useState<string | null>(null)
  const [ok, setOk] = useState(false)

  const carregar = useCallback(async () => {
    try {
      const [j, a] = await Promise.all([req<Jogo>(`/jogos/${id}`), req<Avaliacao[]>(`/jogos/${id}/avaliacoes`)])
      setJogo(j); setAvals(a)
      const minha = a.find((x) => x.usuario_id === usuario?.id)
      if (minha) { setNota(minha.nota); setComentario(minha.comentario ?? '') }
    } catch (x) { setMsg(x instanceof ApiErro ? erro(x.codigo, x.message) : String(x)) }
  }, [id, usuario?.id, erro])
  useEffect(() => { carregar() }, [carregar])

  const avaliar = async (e: FormEvent) => {
    e.preventDefault()
    setMsg(null); setOk(false)
    try { await req(`/jogos/${id}/avaliacao`, json('PUT', { nota, comentario })); setOk(true); carregar() }
    catch (x) { setMsg(x instanceof ApiErro ? erro(x.codigo, x.message) : String(x)) }
  }

  if (!jogo) return <><Erro texto={msg} /><p className="aviso">{msg ? '' : t('carregando')}</p></>
  return (
    <>
      <p><Link to="/jogos">← {t('voltar')}</Link></p>
      <section className="detalhe cartao">
        <Capa jogo={jogo} />
        <div>
          <h1>{jogo.nome} {jogo.excluido && <span className="selo">{t('excluido')}</span>}</h1>
          <p className="meta">{jogo.ano} · {jogo.genero.nome} <span className="faixa">{jogo.faixa_etaria.descricao}</span></p>
          <p className="chips">{jogo.consoles.map((c) => <span key={c.id}>{c.nome}</span>)}</p>
          <p>{jogo.nota_media ? <><Estrelas nota={jogo.nota_media} /> {jogo.nota_media} ({jogo.total_avaliacoes} {t(jogo.total_avaliacoes === 1 ? 'avaliacao' : 'avaliacoes')})</> : t('sem_avaliacao')}</p>
          {jogo.historia && <><h3>{t('historia')}</h3><p className="historia">{jogo.historia}</p></>}
          <p className="meta">{t('cadastrado_por')} {jogo.cadastrado_por}
            {jogo.alterado_por && <> · {t('alterado_por')} {jogo.alterado_por}</>}
            {jogo.excluido_por && <> · {t('excluido_por')} {jogo.excluido_por}</>}</p>
          {!jogo.excluido && <Link className="btn secundario" to={`/jogos/${jogo.id}/editar`}>{t('editar')}</Link>}
        </div>
      </section>

      {!jogo.excluido && (
        <form className="cartao formulario" onSubmit={avaliar}>
          <h2>{t('avaliar')}</h2>
          <div className="nota" role="radiogroup" aria-label={t('sua_nota')}>
            {[1, 2, 3, 4, 5].map((n) => (
              <button type="button" key={n} className={n <= nota ? 'ligada' : ''} onClick={() => setNota(n)} aria-label={`${n}`}>★</button>))}
          </div>
          <label>{t('comentario')}<textarea rows={3} maxLength={1000} value={comentario} onChange={(e) => setComentario(e.target.value)} /></label>
          <Erro texto={msg} />
          {ok && <p className="ok">{t('salvo')}</p>}
          <button className="btn" type="submit" disabled={nota === 0}>{t('enviar_avaliacao')}</button>
        </form>
      )}

      <section className="avaliacoes">
        {avals.length === 0 ? <p className="aviso">{t('sem_avaliacoes_ainda')}</p> : avals.map((a) => (
          <div className="cartao aval" key={a.usuario_id}>
            <strong>{a.usuario}</strong> <Estrelas nota={a.nota} />
            {a.comentario && <p>{a.comentario}</p>}
          </div>))}
      </section>
    </>
  )
}

// ---------- lançamentos ----------
function CapaLancamento({ url, nome }: { url: string | null; nome: string }) {
  const [falhou, setFalhou] = useState(false)
  return url && !falhou
    ? <img className="capa" src={url} alt={nome} loading="lazy" referrerPolicy="no-referrer" onError={() => setFalhou(true)} />
    : <div className="capa sem-capa" aria-hidden>🎮</div>
}

export function Lancamentos() {
  const { t, idioma, erro } = useIdioma()
  const [itens, setItens] = useState<Lancamento[] | null>(null)
  const [msg, setMsg] = useState<string | null>(null)
  useEffect(() => {
    req<Lancamento[]>('/lancamentos').then(setItens)
      .catch((x) => setMsg(x instanceof ApiErro ? erro(x.codigo, x.message) : String(x)))
  }, [erro])
  const origem = itens?.[0]?.origem ?? 'IGDB'
  const data = (d: string | null) => d ? new Date(d + 'T00:00:00').toLocaleDateString(idioma === 'pt' ? 'pt-BR' : 'en-US') : t('data_a_definir')
  return (
    <>
      <h1>{t('lancamentos_titulo')}</h1>
      <p className="meta sub">{t('lancamentos_sub')}</p>
      <Erro texto={msg} />
      {itens && itens.length === 0 && <p className="aviso">{t('lancamentos_vazio')}</p>}
      <div className="grade">
        {itens?.map((l) => (
          <article className="cartao lancamento" key={l.id}>
            <CapaLancamento url={l.capa_url} nome={l.nome} />
            <p className="data">{data(l.data_lancamento)}</p>
            <h2>{l.nome}</h2>
            {l.plataformas && <p className="chips">{l.plataformas.split(', ').map((p) => <span key={p}>{p}</span>)}</p>}
          </article>))}
      </div>
      <p className="atribuicao">{t('fonte_dados')} <a href={origem === 'RAWG' ? 'https://rawg.io' : 'https://www.igdb.com'} target="_blank" rel="noreferrer">{origem}</a></p>
    </>
  )
}
