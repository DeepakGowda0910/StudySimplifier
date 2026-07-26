import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Wand2 } from 'lucide-react'
import CodeEditor from '../../../components/school/CodeEditor'

const EXAMPLES = [
  { label: 'Hello World', code: 'print("Hello, World!")\nprint("Welcome to AI School!")', desc: 'Your first Python program' },
  { label: 'Calculator', code: 'a = float(input("Enter first number: "))\nb = float(input("Enter second number: "))\nprint(f"Sum: {a + b}")\nprint(f"Product: {a * b}")', desc: 'Basic arithmetic' },
  { label: 'FizzBuzz', code: 'for i in range(1, 21):\n    if i % 15 == 0:\n        print("FizzBuzz")\n    elif i % 3 == 0:\n        print("Fizz")\n    elif i % 5 == 0:\n        print("Buzz")\n    else:\n        print(i)', desc: 'Classic coding challenge' },
  { label: 'Fibonacci', code: 'def fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        print(a, end=" ")\n        a, b = b, a + b\n\nfibonacci(10)', desc: 'Famous number sequence' },
  { label: 'Number Guessing', code: 'import random\nsecret = random.randint(1, 10)\nguesses = 3\n\nprint("I\'m thinking of a number 1-10. You have", guesses, "guesses!")\nfor i in range(guesses):\n    guess = int(input(f"Guess {i+1}: "))\n    if guess == secret:\n        print("Correct! You win!")\n        break\n    elif guess < secret:\n        print("Too low!")\n    else:\n        print("Too high!")\nelse:\n    print(f"Out of guesses! It was {secret}")', desc: 'Mini game with loops' },
  { label: 'Word Counter', code: 'sentence = input("Enter a sentence: ")\nwords = sentence.split()\nword_count = {}\nfor word in words:\n    word = word.lower()\n    word_count[word] = word_count.get(word, 0) + 1\n\nprint(f"Total words: {len(words)}")\nprint("\\nWord frequencies:")\nfor word, count in sorted(word_count.items(), key=lambda x: -x[1]):\n    print(f"  {word}: {count}")', desc: 'Dictionaries in action' },
]

export default function CodingPlayground() {
  const navigate = useNavigate()
  const [selected, setSelected] = useState(EXAMPLES[0])
  const [key, setKey] = useState(0)

  const loadExample = (ex) => {
    setSelected(ex)
    setKey(k => k + 1) // force CodeEditor remount to reset state
  }

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="sticky top-0 z-10 bg-slate-950/90 backdrop-blur border-b border-white/10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="text-slate-400 hover:text-white transition">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-white font-semibold">Coding Playground</h1>
            <p className="text-xs text-slate-500">Python runs directly in your browser — no install needed</p>
          </div>
          <Wand2 className="w-5 h-5 text-indigo-400 ml-auto" />
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-6">
        <div className="grid grid-cols-[200px_1fr] gap-6">
          {/* Example list */}
          <div className="space-y-1">
            <p className="text-xs text-slate-500 uppercase tracking-wide font-medium mb-3">Examples</p>
            {EXAMPLES.map(ex => (
              <button
                key={ex.label}
                onClick={() => loadExample(ex)}
                className={`w-full text-left px-3 py-2.5 rounded-lg transition text-sm ${
                  selected.label === ex.label
                    ? 'bg-indigo-600/30 border border-indigo-500/50 text-indigo-300'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
              >
                <span className="font-medium">{ex.label}</span>
                <p className="text-xs text-slate-600 mt-0.5">{ex.desc}</p>
              </button>
            ))}
            <div className="mt-4 pt-4 border-t border-white/10">
              <button
                onClick={() => loadExample({ label: 'Blank', code: '# Write your code here\n', desc: 'Fresh start' })}
                className="w-full text-left px-3 py-2.5 rounded-lg text-sm text-slate-500 hover:text-slate-200 hover:bg-white/5 transition"
              >
                + Blank Editor
              </button>
            </div>
          </div>

          {/* Editor */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-white font-medium">{selected.label}</h2>
                <p className="text-xs text-slate-500">{selected.desc}</p>
              </div>
            </div>
            <CodeEditor key={key} initialCode={selected.code} language="python" />
            <p className="text-xs text-slate-600 mt-3 text-center">
              Powered by Pyodide — Python 3.11 running in your browser via WebAssembly
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
