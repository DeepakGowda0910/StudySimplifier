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
import Settings from './pages/Settings'

// School module
import SchoolLogin from './pages/school/SchoolLogin'
import SchoolRegister from './pages/school/SchoolRegister'
import SchoolJoin from './pages/school/SchoolJoin'
import AdminDashboard from './pages/school/admin/AdminDashboard'
import ManageStudents from './pages/school/admin/ManageStudents'
import ManageTeachers from './pages/school/admin/ManageTeachers'
import ManageClasses from './pages/school/admin/ManageClasses'
import SchoolReports from './pages/school/admin/SchoolReports'
import TeacherDashboard from './pages/school/teacher/TeacherDashboard'
import ClassView from './pages/school/teacher/ClassView'
import StudentProgressTeacher from './pages/school/teacher/StudentProgress'
import StudentDashboard from './pages/school/student/StudentDashboard'
import CurriculumPage from './pages/school/student/CurriculumPage'
import LessonView from './pages/school/student/LessonView'
import CodingPlayground from './pages/school/student/CodingPlayground'
import MyProgress from './pages/school/student/MyProgress'
import AITutor from './pages/school/student/AITutor'

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

function SchoolRoute({ children, allowedRoles }) {
  const { token, role } = useAuthStore()
  if (!token) return <Navigate to="/school/login" replace />
  if (allowedRoles && !allowedRoles.includes(role)) {
    // Redirect to the correct dashboard for their role
    if (role === 'school_admin') return <Navigate to="/school/admin" replace />
    if (role === 'school_teacher') return <Navigate to="/school/teacher" replace />
    if (role === 'school_student') return <Navigate to="/school/student" replace />
    return <Navigate to="/school/login" replace />
  }
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
          <Route path="settings" element={<Settings />} />
        </Route>
        {/* School auth (public) */}
        <Route path="/school/login" element={<SchoolLogin />} />
        <Route path="/school/register" element={<SchoolRegister />} />
        <Route path="/school/join" element={<SchoolJoin />} />

        {/* Admin routes */}
        <Route path="/school/admin" element={<SchoolRoute allowedRoles={['school_admin']}><AdminDashboard /></SchoolRoute>} />
        <Route path="/school/admin/students" element={<SchoolRoute allowedRoles={['school_admin']}><ManageStudents /></SchoolRoute>} />
        <Route path="/school/admin/teachers" element={<SchoolRoute allowedRoles={['school_admin']}><ManageTeachers /></SchoolRoute>} />
        <Route path="/school/admin/classes" element={<SchoolRoute allowedRoles={['school_admin']}><ManageClasses /></SchoolRoute>} />
        <Route path="/school/admin/reports" element={<SchoolRoute allowedRoles={['school_admin']}><SchoolReports /></SchoolRoute>} />

        {/* Teacher routes */}
        <Route path="/school/teacher" element={<SchoolRoute allowedRoles={['school_teacher', 'school_admin']}><TeacherDashboard /></SchoolRoute>} />
        <Route path="/school/teacher/classes" element={<SchoolRoute allowedRoles={['school_teacher', 'school_admin']}><TeacherDashboard /></SchoolRoute>} />
        <Route path="/school/teacher/class/:classId" element={<SchoolRoute allowedRoles={['school_teacher', 'school_admin']}><ClassView /></SchoolRoute>} />
        <Route path="/school/teacher/student/:studentId" element={<SchoolRoute allowedRoles={['school_teacher', 'school_admin']}><StudentProgressTeacher /></SchoolRoute>} />

        {/* Student routes */}
        <Route path="/school/student" element={<SchoolRoute allowedRoles={['school_student', 'school_teacher', 'school_admin']}><StudentDashboard /></SchoolRoute>} />
        <Route path="/school/student/curriculum" element={<SchoolRoute allowedRoles={['school_student', 'school_teacher', 'school_admin']}><CurriculumPage /></SchoolRoute>} />
        <Route path="/school/student/lesson/:lessonId" element={<SchoolRoute allowedRoles={['school_student', 'school_teacher', 'school_admin']}><LessonView /></SchoolRoute>} />
        <Route path="/school/student/playground" element={<SchoolRoute allowedRoles={['school_student', 'school_teacher', 'school_admin']}><CodingPlayground /></SchoolRoute>} />
        <Route path="/school/student/progress" element={<SchoolRoute allowedRoles={['school_student', 'school_teacher', 'school_admin']}><MyProgress /></SchoolRoute>} />
        <Route path="/school/student/tutor" element={<SchoolRoute allowedRoles={['school_student', 'school_teacher', 'school_admin']}><AITutor /></SchoolRoute>} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
