import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ClovaChatProvider } from './context/ClovaChatContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ClovaChatProvider>
      <App />
    </ClovaChatProvider>
  </StrictMode>,
)
