import { useState, useEffect, useRef } from 'react'
import { Play, RotateCcw, Loader2, Terminal } from 'lucide-react'

export default function CodeEditor({ initialCode = '', language = 'python', readOnly = false }) {
  const [code, setCode] = useState(initialCode)
  const [output, setOutput] = useState('')
  const [loading, setLoading] = useState(false)
  const [pyodideReady, setPyodideReady] = useState(false)
  const pyodideRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    if (language !== 'python') return
    if (window.loadPyodide) {
      initPyodide()
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js'
    script.onload = initPyodide
    document.head.appendChild(script)
  }, [language])

  const initPyodide = async () => {
    try {
      pyodideRef.current = await window.loadPyodide({ indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/' })
      // Redirect stdout
      await pyodideRef.current.runPythonAsync(`
import sys
from io import StringIO
sys.stdout = StringIO()
      `)
      setPyodideReady(true)
    } catch (e) {
      console.error('Pyodide load failed:', e)
    }
  }

  const runCode = async () => {
    if (!pyodideRef.current) {
      setOutput('Python runtime is loading… please wait and try again.')
      return
    }
    setLoading(true)
    setOutput('')
    try {
      // Reset stdout buffer
      await pyodideRef.current.runPythonAsync(`
import sys
from io import StringIO
sys.stdout = StringIO()
      `)
      await pyodideRef.current.runPythonAsync(code)
      const stdout = await pyodideRef.current.runPythonAsync('sys.stdout.getvalue()')
      setOutput(stdout || '(no output)')
    } catch (err) {
      setOutput(`Error:\n${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault()
      const ta = textareaRef.current
      const start = ta.selectionStart
      const end = ta.selectionEnd
      const newCode = code.substring(0, start) + '    ' + code.substring(end)
      setCode(newCode)
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + 4
      })
    }
  }

  return (
    <div className="rounded-xl overflow-hidden border border-white/10 bg-slate-900">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-800/60 border-b border-white/10">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/70" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
            <div className="w-3 h-3 rounded-full bg-green-500/70" />
          </div>
          <span className="text-xs text-slate-400 font-mono ml-2">
            {language === 'python' ? 'Python' : language}
            {pyodideReady && <span className="ml-2 text-emerald-400">● Ready</span>}
            {!pyodideReady && language === 'python' && <span className="ml-2 text-amber-400">● Loading…</span>}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { setCode(initialCode); setOutput('') }}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs text-slate-400 hover:text-slate-200 transition"
          >
            <RotateCcw className="w-3 h-3" /> Reset
          </button>
          <button
            onClick={runCode}
            disabled={loading || (language === 'python' && !pyodideReady)}
            className="flex items-center gap-1.5 px-3 py-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-medium rounded-lg transition"
          >
            {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3" />}
            {loading ? 'Running…' : 'Run'}
          </button>
        </div>
      </div>

      {/* Code area */}
      <textarea
        ref={textareaRef}
        value={code}
        onChange={e => !readOnly && setCode(e.target.value)}
        onKeyDown={handleKeyDown}
        readOnly={readOnly}
        spellCheck={false}
        className="w-full bg-slate-900 text-slate-100 font-mono text-sm p-4 outline-none resize-none min-h-[220px] leading-relaxed"
        style={{ tabSize: 4 }}
      />

      {/* Output */}
      {(output || loading) && (
        <div className="border-t border-white/10">
          <div className="flex items-center gap-2 px-4 py-2 bg-slate-800/40 border-b border-white/5">
            <Terminal className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-xs text-slate-400 font-medium">Output</span>
          </div>
          <pre className={`p-4 font-mono text-sm min-h-[60px] whitespace-pre-wrap ${
            output.startsWith('Error') ? 'text-red-400' : 'text-emerald-400'
          }`}>
            {loading ? <span className="text-slate-500">Running…</span> : output}
          </pre>
        </div>
      )}
    </div>
  )
}
