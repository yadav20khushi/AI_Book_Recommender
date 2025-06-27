import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage1 from './pages/HomePage1'
import KeywordPage from './pages/KeywordPage'
import ResultsPage from './pages/ResultsPage'
import ClovaChatPage from './pages/ClovaChatPage'
import AgeGroupPage from './pages/AgeGroupPage'
import BestsellerPage from './pages/BestsellerPage'
import SignupPage from './pages/SignupPage'
import LoginPage from './pages/LoginPage'
import ReturningUserPage from './pages/ReturningUserPage'
import SearchBar from './components/SearchBar'

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/home" element={<HomePage1 />} />
        <Route path="/keyword" element={<KeywordPage />} />
        <Route path="/result" element={<ResultsPage />} />
        <Route path="/clova-chat" element={<ClovaChatPage />} />
        <Route path="/age-group" element={<AgeGroupPage />} />
        <Route path="/bestsellers" element={<BestsellerPage />} />
        <Route path="/returning" element={<ReturningUserPage />} />
        <Route path="/searchbar" element={<SearchBar />} />
      </Routes>
    </Router>
  )
}
