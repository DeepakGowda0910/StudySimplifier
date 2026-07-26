import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { ArrowLeft, BarChart3, TrendingUp, Users } from 'lucide-react'
import { getReports } from '../../../api/school'

export default function SchoolReports() {
  const navigate = useNavigate()
  const { data, isLoading } = useQuery({ queryKey: ['reports'], queryFn: getReports })
  const grades = data?.by_grade || []

  const maxStudents = Math.max(...grades.map(g => g.students), 1)

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-white font-semibold">School Reports</h1>
          <BarChart3 className="w-5 h-5 text-emerald-400 ml-auto" />
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-6 space-y-6">
        {isLoading ? (
          <div className="space-y-2">{[...Array(4)].map((_, i) => <div key={i} className="h-20 bg-white/5 rounded-xl animate-pulse" />)}</div>
        ) : grades.length === 0 ? (
          <div className="text-center py-16 text-slate-500">
            <BarChart3 className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No data yet — enroll students to see reports</p>
          </div>
        ) : (
          <>
            {/* Summary */}
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                <Users className="w-5 h-5 text-indigo-400 mx-auto mb-1" />
                <p className="text-xl font-bold">{grades.reduce((a, g) => a + g.students, 0)}</p>
                <p className="text-xs text-slate-500">Total Students</p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                <TrendingUp className="w-5 h-5 text-emerald-400 mx-auto mb-1" />
                <p className="text-xl font-bold">
                  {grades.length ? Math.round(grades.reduce((a, g) => a + g.completion_rate, 0) / grades.length) : 0}%
                </p>
                <p className="text-xs text-slate-500">Avg Completion</p>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-xl p-4 text-center">
                <BarChart3 className="w-5 h-5 text-purple-400 mx-auto mb-1" />
                <p className="text-xl font-bold">{grades.reduce((a, g) => a + g.lessons_completed, 0)}</p>
                <p className="text-xs text-slate-500">Lessons Completed</p>
              </div>
            </div>

            {/* Grade-wise chart */}
            <div className="bg-white/3 border border-white/10 rounded-xl p-5">
              <h2 className="text-white font-semibold mb-5">Completion by Grade</h2>
              <div className="space-y-4">
                {grades.map((g, i) => (
                  <motion.div
                    key={g.grade}
                    initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm font-medium text-slate-300">Grade {g.grade}</span>
                      <div className="flex items-center gap-3 text-xs text-slate-500">
                        <span>{g.students} students</span>
                        <span className={`font-semibold ${g.completion_rate >= 75 ? 'text-emerald-400' : g.completion_rate >= 40 ? 'text-amber-400' : 'text-red-400'}`}>
                          {g.completion_rate}%
                        </span>
                      </div>
                    </div>
                    <div className="h-2.5 bg-white/8 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${g.completion_rate}%` }}
                        transition={{ duration: 0.6, delay: i * 0.05 }}
                        className={`h-full rounded-full ${
                          g.completion_rate >= 75 ? 'bg-emerald-500' :
                          g.completion_rate >= 40 ? 'bg-amber-500' : 'bg-red-500'
                        }`}
                      />
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Table */}
            <div className="bg-white/3 border border-white/10 rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/10">
                    {['Grade', 'Students', 'Completed Lessons', 'Total Attempts', 'Rate'].map(h => (
                      <th key={h} className="text-left text-xs text-slate-500 font-medium px-4 py-3">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {grades.map((g, i) => (
                    <tr key={g.grade} className={`border-b border-white/5 ${i % 2 === 0 ? '' : 'bg-white/2'}`}>
                      <td className="px-4 py-3 text-white font-medium">Grade {g.grade}</td>
                      <td className="px-4 py-3 text-slate-400">{g.students}</td>
                      <td className="px-4 py-3 text-slate-400">{g.lessons_completed}</td>
                      <td className="px-4 py-3 text-slate-400">{g.total_lesson_attempts}</td>
                      <td className="px-4 py-3">
                        <span className={`font-semibold ${g.completion_rate >= 75 ? 'text-emerald-400' : g.completion_rate >= 40 ? 'text-amber-400' : 'text-red-400'}`}>
                          {g.completion_rate}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
