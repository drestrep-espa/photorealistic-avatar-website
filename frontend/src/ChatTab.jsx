import { useEffect, useRef, useState } from 'react'
import MarkdownContent from './MarkdownContent.jsx'

const API_BASE = '/api'

const EXAMPLE_QUESTIONS = [
  '¿Cuál es la ocupación máxima permitida para la ordenanza RU-3?',
  '¿Qué retranqueos exige la normativa para vivienda unifamiliar?',
]

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
      setMessages((previous) => [
        ...previous,
        { role: 'assistant', content: data.answer },
      ])
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
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="mb-1 text-sm font-semibold text-slate-900">
            Consulta la normativa
          </p>
          <p className="max-w-2xl text-sm leading-6 text-slate-500">
            Pregunta sobre la normativa urbanística indexada. Cada respuesta se basa
            en fragmentos recuperados del documento.
          </p>
        </div>
        {!isEmpty && (
          <button
            type="button"
            onClick={handleClear}
            className="shrink-0 self-start rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-semibold text-slate-600 shadow-sm transition hover:border-slate-300 hover:bg-slate-50 sm:self-auto"
          >
            Nueva conversación
          </button>
        )}
      </div>

      <section className="flex h-[calc(100vh-15.5rem)] min-h-[34rem] max-h-[52rem] flex-col overflow-hidden rounded-3xl border border-slate-200/90 bg-white shadow-xl shadow-slate-200/50">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            </span>
            Normativa lista para consultar
          </div>
          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[0.68rem] font-semibold uppercase tracking-wide text-slate-500">
            IA
          </span>
        </div>

        <div className="flex flex-1 flex-col gap-6 overflow-y-auto bg-slate-50/45 px-4 py-6 sm:px-6">
          {isEmpty && !isRunning && (
            <EmptyState onSelectQuestion={setInput} />
          )}

          {messages.map((message, index) => (
            <Message key={`${message.role}-${index}`} message={message} />
          ))}

          {isRunning && (
            <div className="flex items-start gap-3">
              <AssistantAvatar />
              <div
                role="status"
                className="flex items-center gap-2 rounded-2xl rounded-tl-md border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm"
              >
                <span className="h-3.5 w-3.5 shrink-0 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent" />
                Consultando la normativa…
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {error && (
          <div className="mx-4 mt-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 sm:mx-5">
            {error}
          </div>
        )}

        <div className="border-t border-slate-100 bg-white p-3 sm:p-4">
          <div className="flex items-end gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm transition focus-within:border-indigo-400 focus-within:ring-4 focus-within:ring-indigo-100">
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
              disabled={isRunning}
              placeholder="Pregunta sobre ocupación, altura, retranqueos…"
              className="max-h-36 min-h-12 flex-1 resize-none bg-transparent px-2 py-2 text-sm leading-6 text-slate-900 outline-none placeholder:text-slate-400 disabled:cursor-not-allowed"
            />
            <button
              type="button"
              aria-label="Enviar pregunta"
              onClick={handleSend}
              disabled={!input.trim() || isRunning}
              className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-600/20 transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400 disabled:shadow-none"
            >
              <SendIcon />
            </button>
          </div>
          <p className="mt-2 text-center text-[0.68rem] text-slate-400">
            Enter para enviar · Mayús + Enter para nueva línea
          </p>
        </div>
      </section>
    </main>
  )
}

function Message({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex items-start gap-3 ${isUser ? 'justify-end' : ''}`}>
      {!isUser && <AssistantAvatar />}
      <div
        className={`min-w-0 text-sm leading-6 ${
          isUser
            ? 'max-w-[82%] whitespace-pre-wrap rounded-2xl rounded-tr-md bg-indigo-600 px-4 py-3 text-white shadow-md shadow-indigo-600/10'
            : 'max-w-[92%] rounded-2xl rounded-tl-md border border-slate-200 bg-white px-5 py-4 text-slate-700 shadow-sm sm:max-w-[88%]'
        }`}
      >
        {isUser ? (
          message.content
        ) : (
          <MarkdownContent content={message.content} />
        )}
      </div>
      {isUser && (
        <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-slate-800 text-xs font-bold text-white">
          Tú
        </div>
      )}
    </div>
  )
}

function EmptyState({ onSelectQuestion }) {
  return (
    <div className="m-auto flex max-w-xl flex-col items-center px-4 py-10 text-center">
      <div className="mb-4 grid h-14 w-14 place-items-center rounded-2xl bg-indigo-50 text-indigo-600">
        <BookIcon />
      </div>
      <h2 className="text-lg font-bold text-slate-900">¿Qué necesitas comprobar?</h2>
      <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
        Haz una pregunta concreta y te responderé con la norma, el apartado y la
        evidencia recuperada.
      </p>
      <div className="mt-6 grid w-full gap-2 sm:grid-cols-2">
        {EXAMPLE_QUESTIONS.map((question) => (
          <button
            key={question}
            type="button"
            onClick={() => onSelectQuestion(question)}
            className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-left text-xs leading-5 text-slate-600 shadow-sm transition hover:border-indigo-300 hover:text-indigo-700 hover:shadow"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  )
}

function AssistantAvatar() {
  return (
    <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-indigo-100 text-indigo-700">
      <ScaleSmallIcon />
    </div>
  )
}

function SendIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="h-5 w-5">
      <path strokeLinecap="round" strokeLinejoin="round" d="m5 12 14-7-4 14-3-6-7-1Z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="m12 13 7-8" />
    </svg>
  )
}

function BookIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-7 w-7">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22V5.5ZM20 5.5A2.5 2.5 0 0 0 17.5 3H13v17h4.5a2.5 2.5 0 0 1 2.5 2V5.5Z" />
    </svg>
  )
}

function ScaleSmallIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-4 w-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v18M5 6h14M7 6l-3 6h6L7 6Zm10 0-3 6h6l-3-6ZM8 21h8" />
    </svg>
  )
}
