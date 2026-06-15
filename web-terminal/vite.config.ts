import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base './' so built assets use RELATIVE paths — required for the Tauri
// desktop shell (loads from the asset protocol, not a web root) AND fine for
// the public web deploy.
export default defineConfig({
  plugins: [react()],
  base: './',
  build: { outDir: 'dist', target: 'es2020', sourcemap: false },
  server: { port: 5173 },
})
