import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth'
import { Layout, Protegida } from './componentes'
import { IdiomaProvider } from './i18n'
import { Inicio } from './pagina_inicio'
import { Cadastro, Login } from './paginas_conta'
import { DetalheJogo, FormJogo, ListaJogos, Lancamentos } from './paginas_jogos'
import './estilos.css'

export default function App() {
  return (
    <IdiomaProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<Layout />}>
              <Route path="/login" element={<Login />} />
              <Route path="/cadastro" element={<Cadastro />} />
              <Route path="/" element={<Inicio />} />
              <Route path="/jogos" element={<Protegida><ListaJogos /></Protegida>} />
              <Route path="/jogos/novo" element={<Protegida><FormJogo /></Protegida>} />
              <Route path="/jogos/:id" element={<Protegida><DetalheJogo /></Protegida>} />
              <Route path="/jogos/:id/editar" element={<Protegida><FormJogo /></Protegida>} />
              <Route path="/lancamentos" element={<Protegida><Lancamentos /></Protegida>} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </IdiomaProvider>
  )
}
