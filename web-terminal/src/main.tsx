import React from 'react'
import ReactDOM from 'react-dom/client'
// Plus Jakarta Sans — SELF-HOSTED (board condition: no third-party font CDN;
// bank proxies block Google Fonts and the EU flags it — bundled woff2 instead)
import '@fontsource/plus-jakarta-sans/400.css'
import '@fontsource/plus-jakarta-sans/500.css'
import '@fontsource/plus-jakarta-sans/600.css'
import '@fontsource/plus-jakarta-sans/700.css'
import '@fontsource/plus-jakarta-sans/800.css'
import './tailwind.css'
import './styles.css'
import { App } from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
