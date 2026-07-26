import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { Plus, Brain, BookOpen, Trash2, RotateCcw, Layers, Wand2, PartyPopper, CheckCircle2 } from 'lucide-react'
import { getAll, getDue, create, generate, review, remove } from '../api/flashcards'

const PERF_BUTTONS = [
  { value: 1, label: 'Again', color: 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-950 dark:text-red-400' },
  { value: 2, label: 'Hard', color: 'bg-orange-100 text-orange-700 hover:bg-orange-200 dark:bg-orange-950 dark:text-orange-400' },
  { value: 3, label: 'Good', color: 'bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-950 dark:text-green-400' },
  { value: 4, label: 'Easy', color: 'bg-navy-100 text-navy-700 hover:bg-navy-200 dark:bg-navy-800 dark:text-navy-300' },
]

function FlipCard({ card, onReview }) {
  const [flipped, setFlipped] = useState(false)
  return (
    <div className="flip-card w-full" style={{ minHeight: 260 }}>
      <div className={`flip-card-inner relative w-full h-64 ${flipped ? 'flipped' : ''}`}>
        {/* Front */}
        <div className="flip-card-front absolute inset-0 card p-6 flex flex-col items-center justify-center text-center cursor-pointer" onClick={() => setFlipped(true)}>
          <p className="text-xs font-semibold text-navy-600 dark:text-navy-300 mb-4 uppercase tracking-wider">
            {card.subject} {card.chapter ? `· ${card.chapter}` : ''}
          </p>
          <p className="text-lg font-semibold text-slate-900 dark:text-white leading-snug">{card.front_text}</p>
          <p className="text-sm text-slate-400 dark:text-slate-500 mt-6">Tap to reveal answer</p>
        </div>
        {/* Back */}
        <div className="flip-card-back absolute inset-0 card bg-navy-50 dark:bg-navy-800 p-6 flex flex-col">
          <p className="text-xs font-semibold text-navy-600 dark:text-navy-300 mb-3 uppercase tracking-wider">Answer</p>
          <p className="text-base text-slate-800 dark:text-slate-200 leading-relaxed flex-1">{card.back_text}</p>
          <div className="flex gap-2 mt-4">
            {PERF_BUTTONS.map(b => (
              <button key={b.value} onClick={() => { onReview(card.id, b.value); setFlipped(false) }}
                className={`flex-1 py-2 rounded-xl text-sm font-semibold transition-all ${b.color}`}>
                {b.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Flashcards() {
  const [tab, setTab] = useState('review')
  const [newCard, setNewCard] = useState({ front_text: '', back_text: '', subject: '', chapter: '' })
  const [genForm, setGenForm] = useState({ subject: '', chapter: '', topic: '', count: 10 })
  const [reviewIdx, setReviewIdx] = useState(0)
  const qc = useQueryClient()

  const { data: due = [], isLoading: dueLoading } = useQuery({ queryKey: ['flashcards-due'], queryFn: getDue })
  const { data: all = [], isLoading: allLoading } = useQuery({ queryKey: ['flashcards-all'], queryFn: getAll })

  const reviewMutation = useMutation({
    mutationFn: ({ id, perf }) => review(id, { performance: perf }),
    onSuccess: (data) => {
      toast.success(`+${data.xp_awarded} XP! Next review in ${data.interval} day${data.interval > 1 ? 's' : ''}`)
      qc.invalidateQueries(['flashcards-due'])
      qc.invalidateQueries(['stats'])
      setReviewIdx(i => i + 1)
    }
  })

  const createMutation = useMutation({
    mutationFn: create,
    onSuccess: () => {
      toast.success('Flashcard created! +2 XP 🃏')
      setNewCard({ front_text: '', back_text: '', subject: '', chapter: '' })
      qc.invalidateQueries(['flashcards-all'])
      qc.invalidateQueries(['stats'])
    }
  })

  const genMutation = useMutation({
    mutationFn: generate,
    onSuccess: (data) => {
      toast.success(`Generated ${data.created} flashcards! +${data.xp_awarded} XP`)
      qc.invalidateQueries(['flashcards-all'])
      qc.invalidateQueries(['stats'])
    }
  })

  const deleteMutation = useMutation({
    mutationFn: remove,
    onSuccess: () => { toast.success('Deleted'); qc.invalidateQueries(['flashcards-all']) }
  })

  const currentCard = due[reviewIdx]
  const doneReview = reviewIdx >= due.length

  return (
    <div className="page-container">
      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-slate-100 dark:bg-navy-800 rounded-xl w-fit mb-6">
        {[
          { id: 'review', label: `Review (${due.length})`, icon: Brain },
          { id: 'create', label: 'Create', icon: Plus },
          { id: 'library', label: `Library (${all.length})`, icon: Layers },
        ].map(t => (
          <button key={t.id} onClick={() => setTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t.id ? 'bg-white dark:bg-navy-700 shadow-sm text-slate-900 dark:text-white' : 'text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'}`}>
            <t.icon size={15} /> {t.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* Review tab */}
        {tab === 'review' && (
          <motion.div key="review" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {dueLoading ? (
              <div className="card p-12 flex items-center justify-center"><div className="w-10 h-10 border-4 border-navy-200 border-t-navy-600 rounded-full animate-spin" /></div>
            ) : due.length === 0 ? (
              <div className="card p-12 text-center">
                <PartyPopper size={40} className="mx-auto mb-4 text-teal-500" />
                <p className="text-xl font-bold text-slate-900 dark:text-white mb-2">All caught up!</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm">No flashcards due for review today. Come back tomorrow!</p>
              </div>
            ) : doneReview ? (
              <div className="card p-12 text-center">
                <CheckCircle2 size={40} className="mx-auto mb-4 text-teal-500" />
                <p className="text-xl font-bold text-slate-900 dark:text-white mb-2">Session complete!</p>
                <p className="text-slate-500 dark:text-slate-400 text-sm mb-4">You reviewed {due.length} flashcards.</p>
                <button onClick={() => setReviewIdx(0)} className="btn-secondary flex items-center gap-2 mx-auto">
                  <RotateCcw size={16} /> Review Again
                </button>
              </div>
            ) : (
              <div className="max-w-xl mx-auto space-y-4">
                <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
                  <span>Card {reviewIdx + 1} of {due.length}</span>
                  <div className="h-1.5 w-48 bg-slate-100 dark:bg-navy-700 rounded-full overflow-hidden">
                    <div className="h-full bg-navy-600 rounded-full transition-all" style={{ width: `${(reviewIdx / due.length) * 100}%` }} />
                  </div>
                </div>
                <FlipCard card={currentCard} onReview={(id, perf) => reviewMutation.mutate({ id, perf })} />
              </div>
            )}
          </motion.div>
        )}

        {/* Create tab */}
        {tab === 'create' && (
          <motion.div key="create" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Manual */}
            <div className="card p-6 space-y-4">
              <h3 className="font-semibold text-slate-900 dark:text-white">Create Manually</h3>
              <div className="grid grid-cols-2 gap-3">
                <div><label className="label">Subject</label><input className="input text-sm" placeholder="e.g. Physics" value={newCard.subject} onChange={e => setNewCard(f => ({ ...f, subject: e.target.value }))} /></div>
                <div><label className="label">Chapter</label><input className="input text-sm" placeholder="e.g. Optics" value={newCard.chapter} onChange={e => setNewCard(f => ({ ...f, chapter: e.target.value }))} /></div>
              </div>
              <div><label className="label">Front (Question)</label><textarea className="input text-sm h-24 resize-none" placeholder="Enter the question or term…" value={newCard.front_text} onChange={e => setNewCard(f => ({ ...f, front_text: e.target.value }))} /></div>
              <div><label className="label">Back (Answer)</label><textarea className="input text-sm h-24 resize-none" placeholder="Enter the answer or definition…" value={newCard.back_text} onChange={e => setNewCard(f => ({ ...f, back_text: e.target.value }))} /></div>
              <button onClick={() => createMutation.mutate(newCard)} disabled={!newCard.front_text || !newCard.back_text || createMutation.isPending} className="btn-primary w-full flex items-center justify-center gap-2">
                {createMutation.isPending ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Plus size={16} />}
                Create Flashcard
              </button>
            </div>

            {/* AI Generate */}
            <div className="card p-6 space-y-4">
              <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                <Wand2 size={18} className="text-navy-500" /> AI Generate
              </h3>
              <div><label className="label">Subject</label><input className="input text-sm" placeholder="e.g. Chemistry" value={genForm.subject} onChange={e => setGenForm(f => ({ ...f, subject: e.target.value }))} /></div>
              <div><label className="label">Chapter</label><input className="input text-sm" placeholder="e.g. Organic Chemistry" value={genForm.chapter} onChange={e => setGenForm(f => ({ ...f, chapter: e.target.value }))} /></div>
              <div><label className="label">Topic (optional)</label><input className="input text-sm" placeholder="e.g. Hydrocarbons" value={genForm.topic} onChange={e => setGenForm(f => ({ ...f, topic: e.target.value }))} /></div>
              <div><label className="label">Number of cards</label>
                <select className="input text-sm" value={genForm.count} onChange={e => setGenForm(f => ({ ...f, count: +e.target.value }))}>
                  {[5,10,15,20].map(n => <option key={n}>{n}</option>)}
                </select>
              </div>
              <button onClick={() => genMutation.mutate(genForm)} disabled={!genForm.subject || !genForm.chapter || genMutation.isPending} className="btn-primary w-full flex items-center justify-center gap-2">
                {genMutation.isPending ? <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating…</> : <><Wand2 size={16} /> Generate with AI</>}
              </button>
            </div>
          </motion.div>
        )}

        {/* Library tab */}
        {tab === 'library' && (
          <motion.div key="library" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {allLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => <div key={i} className="card h-32 shimmer" />)}
              </div>
            ) : all.length === 0 ? (
              <div className="card p-12 text-center">
                <Layers size={40} className="mx-auto mb-4 text-slate-300 dark:text-navy-600" />
                <p className="text-lg font-semibold text-slate-700 dark:text-slate-300">No flashcards yet</p>
                <p className="text-sm text-slate-400 mt-1">Create some to start studying</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {all.map(card => (
                  <div key={card.id} className="card p-4 group">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-xs text-navy-600 dark:text-navy-300 font-medium">{card.subject || 'General'}</span>
                      <button onClick={() => deleteMutation.mutate(card.id)} className="opacity-0 group-hover:opacity-100 transition-opacity btn-ghost p-1 text-red-400 hover:text-red-600">
                        <Trash2 size={14} />
                      </button>
                    </div>
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-200 mb-2 line-clamp-2">{card.front_text}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{card.back_text}</p>
                    <div className="flex items-center gap-3 mt-3 pt-3 border-t border-slate-100 dark:border-navy-700">
                      <span className="text-xs text-slate-400">Reviews: {card.review_count}</span>
                      <span className="text-xs text-slate-400">Next: {card.next_review_date}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
