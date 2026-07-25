import { useRef, useState } from 'react'
import MarkdownContent from './MarkdownContent.jsx'

const API_BASE = '/api'

const STATUS = {
  IDLE: 'idle',
  RUNNING: 'running',
  DONE: 'done',
  ERROR: 'error',
}

function formatCost(costSummary) {
  if (!costSummary || typeof costSummary.total_cost_usd !== 'number') return null
  return costSummary.total_cost_usd.toFixed(4)
}

export default function ReviewTab() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState(STATUS.IDLE)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  const isRunning = status === STATUS.RUNNING

  function handleFileChange(event) {
    const selected = event.target.files?.[0] ?? null
    setFile(selected)
    setStatus(STATUS.IDLE)
    setResult(null)
    setError(null)
  }

  function handleDrop(event) {
    event.preventDefault()
    if (isRunning) return
    const dropped = event.dataTransfer.files?.[0]
    if (dropped && dropped.type === 'application/pdf') {
      setFile(dropped)
      setStatus(STATUS.IDLE)
      setResult(null)
      setError(null)
    }
  }

  async function handleCotejar() {
    if (!file || isRunning) return
    setStatus(STATUS.RUNNING)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE}/reviews`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const detail = await response.json().catch(() => null)
        throw new Error(detail?.detail || `Error del servidor (${response.status})`)
      }

      const data = await response.json()
      setResult(data)
      setStatus(STATUS.DONE)
    } catch (err) {
      setError(err.message || 'No se pudo completar la revisión.')
      setStatus(STATUS.ERROR)
    }
  }

  function handleReset() {
    setFile(null)
    setStatus(STATUS.IDLE)
    setResult(null)
    setError(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <main className="flex flex-1 flex-col gap-5">
      <div>
        <p className="mb-1 text-sm font-semibold text-slate-900">Revisa tu proyecto</p>
        <p className="max-w-2xl text-sm leading-6 text-slate-500">
          Sube el proyecto básico en PDF y compáralo automáticamente frente a la
          normativa urbanística indexada.
        </p>
      </div>

      <label
        htmlFor="pdf-input"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
        className={`flex min-h-72 cursor-pointer flex-col items-center justify-center gap-3 rounded-3xl border-2 border-dashed px-6 py-12 text-center shadow-sm transition-all ${
          isRunning
            ? 'cursor-not-allowed border-slate-200 bg-slate-100'
            : 'border-slate-300 bg-white hover:-translate-y-0.5 hover:border-indigo-400 hover:bg-indigo-50/50 hover:shadow-lg'
        }`}
      >
        <span className="grid h-14 w-14 place-items-center rounded-2xl bg-indigo-50 text-indigo-600">
          <UploadIcon />
        </span>
        <span className="text-sm font-semibold text-slate-800">
          {file ? file.name : 'Arrastra el PDF aquí o haz clic para seleccionarlo'}
        </span>
        {!file && (
          <span className="text-xs text-slate-400">
            Solo ficheros PDF
          </span>
        )}
        <input
          id="pdf-input"
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          disabled={isRunning}
          onChange={handleFileChange}
        />
      </label>

      <div className="flex gap-3">
        <button
          type="button"
          onClick={handleCotejar}
          disabled={!file || isRunning}
          className="flex-1 rounded-xl bg-indigo-600 px-4 py-3 text-sm font-semibold text-white shadow-md shadow-indigo-600/15 transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
        >
          {isRunning ? 'Cotejando resultados…' : 'Cotejar resultados'}
        </button>
        {(result || error) && (
          <button
            type="button"
            onClick={handleReset}
            className="rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm font-medium text-slate-600 hover:bg-slate-50"
          >
            Nueva revisión
          </button>
        )}
      </div>

      {isRunning && (
        <div className="flex items-center gap-3 rounded-xl border border-indigo-200 bg-indigo-50 px-4 py-3 text-sm text-indigo-700">
          <span className="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent" />
          Generando el informe. Esto puede tardar varios minutos, no cierres esta pestaña.
        </div>
      )}

      {status === STATUS.ERROR && error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {status === STATUS.DONE && result && (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-5 py-5 text-sm text-emerald-900 shadow-sm">
          <p className="font-semibold">Ya está terminado el informe.</p>
          <p className="mt-1">
            Te lo dejo guardado en esta ruta:{' '}
            <code className="rounded bg-emerald-100 px-1.5 py-0.5 font-mono text-xs">
              {result.report_path}
            </code>
          </p>
          {formatCost(result.cost_summary) && (
            <p className="mt-1 text-xs text-emerald-700/80">
              Coste de esta ejecución: ${formatCost(result.cost_summary)}
            </p>
          )}
          {result.summary && (
            <details className="mt-3">
              <summary className="cursor-pointer text-xs font-semibold text-emerald-700">
                Ver resumen del informe
              </summary>
              <div className="mt-3 max-h-[32rem] overflow-auto rounded-xl border border-emerald-200 bg-white p-5 text-slate-700">
                <MarkdownContent content={result.summary} />
              </div>
            </details>
          )}
        </div>
      )}
    </main>
  )
}

function UploadIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="h-7 w-7">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M5 14v4a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-4" />
    </svg>
  )
}
