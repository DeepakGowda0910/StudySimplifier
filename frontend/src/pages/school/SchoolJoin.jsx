import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Key, User, Lock } from 'lucide-react'
import { schoolJoin } from '../../api/school'
import { useAuthStore } from '../../store/authStore'
import toast from 'react-hot-toast'

export default function SchoolJoin() {
  const navigate = useNavigate()
  const setSchoolAuth = useAuthStore(s => s.setSchoolAuth)
  const [form, setForm] = useState({ invite_code: '', username: '', password: '', full_name: '', email: '' })
  const [loading, setLoading] = useState(false)

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await schoolJoin({ ...form, invite_code: form.invite_code.trim().toUpperCase() })
      setSchoolAuth(data)
      toast.success(`Welcome to ${data.school_name}!`)
      if (data.role === 'school_teacher') navigate('/school/teacher')
      else navigate('/school/student')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Invalid invite code')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-950 to-slate-900 flex items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <p className="text-white font-bold text-xl">Join Your School</p>
          </div>
          <p className="text-slate-400 text-sm">Use the invite code from your teacher or admin</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                <Key className="w-3 h-3 inline mr-1" />Invite Code *
              </label>
              <input
                type="text" required value={form.invite_code} onChange={e => update('invite_code', e.target.value.toUpperCase())}
                className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition font-mono tracking-widest text-center text-lg uppercase"
                placeholder="ABC12345"
                maxLength={10}
              />
            </div>

            <div className="border-t border-white/10 pt-4">
              <p className="text-xs text-slate-500 mb-4 uppercase tracking-wide font-medium">Create your account</p>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Full Name *</label>
                  <input
                    type="text" required value={form.full_name} onChange={e => update('full_name', e.target.value)}
                    className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                    placeholder="Your full name"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">
                      <User className="w-3 h-3 inline mr-1" />Username *
                    </label>
                    <input
                      type="text" required value={form.username} onChange={e => update('username', e.target.value)}
                      className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                      placeholder="username"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">
                      <Lock className="w-3 h-3 inline mr-1" />Password *
                    </label>
                    <input
                      type="password" required minLength={6} value={form.password} onChange={e => update('password', e.target.value)}
                      className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                      placeholder="Min 6 chars"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Email (optional)</label>
                  <input
                    type="email" value={form.email} onChange={e => update('email', e.target.value)}
                    className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                    placeholder="your@email.com"
                  />
                </div>
              </div>
            </div>

            <button
              type="submit" disabled={loading}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition-all shadow-lg"
            >
              {loading ? 'Joining…' : 'Join School'}
            </button>
          </div>
        </form>

        <p className="text-center text-sm text-slate-500 mt-4">
          Already have an account?{' '}
          <Link to="/school/login" className="text-indigo-400 hover:text-indigo-300">Sign in</Link>
        </p>
      </motion.div>
    </div>
  )
}
