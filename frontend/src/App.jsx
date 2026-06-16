import React, { useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import StudyTools from './pages/StudyTools'
import Flashcards from './pages/Flashcards'
import Achievements from './pages/Achievements'
import Analytics from './pages/Analytics'
import Notes from './pages/Notes'
import Planner from './pages/Planner'
import Leaderboard from './pages/Leaderboard'
import StudyAgent from './pages/StudyAgent'
import KnowledgeGraph from './pages/KnowledgeGraph'

function PrivateRoute({ children }) {
  const token = useAuthStore(s => s.token)
  if (!token) return <Navigate to="/login" replace />
  return children
}

function OnboardedRoute({ children }) {
  const { token, onboarded } = useAuthStore()
  if (!token) return <Navigate to="/login" replace />
  if (!onboarded) return <Navigate to="/onboarding" replace />
  return children
}

export default function App() {
  const { theme } = useAuthStore()

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          className: 'dark:bg-slate-800 dark:text-white',
          duration: 3000,
          style: { borderRadius: '12px', fontFamily: 'Inter, sans-serif', fontSize: '14px' }
        }}
      />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/onboarding" element={<PrivateRoute><Onboarding /></PrivateRoute>} />
        <Route path="/" element={<OnboardedRoute><Layout /></OnboardedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="study" element={<StudyTools />} />
          <Route path="flashcards" element={<Flashcards />} />
          <Route path="achievements" element={<Achievements />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="notes" element={<Notes />} />
          <Route path="planner" element={<Planner />} />
          <Route path="leaderboard" element={<Leaderboard />} />
          <Route path="agent" element={<StudyAgent />} />
          <Route path="graph" element={<KnowledgeGraph />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
