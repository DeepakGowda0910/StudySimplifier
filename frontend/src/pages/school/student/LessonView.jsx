import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, CheckCircle2, Clock, Code, FileText, HelpCircle, Rocket, Trophy } from 'lucide-react'
import { getLesson, completeLesson } from '../../../api/curriculum'
import CodeEditor from '../../../components/school/CodeEditor'
import InteractiveQuiz from '../../../components/school/InteractiveQuiz'
import toast from 'react-hot-toast'

const TYPE_ICONS = { text: FileText, coding: Code, quiz: HelpCircle, project: Rocket }

export default function LessonView() {
  const { lessonId } = useParams()
  const navigate = useNavigate()
  const qc = useQueryClient()
  const [quizScore, setQuizScore] = useState(null)
  const [startTime] = useState(Date.now())

  const { data: lesson, isLoading } = useQuery({
    queryKey: ['lesson', lessonId],
    queryFn: () => getLesson(parseInt(lessonId)),
  })

  const complete = useMutation({
    mutationFn: (score) => completeLesson(parseInt(lessonId), {
      lesson_id: parseInt(lessonId),
      status: 'completed',
      score,
      time_spent_mins: Math.round((Date.now() - startTime) / 60000),
    }),
    onSuccess: () => {
      qc.invalidateQueries(['student-dashboard'])
      qc.invalidateQueries(['curriculum'])
      toast.success('Lesson completed!')
    },
  })

  if (isLoading) return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <p className="text-slate-400">Loading lesson…</p>
    </div>
  )

  if (!lesson) return null

  const TypeIcon = TYPE_ICONS[lesson.content_type] || FileText
  const sections = lesson.content_json?.sections || []
  const quiz = lesson.content_json?.quiz || []
  const starterCode = lesson.content_json?.starter_code || ''
  const exercises = lesson.content_json?.exercises || []
  const project = lesson.content_json?.project || null
  const isCompleted = lesson.progress?.status === 'completed'

  const handleQuizComplete = (score) => {
    setQuizScore(score)
    complete.mutate(score)
  }

  const handleMarkDone = () => {
    complete.mutate(quizScore)
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Sticky header */}
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-3xl mx-auto px-6 py-3 flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-slate-500 flex items-center gap-1.5">
              <TypeIcon className="w-3 h-3" />{lesson.subject} · Grade {lesson.grade}
            </p>
            <h1 className="text-white font-semibold truncate">{lesson.title}</h1>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Clock className="w-3.5 h-3.5" />{lesson.estimated_mins}m
            {isCompleted && <span className="ml-2 text-emerald-400 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" />Done</span>}
          </div>
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-8 space-y-8">
        {/* Description */}
        {lesson.description && (
          <p className="text-slate-400 text-base leading-relaxed">{lesson.description}</p>
        )}

        {/* Content sections */}
        {sections.map((section, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
            <h2 className="text-white font-semibold text-lg mb-3">{section.heading}</h2>
            <div className="text-slate-300 leading-relaxed whitespace-pre-wrap font-mono text-sm bg-white/3 rounded-xl p-4 border border-white/5">
              {section.body}
            </div>
          </motion.div>
        ))}

        {/* Starter code editor */}
        {(lesson.content_type === 'coding' || lesson.content_type === 'project') && starterCode && (
          <div>
            <h2 className="text-white font-semibold text-lg mb-3">Try it in the Editor</h2>
            <CodeEditor initialCode={starterCode} />
          </div>
        )}

        {/* Exercises */}
        {exercises.length > 0 && (
          <div>
            <h2 className="text-white font-semibold text-lg mb-3">Exercises</h2>
            <div className="space-y-4">
              {exercises.map((ex, i) => (
                <div key={i} className="bg-white/3 border border-white/10 rounded-xl p-4">
                  <h3 className="text-indigo-300 font-medium mb-2">Exercise {i + 1}: {ex.title}</h3>
                  <p className="text-slate-300 text-sm mb-3">{ex.prompt}</p>
                  <CodeEditor initialCode={`# ${ex.title}\n# ${ex.prompt}\n\n`} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Project spec */}
        {project && (
          <div className="bg-gradient-to-br from-purple-900/20 to-indigo-900/20 border border-purple-500/30 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Rocket className="w-5 h-5 text-purple-400" />
              <h2 className="text-white font-semibold">Project: {project.title || 'Grade Project'}</h2>
            </div>
            {project.instructions && <p className="text-slate-300 text-sm mb-4">{project.instructions}</p>}
            {project.requirements && (
              <div>
                <p className="text-xs text-purple-300 font-medium uppercase tracking-wide mb-2">Requirements</p>
                <ul className="space-y-1">
                  {project.requirements.map((req, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                      <span className="text-purple-400 mt-0.5">✓</span>{req}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Quiz */}
        {quiz.length > 0 && (
          <div className="bg-white/3 border border-white/10 rounded-xl p-5">
            <h2 className="text-white font-semibold mb-4 flex items-center gap-2">
              <HelpCircle className="w-5 h-5 text-indigo-400" /> Knowledge Check
            </h2>
            {quizScore !== null ? (
              <div className="text-center py-4">
                <Trophy className="w-12 h-12 text-yellow-400 mx-auto mb-2" />
                <p className="text-2xl font-black text-white">{quizScore}%</p>
                <p className="text-slate-400 text-sm mt-1">Quiz complete!</p>
              </div>
            ) : (
              <InteractiveQuiz questions={quiz} onComplete={handleQuizComplete} />
            )}
          </div>
        )}

        {/* Complete button */}
        {!isCompleted && quiz.length === 0 && (
          <button
            onClick={handleMarkDone}
            disabled={complete.isPending}
            className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-60 text-white font-semibold py-3.5 rounded-xl transition flex items-center justify-center gap-2"
          >
            <CheckCircle2 className="w-5 h-5" />
            {complete.isPending ? 'Saving…' : 'Mark as Complete'}
          </button>
        )}

        {isCompleted && (
          <div className="text-center py-4">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto mb-2" />
            <p className="text-emerald-400 font-semibold">Lesson Completed!</p>
            <button onClick={() => navigate(-1)} className="mt-3 text-sm text-slate-400 hover:text-slate-200 transition">
              ← Back to curriculum
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
