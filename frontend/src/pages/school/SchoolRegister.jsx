import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Building2, User, Mail, Lock, MapPin, GraduationCap } from 'lucide-react'
import { schoolRegister } from '../../api/school'
import { useAuthStore } from '../../store/authStore'
import toast from 'react-hot-toast'

const BOARDS = ['CBSE', 'ICSE', 'IGCSE', 'State Board (Maharashtra)', 'State Board (Karnataka)',
  'State Board (Tamil Nadu)', 'State Board (UP)', 'State Board (Rajasthan)', 'Other']

export default function SchoolRegister() {
  const navigate = useNavigate()
  const setSchoolAuth = useAuthStore(s => s.setSchoolAuth)
  const [step, setStep] = useState(1)
  const [form, setForm] = useState({
    name: '', city: '', board: '',
    admin_username: '', admin_email: '', admin_password: '', admin_full_name: ''
  })
  const [loading, setLoading] = useState(false)

  const update = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await schoolRegister(form)
      setSchoolAuth(data)
      toast.success(`${form.name} is now registered!`)
      navigate('/school/admin')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-purple-950 to-slate-900 flex items-center justify-center p-4">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-lg">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Brain className="w-7 h-7 text-white" />
            </div>
            <p className="text-white font-bold text-xl">Register Your School</p>
          </div>
          <p className="text-slate-400 text-sm">Bring AI education to every student in your school</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center gap-2 mb-6 justify-center">
          {[1, 2].map(s => (
            <div key={s} className={`flex items-center ${s < 2 ? 'flex-1' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
                step >= s ? 'bg-indigo-600 text-white' : 'bg-white/10 text-slate-500'
              }`}>{s}</div>
              {s < 2 && <div className={`flex-1 h-0.5 mx-2 ${step > s ? 'bg-indigo-600' : 'bg-white/10'}`} />}
            </div>
          ))}
        </div>

        <form onSubmit={handleSubmit}>
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8 shadow-2xl space-y-5">
            {step === 1 && (
              <>
                <h2 className="text-white font-semibold text-lg flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-indigo-400" /> School Details
                </h2>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">School Name *</label>
                  <input
                    type="text" required value={form.name} onChange={e => update('name', e.target.value)}
                    className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                    placeholder="e.g. St. Mary's High School"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">
                      <MapPin className="w-3 h-3 inline mr-1" />City
                    </label>
                    <input
                      type="text" value={form.city} onChange={e => update('city', e.target.value)}
                      className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                      placeholder="Mumbai"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">
                      <GraduationCap className="w-3 h-3 inline mr-1" />Board
                    </label>
                    <select
                      value={form.board} onChange={e => update('board', e.target.value)}
                      className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition"
                    >
                      <option value="">Select board</option>
                      {BOARDS.map(b => <option key={b} value={b} className="bg-slate-800">{b}</option>)}
                    </select>
                  </div>
                </div>
                <button
                  type="button" onClick={() => { if (!form.name) { toast.error('School name required'); return } setStep(2) }}
                  className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold py-3 rounded-xl transition-all"
                >
                  Next: Admin Account →
                </button>
              </>
            )}

            {step === 2 && (
              <>
                <h2 className="text-white font-semibold text-lg flex items-center gap-2">
                  <User className="w-5 h-5 text-indigo-400" /> Admin Account
                </h2>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">Full Name *</label>
                  <input
                    type="text" required value={form.admin_full_name} onChange={e => update('admin_full_name', e.target.value)}
                    className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                    placeholder="Your full name"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">Username *</label>
                    <input
                      type="text" required value={form.admin_username} onChange={e => update('admin_username', e.target.value)}
                      className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                      placeholder="admin_user"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1.5">
                      <Mail className="w-3 h-3 inline mr-1" />Email *
                    </label>
                    <input
                      type="email" required value={form.admin_email} onChange={e => update('admin_email', e.target.value)}
                      className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                      placeholder="admin@school.edu"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">
                    <Lock className="w-3 h-3 inline mr-1" />Password *
                  </label>
                  <input
                    type="password" required minLength={6} value={form.admin_password} onChange={e => update('admin_password', e.target.value)}
                    className="w-full bg-white/5 border border-white/15 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition"
                    placeholder="Min 6 characters"
                  />
                </div>
                <div className="flex gap-3">
                  <button
                    type="button" onClick={() => setStep(1)}
                    className="flex-1 bg-white/5 hover:bg-white/10 text-slate-300 font-medium py-3 rounded-xl transition"
                  >
                    ← Back
                  </button>
                  <button
                    type="submit" disabled={loading}
                    className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:opacity-60 text-white font-semibold py-3 rounded-xl transition-all"
                  >
                    {loading ? 'Creating…' : 'Register School'}
                  </button>
                </div>
              </>
            )}
          </div>
        </form>

        <p className="text-center text-sm text-slate-500 mt-4">
          Already registered?{' '}
          <Link to="/school/login" className="text-indigo-400 hover:text-indigo-300">Sign in</Link>
        </p>
      </motion.div>
    </div>
  )
}
