import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Eye, EyeOff, School } from 'lucide-react'
import { schoolLogin } from '../../api/school'
import { useAuthStore } from '../../store/authStore'
import toast from 'react-hot-toast'

export default function SchoolLogin() {
  const navigate = useNavigate()
  const setSchoolAuth = useAuthStore(s => s.setSchoolAuth)
  const [form, setForm] = useState({ username: '', password: '' })
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await schoolLogin(form)
      setSchoolAuth(data)
      if (data.role === 'school_admin') navigate('/school/admin')
      else if (data.role === 'school_teacher') navigate('/school/teacher')
      else navigate('/school/student')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-950 to-slate-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <div className="text-left">
              <p className="text-white font-bold text-xl leading-tight">AI School</p>
              <p className="text-indigo-300 text-sm">by StudySmart</p>
            </div>
          </div>
          <p className="text-slate-400 text-sm mt-2">Sign in to your school account</p>
        </div>

        {/* Card */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Username</label>
              <input
                type="text"
                value={form.username}
                onChange={e => setForm(f => ({ ...f, username: e.target.value }))}
                className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition"
                placeholder="Enter your username"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPass ? 'text' : 'password'}
                  value={form.password}
                  onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                  className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 pr-11 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50 transition"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPass(p => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                >
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition-all shadow-lg shadow-indigo-500/20"
            >
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 pt-5 border-t border-white/10 flex flex-col gap-2 text-center text-sm text-slate-400">
            <p>
              Have an invite code?{' '}
              <Link to="/school/join" className="text-indigo-400 hover:text-indigo-300 font-medium">
                Join school
              </Link>
            </p>
            <p>
              Setting up a new school?{' '}
              <Link to="/school/register" className="text-indigo-400 hover:text-indigo-300 font-medium">
                Register school
              </Link>
            </p>
            <p>
              <Link to="/login" className="text-slate-500 hover:text-slate-300">
                ← Back to StudySmart
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
