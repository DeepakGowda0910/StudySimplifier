import React, { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { getProfile } from '../api/user'
import { getSubjects, getTopics, getChapters } from '../api/study'
import { generateKnowledgeGraph } from '../api/agent'
import { Network, ChevronDown, Info, Loader2, BookOpen, ZoomIn, ZoomOut } from 'lucide-react'
import toast from 'react-hot-toast'

const MASTERY_COLOR = {
  untouched: '#94a3b8',
  weak: '#ef4444',
  learning: '#f59e0b',
  strong: '#3b82f6',
  expert: '#10b981',
}
const MASTERY_BG = {
  untouched: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400',
  weak: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400',
  learning: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400',
  strong: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400',
  expert: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400',
}
const CATEGORY_Y = { foundation: 80, core: 220, advanced: 360, application: 480 }

function computeLayout(nodes) {
  const byCategory = { foundation: [], core: [], advanced: [], application: [] }
  nodes.forEach(n => {
    const cat = n.category || 'core'
    if (byCategory[cat]) byCategory[cat].push(n)
    else byCategory.core.push(n)
  })
  const positioned = {}
  Object.entries(byCategory).forEach(([cat, catNodes]) => {
    const y = CATEGORY_Y[cat] || 300
    const spacing = Math.max(140, 700 / Math.max(catNodes.length, 1))
    catNodes.forEach((n, i) => {
      positioned[n.id] = {
        x: 80 + i * spacing,
        y,
        ...n,
      }
    })
  })
  return positioned
}

function GraphCanvas({ nodes, graphWidth }) {
  const [tooltip, setTooltip] = useState(null)
  const [scale, setScale] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const svgRef = useRef(null)
  const dragging = useRef(false)
  const lastPos = useRef(null)

  const positioned = computeLayout(nodes)

  const edges = []
  nodes.forEach(n => {
    (n.prerequisites || []).forEach(prereq => {
      if (positioned[prereq] && positioned[n.id]) {
        edges.push({ from: prereq, to: n.id })
      }
    })
  })

  const onWheel = (e) => {
    e.preventDefault()
    setScale(s => Math.max(0.4, Math.min(2.5, s - e.deltaY * 0.001)))
  }
  const onMouseDown = (e) => { dragging.current = true; lastPos.current = { x: e.clientX, y: e.clientY } }
  const onMouseMove = (e) => {
    if (!dragging.current) return
    setPan(p => ({ x: p.x + e.clientX - lastPos.current.x, y: p.y + e.clientY - lastPos.current.y }))
    lastPos.current = { x: e.clientX, y: e.clientY }
  }
  const onMouseUp = () => { dragging.current = false }

  useEffect(() => {
    const el = svgRef.current
    if (el) el.addEventListener('wheel', onWheel, { passive: false })
    return () => { if (el) el.removeEventListener('wheel', onWheel) }
  }, [])

  const svgH = 580
  const svgW = Math.max(graphWidth, 800)

  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900" style={{ height: svgH }}>
      {/* Controls */}
      <div className="absolute top-3 right-3 z-10 flex flex-col gap-1.5">
        <button onClick={() => setScale(s => Math.min(2.5, s + 0.15))} className="btn-ghost p-2 bg-white dark:bg-slate-800 shadow rounded-xl"><ZoomIn size={14} /></button>
        <button onClick={() => setScale(s => Math.max(0.4, s - 0.15))} className="btn-ghost p-2 bg-white dark:bg-slate-800 shadow rounded-xl"><ZoomOut size={14} /></button>
        <button onClick={() => { setScale(1); setPan({ x: 0, y: 0 }) }} className="btn-ghost p-2 bg-white dark:bg-slate-800 shadow rounded-xl text-xs font-bold">1:1</button>
      </div>

      {/* Legend */}
      <div className="absolute top-3 left-3 z-10 bg-white dark:bg-slate-800 rounded-xl p-2.5 shadow text-xs space-y-1.5">
        {Object.entries(MASTERY_COLOR).map(([k, c]) => (
          <div key={k} className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full" style={{ background: c }} />
            <span className="text-slate-600 dark:text-slate-400 capitalize">{k}</span>
          </div>
        ))}
      </div>

      <svg
        ref={svgRef}
        width="100%" height={svgH}
        style={{ cursor: dragging.current ? 'grabbing' : 'grab' }}
        onMouseDown={onMouseDown}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
      >
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
            <path d="M0,0 L0,6 L8,3 z" fill="#94a3b8" />
          </marker>
        </defs>
        <g transform={`translate(${pan.x},${pan.y}) scale(${scale})`}>
          {/* Edges */}
          {edges.map((e, i) => {
            const from = positioned[e.from]
            const to = positioned[e.to]
            if (!from || !to) return null
            const mx = (from.x + to.x) / 2
            const my = (from.y + to.y) / 2 - 30
            return (
              <path
                key={i}
                d={`M ${from.x} ${from.y} Q ${mx} ${my} ${to.x} ${to.y}`}
                fill="none"
                stroke="#94a3b8"
                strokeWidth="1.5"
                strokeDasharray="5,4"
                markerEnd="url(#arrow)"
                opacity={0.6}
              />
            )
          })}

          {/* Nodes */}
          {Object.values(positioned).map((node) => {
            const mastery = node.mastery || 'untouched'
            const color = MASTERY_COLOR[mastery]
            const r = 34 + (node.difficulty || 3) * 3
            return (
              <g
                key={node.id}
                transform={`translate(${node.x},${node.y})`}
                style={{ cursor: 'pointer' }}
                onClick={(e) => { e.stopPropagation(); setTooltip(t => t?.id === node.id ? null : node) }}
              >
                <circle r={r} fill={color} fillOpacity={0.15} stroke={color} strokeWidth={2.5} />
                <circle r={r - 6} fill={color} fillOpacity={0.08} />
                <text textAnchor="middle" dominantBaseline="middle" fill={color} fontSize={10} fontWeight="600">
                  {(node.label || node.id).slice(0, 12)}
                </text>
                {node.elo && (
                  <text y={r + 12} textAnchor="middle" fill="#94a3b8" fontSize={9}>
                    ELO {Math.round(node.elo)}
                  </text>
                )}
              </g>
            )
          })}
        </g>
      </svg>

      {/* Tooltip */}
      <AnimatePresence>
        {tooltip && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white dark:bg-slate-800 rounded-xl p-4 shadow-xl border border-slate-100 dark:border-slate-700 text-sm min-w-56 max-w-xs z-20"
          >
            <button onClick={() => setTooltip(null)} className="absolute top-2 right-2 text-slate-400 hover:text-slate-600 text-xs">✕</button>
            <p className="font-bold text-slate-800 dark:text-slate-200 mb-2">{tooltip.label || tooltip.id}</p>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Category</span>
                <span className="font-medium capitalize">{tooltip.category}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Difficulty</span>
                <span className="font-medium">{'⭐'.repeat(tooltip.difficulty || 3)}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Est. Hours</span>
                <span className="font-medium">{tooltip.estimated_hours}h</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-slate-500">Mastery</span>
                <span className={`font-medium capitalize px-1.5 py-0.5 rounded ${MASTERY_BG[tooltip.mastery || 'untouched']}`}>
                  {tooltip.mastery || 'untouched'}
                </span>
              </div>
              {tooltip.elo && (
                <div className="flex justify-between text-xs">
                  <span className="text-slate-500">ELO</span>
                  <span className="font-medium">{Math.round(tooltip.elo)}</span>
                </div>
              )}
              {(tooltip.prerequisites || []).length > 0 && (
                <div className="text-xs mt-2">
                  <span className="text-slate-500">Prerequisites: </span>
                  <span className="text-slate-700 dark:text-slate-300">{tooltip.prerequisites.join(', ')}</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function KnowledgeGraph() {
  const [subject, setSubject] = useState('')
  const [allChapters, setAllChapters] = useState([])
  const [graphData, setGraphData] = useState(null)
  const [generating, setGenerating] = useState(false)

  const { data: profile } = useQuery({ queryKey: ['profile'], queryFn: getProfile })
  const { data: subjects = [] } = useQuery({
    queryKey: ['subjects', profile?.category, profile?.course, profile?.stream],
    queryFn: () => getSubjects(profile.category, profile.course, profile.stream || 'General'),
    enabled: !!profile?.category && !!profile?.course,
  })

  const loadChapters = async (subj) => {
    if (!profile || !subj) return
    try {
      const topics = await import('../api/study').then(m => m.getTopics(profile.category, profile.course, profile.stream || 'General', subj))
      const chapterSets = await Promise.all(
        topics.map(t => import('../api/study').then(m => m.getChapters(profile.category, profile.course, profile.stream || 'General', subj, t)))
      )
      setAllChapters([...new Set(chapterSets.flat())])
    } catch { toast.error('Failed to load chapters') }
  }

  const handleSubjectChange = (s) => {
    setSubject(s)
    setGraphData(null)
    setAllChapters([])
    if (s) loadChapters(s)
  }

  const handleGenerate = async () => {
    if (!subject || !allChapters.length) return
    setGenerating(true)
    try {
      const data = await generateKnowledgeGraph({ subject, course: profile?.course || '', chapters: allChapters })
      setGraphData(data)
    } catch { toast.error('Failed to generate graph') }
    finally { setGenerating(false) }
  }

  const graphWidth = allChapters.length * 150

  return (
    <div className="page-container space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
          <Network size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Knowledge Graph</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm">Visual concept dependency map with mastery tracking</p>
        </div>
      </div>

      {/* Config */}
      <div className="card p-5 flex flex-wrap items-end gap-4">
        <div className="flex-1 min-w-48">
          <label className="label">Subject</label>
          <select className="input text-sm" value={subject} onChange={e => handleSubjectChange(e.target.value)}>
            <option value="">Select a subject</option>
            {subjects.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>
        {allChapters.length > 0 && (
          <div className="text-sm text-slate-500 dark:text-slate-400">
            <span className="font-semibold text-slate-700 dark:text-slate-300">{allChapters.length}</span> chapters loaded
          </div>
        )}
        <button
          onClick={handleGenerate}
          disabled={!subject || !allChapters.length || generating}
          className="btn-primary flex items-center gap-2"
        >
          {generating ? <><Loader2 size={15} className="animate-spin" /> Building Graph…</> : <><Network size={15} /> Generate Graph</>}
        </button>
      </div>

      {/* Legend info */}
      <div className="flex flex-wrap gap-2">
        {Object.entries(MASTERY_BG).map(([k, cls]) => (
          <span key={k} className={`text-xs px-3 py-1 rounded-full font-medium ${cls}`}>{k}</span>
        ))}
        <span className="text-xs px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">Scroll to zoom • Drag to pan • Click node for details</span>
      </div>

      {/* Graph */}
      {generating ? (
        <div className="card p-16 flex flex-col items-center gap-4">
          <div className="w-14 h-14 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
          <p className="text-slate-500 dark:text-slate-400">Building dependency graph with AI…</p>
        </div>
      ) : graphData?.nodes?.length > 0 ? (
        <GraphCanvas nodes={graphData.nodes} graphWidth={graphWidth} />
      ) : (
        <div className="card p-16 flex flex-col items-center gap-4 text-center">
          <div className="w-16 h-16 rounded-2xl bg-blue-100 dark:bg-blue-950 flex items-center justify-center">
            <Network size={28} className="text-blue-500" />
          </div>
          <div>
            <p className="font-semibold text-slate-800 dark:text-slate-200">No graph yet</p>
            <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Select a subject and click Generate Graph to visualize concept dependencies</p>
          </div>
        </div>
      )}
    </div>
  )
}
