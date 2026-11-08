import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// A API libera exatamente a porta 5173 (CORS), por isso a porta é fixa.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, strictPort: true },
})
