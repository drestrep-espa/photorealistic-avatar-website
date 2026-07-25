import { useEffect, useRef, useState } from 'react'

const API_BASE = '/api'

export default function ChatTab() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [error, setError] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isRunning])

  async function handleSend() {
    const question = input.trim()
    if (!question || isRunning) return

    const history = messages
    setMessages([...history, { role: 'user', content: question }])
    setInput('')
    setIsRunning(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}/questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, history }),
      })

      if (!response.ok) {
        const detail = await response.json().catch(() => null)
        throw new Error(detail?.detail || `Error del servidor (${response.status})`)
      }

      const data = await response.json()
      setMessages((prev) => [...prev, { role: 'assistant', content: data.answer }])
    } catch (err) {
      setError(err.message || 'No se pudo obtener la respuesta.')
    } finally {
      setIsRunning(false)
    }
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSend()
    }
  }

  function handleClear() {
    setMessages([])
    setError(null)
    setInput('')
  }

  const isEmpty = messages.length === 0

  return (
    <main className="flex flex-1 flex-col gap-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Pregunta sobre la normativa urbanística indexada. Las respuestas se basan en los
          fragmentos recuperados del documento.
        </p>
        {!isEmpty && (
          <button
            type="button"
            onClick={handleClear}
            className="shrink-0 rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Nueva conversación
          </button>
        )}
      </div>

      <div className="flex min-h-[24rem] flex-1 flex-col gap-4 overflow-y-auto rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
        {isEmpty && !isRunning && (
          <div className="m-auto max-w-sm text-center text-sm text-slate-400 dark:text-slate-500">
            Escribe una pregunta para empezar. Por ejemplo:{' '}
            <span className="italic">
              «¿Cuál es la altura máxima para vivienda unifamiliar aislada?»
            </span>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm ${
                message.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-100'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}

        {isRunning && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-2xl bg-slate-100 px-4 py-2.5 text-sm text-slate-500 dark:bg-slate-800 dark:text-slate-400">
              <span className="h-3.5 w-3.5 shrink-0 animate-spin rounded-full border-2 border-slate-400 border-t-transparent" />
              Consultando la normativa…
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      <div className="flex items-end gap-3">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          disabled={isRunning}
          placeholder="Escribe tu pregunta y pulsa Enter…"
          className="flex-1 resize-none rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400 disabled:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-500 dark:disabled:bg-slate-800"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={!input.trim() || isRunning}
          className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-300 dark:disabled:bg-slate-800"
        >
          Enviar
        </button>
      </div>
    </main>
  )
}
