import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Users, BookOpen, ClipboardList, ArrowRight, BarChart3, Brain } from 'lucide-react'
import { getTeacherDashboard } from '../../../api/school'
import { useAuthStore } from '../../../store/authStore'

export default function TeacherDashboard() {
  const navigate = useNavigate()
  const { fullName, username, schoolName } = useAuthStore()
  const { data, isLoading } = useQuery({ queryKey: ['teacher-dashboard'], queryFn: getTeacherDashboard })

  const classes = data?.classes || []

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-teal-950 via-emerald-950 to-slate-950 border-b border-white/10">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <p className="text-slate-400 text-sm">{schoolName} · Teacher Dashboard</p>
          <h1 className="text-2xl font-bold text-white mt-1">Welcome, {fullName || username}</h1>
          <p className="text-slate-400 text-sm mt-1">{classes.length} class{classes.length !== 1 ? 'es' : ''} assigned</p>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-6">
        {/* Quick actions */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { icon: Users, label: 'My Classes', desc: 'View all assigned classes', path: '/school/teacher/classes', color: 'from-teal-600 to-emerald-700' },
            { icon: BarChart3, label: 'Progress', desc: 'Track student completion', path: '/school/teacher/classes', color: 'from-indigo-600 to-blue-700' },
            { icon: ClipboardList, label: 'Assignments', desc: 'Assign lessons to classes', path: '/school/teacher/classes', color: 'from-purple-600 to-violet-700' },
          ].map(({ icon: Icon, label, desc, path, color }, i) => (
            <motion.button
              key={label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => navigate(path)}
              className={`bg-gradient-to-br ${color} p-5 rounded-xl text-left hover:scale-105 transition-transform`}
            >
              <Icon className="w-6 h-6 text-white/80 mb-3" />
              <p className="text-white font-semibold">{label}</p>
              <p className="text-white/60 text-xs mt-1">{desc}</p>
            </motion.button>
          ))}
        </div>

        {/* My Classes */}
        <div>
          <h2 className="text-white font-semibold mb-3">My Classes</h2>
          {isLoading ? (
            <div className="space-y-2">{[...Array(3)].map((_, i) => <div key={i} className="h-16 bg-white/5 rounded-xl animate-pulse" />)}</div>
          ) : classes.length === 0 ? (
            <div className="text-center py-12 bg-white/3 border border-white/10 rounded-xl">
              <Users className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-slate-500">No classes assigned yet</p>
              <p className="text-xs text-slate-600 mt-1">Your school admin will assign classes to you</p>
            </div>
          ) : (
            <div className="space-y-2">
              {classes.map((cls, i) => (
                <motion.div
                  key={cls.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.04 }}
                  onClick={() => navigate(`/school/teacher/class/${cls.id}`)}
                  className="flex items-center justify-between bg-white/5 border border-white/10 hover:border-teal-500/40 rounded-xl px-5 py-4 cursor-pointer transition group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-teal-500/15 flex items-center justify-center">
                      <span className="text-teal-400 font-bold">{cls.grade}</span>
                    </div>
                    <div>
                      <p className="text-white font-medium">Grade {cls.grade} — {cls.section_name}</p>
                      <p className="text-xs text-slate-500">{cls.academic_year} · {cls.student_count || 0} students</p>
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-600 group-hover:text-teal-400 transition" />
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
