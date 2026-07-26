import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Users, GraduationCap, BarChart3, Key, Settings, BookOpen, ArrowRight, School } from 'lucide-react'
import { getAdminOverview } from '../../../api/school'
import { useAuthStore } from '../../../store/authStore'
import InviteCodePanel from '../../../components/school/InviteCodePanel'

export default function AdminDashboard() {
  const navigate = useNavigate()
  const { schoolName, fullName, username } = useAuthStore()
  const { data, isLoading } = useQuery({ queryKey: ['admin-overview'], queryFn: getAdminOverview })

  const stats = [
    { icon: Users, label: 'Students', value: data?.total_students ?? '—', color: 'text-indigo-400' },
    { icon: GraduationCap, label: 'Teachers', value: data?.total_teachers ?? '—', color: 'text-teal-400' },
    { icon: BookOpen, label: 'Classes', value: data?.total_classes ?? '—', color: 'text-purple-400' },
    { icon: BarChart3, label: 'Completion', value: data ? `${data.avg_completion_rate}%` : '—', color: 'text-emerald-400' },
  ]

  const navCards = [
    { icon: Users, label: 'Manage Students', desc: 'View all students, their grade & progress', path: '/school/admin/students', color: 'from-indigo-600/30 to-indigo-800/20 border-indigo-500/30' },
    { icon: GraduationCap, label: 'Manage Teachers', desc: 'Add/remove teachers, view their classes', path: '/school/admin/teachers', color: 'from-teal-600/30 to-teal-800/20 border-teal-500/30' },
    { icon: BookOpen, label: 'Manage Classes', desc: 'Create class sections, assign teachers', path: '/school/admin/classes', color: 'from-purple-600/30 to-purple-800/20 border-purple-500/30' },
    { icon: BarChart3, label: 'Reports', desc: 'Grade-wise completion rates', path: '/school/admin/reports', color: 'from-emerald-600/30 to-emerald-800/20 border-emerald-500/30' },
  ]

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-950 via-purple-950 to-slate-950 border-b border-white/10">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <School className="w-5 h-5 text-indigo-400" />
                <p className="text-slate-400 text-sm">{schoolName}</p>
              </div>
              <h1 className="text-2xl font-bold text-white">Admin Dashboard</h1>
              <p className="text-slate-400 text-sm mt-1">Welcome, {fullName || username}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        {/* Stats */}
        <div className="grid grid-cols-4 gap-4">
          {stats.map(({ icon: Icon, label, value, color }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-white/5 border border-white/10 rounded-xl p-4 text-center"
            >
              <Icon className={`w-6 h-6 ${color} mx-auto mb-1.5`} />
              <p className="text-2xl font-bold text-white">{isLoading ? '…' : value}</p>
              <p className="text-xs text-slate-500">{label}</p>
            </motion.div>
          ))}
        </div>

        {/* Nav cards */}
        <div className="grid grid-cols-2 gap-4">
          {navCards.map(({ icon: Icon, label, desc, path, color }, i) => (
            <motion.button
              key={label}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + i * 0.05 }}
              onClick={() => navigate(path)}
              className={`bg-gradient-to-br ${color} border rounded-xl p-5 text-left hover:scale-[1.02] transition-transform group`}
            >
              <div className="flex items-start justify-between">
                <Icon className="w-6 h-6 text-white/70 mb-3" />
                <ArrowRight className="w-4 h-4 text-white/30 group-hover:text-white/60 transition" />
              </div>
              <p className="text-white font-semibold">{label}</p>
              <p className="text-white/50 text-xs mt-1">{desc}</p>
            </motion.button>
          ))}
        </div>

        {/* Invite code panel */}
        <div className="bg-white/3 border border-white/10 rounded-xl p-5">
          <h2 className="text-white font-semibold mb-4 flex items-center gap-2">
            <Key className="w-5 h-5 text-yellow-400" /> Invite Codes
          </h2>
          <InviteCodePanel />
        </div>
      </div>
    </div>
  )
}
