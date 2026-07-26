import React, { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { Play, Pause, RotateCcw, Check, Flame } from 'lucide-react'
import { recordPomodoro, getPomodoroStats } from '../../api/planner'
import { useQuery, useQueryClient } from '@tanstack/react-query'

const MODES = [
  { label: 'Focus', duration: 25, color: '#2e4d7a' },
  { label: 'Short Break', duration: 5, color: '#10b981' },
  { label: 'Long Break', duration: 15, color: '#0d9488' },
]

export default function PomodoroTimer() {
  const [modeIdx, setModeIdx] = useState(0)
  const [secondsLeft, setSecondsLeft] = useState(MODES[0].duration * 60)
  const [running, setRunning] = useState(false)
  const [subject, setSubject] = useState('')
  const [sessions, setSessions] = useState(0)
  const intervalRef = useRef(null)
  const qc = useQueryClient()

  const { data: stats } = useQuery({ queryKey: ['pomodoro-stats'], queryFn: getPomodoroStats })
  const mode = MODES[modeIdx]
  const total = mode.duration * 60
  const progress = (secondsLeft / total) * 100
  const mins = Math.floor(secondsLeft / 60).toString().padStart(2, '0')
  const secs = (secondsLeft % 60).toString().padStart(2, '0')
  const circumference = 2 * Math.PI * 90

  useEffect(() => {
    setSecondsLeft(mode.duration * 60)
    setRunning(false)
    clearInterval(intervalRef.current)
  }, [modeIdx])

  useEffect(() => {
    if (running) {
      intervalRef.current = setInterval(() => {
        setSecondsLeft(s => {
          if (s <= 1) {
            clearInterval(intervalRef.current)
            setRunning(false)
            handleComplete()
            return 0
          }
          return s - 1
        })
      }, 1000)
    } else {
      clearInterval(intervalRef.current)
    }
    return () => clearInterval(intervalRef.current)
  }, [running])

  const handleComplete = async () => {
    toast.success(modeIdx === 0 ? `Focus session complete! +${Math.floor(mode.duration / 5)} XP` : 'Break over! Ready to focus?', { duration: 5000 })
    if (modeIdx === 0) {
      setSessions(s => s + 1)
      try {
        await recordPomodoro(subject, mode.duration)
        qc.invalidateQueries(['pomodoro-stats'])
        qc.invalidateQueries(['stats'])
      } catch {}
    }
  }

  const reset = () => {
    setRunning(false)
    setSecondsLeft(mode.duration * 60)
  }

  const strokeDashoffset = circumference - (circumference * (1 - progress / 100))

  return (
    <div className="max-w-lg mx-auto space-y-6">
      {/* Mode selector */}
      <div className="flex gap-2 p-1 bg-slate-100 dark:bg-navy-800 rounded-xl">
        {MODES.map((m, i) => (
          <button key={i} onClick={() => setModeIdx(i)}
            className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${modeIdx === i ? 'bg-white dark:bg-navy-700 shadow-sm text-slate-900 dark:text-white' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}>
            {m.label}
          </button>
        ))}
      </div>

      {/* Timer ring */}
      <div className="card p-8 flex flex-col items-center gap-6">
        <div className="relative w-52 h-52">
          <svg className="w-full h-full pomodoro-ring" viewBox="0 0 200 200">
            <circle cx="100" cy="100" r="90" fill="none" stroke="#f1f5f9" strokeWidth="10" className="dark:[stroke:#0f1c33]" />
            <motion.circle
              cx="100" cy="100" r="90" fill="none"
              stroke={mode.color} strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              animate={{ strokeDashoffset }}
              transition={{ duration: 0.5, ease: 'linear' }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <p className="text-5xl font-bold font-mono text-slate-900 dark:text-white tracking-tight">{mins}:{secs}</p>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{mode.label}</p>
          </div>
        </div>

        {/* Subject input */}
        <input className="input text-sm text-center w-full max-w-xs" placeholder="What are you studying?" value={subject} onChange={e => setSubject(e.target.value)} />

        {/* Controls */}
        <div className="flex items-center gap-3">
          <button onClick={reset} className="btn-secondary p-3 rounded-xl"><RotateCcw size={20} /></button>
          <button onClick={() => setRunning(r => !r)}
            className="w-14 h-14 rounded-2xl flex items-center justify-center text-white shadow-lg transition-all active:scale-95"
            style={{ background: mode.color }}>
            {running ? <Pause size={24} /> : <Play size={24} fill="currentColor" />}
          </button>
          <button onClick={() => { setRunning(false); handleComplete() }} className="btn-secondary p-3 rounded-xl" title="Mark complete">
            <Check size={20} />
          </button>
        </div>

        {/* Session count */}
        <div className="flex items-center gap-2">
          {[...Array(4)].map((_, i) => (
            <div key={i} className={`w-3 h-3 rounded-full ${i < sessions % 4 ? 'bg-navy-600' : 'bg-slate-200 dark:bg-navy-700'}`} />
          ))}
          <span className="text-sm text-slate-500 dark:text-slate-400 ml-2">{sessions} sessions today</span>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="card p-5">
          <h3 className="font-semibold text-slate-900 dark:text-white mb-3 text-sm">All-time Pomodoro Stats</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-red-50 dark:bg-red-950 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-red-600 dark:text-red-400 flex items-center justify-center gap-1.5"><Flame size={20} /> {stats.total_sessions}</p>
              <p className="text-xs text-slate-500 mt-1">Total Sessions</p>
            </div>
            <div className="bg-navy-50 dark:bg-navy-800 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-navy-600 dark:text-navy-300">{Math.floor(stats.total_minutes / 60)}h</p>
              <p className="text-xs text-slate-500 mt-1">Focus Time</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
