import { useState } from 'react'
import { motion } from 'framer-motion'
import { Copy, Check, Plus, Key, Users, GraduationCap } from 'lucide-react'
import { generateInvites, listInvites } from '../../api/school'
import toast from 'react-hot-toast'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

export default function InviteCodePanel() {
  const qc = useQueryClient()
  const [form, setForm] = useState({ role: 'school_student', grade: 6, count: 5 })
  const [copied, setCopied] = useState(null)

  const { data: invites = [] } = useQuery({ queryKey: ['invites'], queryFn: listInvites })

  const generate = useMutation({
    mutationFn: () => generateInvites(form),
    onSuccess: () => {
      qc.invalidateQueries(['invites'])
      toast.success(`${form.count} invite code${form.count > 1 ? 's' : ''} generated!`)
    },
    onError: e => toast.error(e.response?.data?.detail || 'Failed'),
  })

  const copyCode = (code) => {
    navigator.clipboard.writeText(code)
    setCopied(code)
    setTimeout(() => setCopied(null), 2000)
  }

  const unused = invites.filter(i => !i.is_used)
  const used = invites.filter(i => i.is_used)

  return (
    <div className="space-y-6">
      {/* Generate form */}
      <div className="bg-white/5 border border-white/10 rounded-xl p-5">
        <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
          <Key className="w-4 h-4 text-indigo-400" /> Generate Invite Codes
        </h3>
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Role</label>
            <select
              value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))}
              className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500"
            >
              <option value="school_student" className="bg-slate-800">Student</option>
              <option value="school_teacher" className="bg-slate-800">Teacher</option>
            </select>
          </div>
          {form.role === 'school_student' && (
            <div>
              <label className="text-xs text-slate-400 mb-1 block">Grade</label>
              <select
                value={form.grade} onChange={e => setForm(f => ({ ...f, grade: parseInt(e.target.value) }))}
                className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500"
              >
                {[6,7,8,9,10,11,12].map(g => (
                  <option key={g} value={g} className="bg-slate-800">Grade {g}</option>
                ))}
              </select>
            </div>
          )}
          <div>
            <label className="text-xs text-slate-400 mb-1 block">Count (max 50)</label>
            <input
              type="number" min={1} max={50} value={form.count}
              onChange={e => setForm(f => ({ ...f, count: parseInt(e.target.value) }))}
              className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>
        <button
          onClick={() => generate.mutate()}
          disabled={generate.isPending}
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg transition"
        >
          <Plus className="w-4 h-4" /> {generate.isPending ? 'Generating…' : 'Generate Codes'}
        </button>
      </div>

      {/* Unused codes */}
      {unused.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
            <Users className="w-4 h-4" /> Available Codes ({unused.length})
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {unused.map(invite => (
              <motion.div
                key={invite.id}
                layout
                className="flex items-center justify-between bg-white/5 border border-white/10 rounded-lg px-3 py-2"
              >
                <div>
                  <p className="font-mono text-sm font-bold text-indigo-300">{invite.invite_code}</p>
                  <p className="text-xs text-slate-500">
                    {invite.role === 'school_student' ? `Student · Grade ${invite.grade}` : 'Teacher'}
                  </p>
                </div>
                <button
                  onClick={() => copyCode(invite.invite_code)}
                  className="text-slate-400 hover:text-white transition ml-2"
                >
                  {copied === invite.invite_code ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Used codes summary */}
      {used.length > 0 && (
        <p className="text-xs text-slate-600">{used.length} code{used.length > 1 ? 's' : ''} already used</p>
      )}
    </div>
  )
}
