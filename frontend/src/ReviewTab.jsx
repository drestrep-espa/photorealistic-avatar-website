import { useRef, useState } from 'react'

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
    <main className="flex flex-1 flex-col gap-6">
      <p className="text-sm text-slate-500 dark:text-slate-400">
        Sube el proyecto básico en PDF y compáralo automáticamente frente a la normativa
        urbanística indexada.
      </p>

      <label
        htmlFor="pdf-input"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-6 py-12 text-center transition-colors ${
          isRunning
            ? 'cursor-not-allowed border-slate-200 bg-slate-100 dark:border-slate-800 dark:bg-slate-900'
            : 'border-slate-300 bg-white hover:border-indigo-400 hover:bg-indigo-50 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-indigo-500 dark:hover:bg-slate-800'
        }`}
      >
        <span className="text-sm font-medium">
          {file ? file.name : 'Arrastra el PDF aquí o haz clic para seleccionarlo'}
        </span>
        {!file && (
          <span className="text-xs text-slate-400 dark:text-slate-500">
            Solo ficheros .pdf
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
          className="flex-1 rounded-lg bg-indigo-600 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-300 dark:disabled:bg-slate-800"
        >
          {isRunning ? 'Cotejando resultados…' : 'Cotejar resultados'}
        </button>
        {(result || error) && (
          <button
            type="button"
            onClick={handleReset}
            className="rounded-lg border border-slate-300 px-4 py-3 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            Nueva revisión
          </button>
        )}
      </div>

      {isRunning && (
        <div className="flex items-center gap-3 rounded-lg border border-indigo-200 bg-indigo-50 px-4 py-3 text-sm text-indigo-700 dark:border-indigo-900 dark:bg-indigo-950 dark:text-indigo-300">
          <span className="h-4 w-4 shrink-0 animate-spin rounded-full border-2 border-indigo-400 border-t-transparent" />
          Generando el informe. Esto puede tardar varios minutos, no cierres esta pestaña.
        </div>
      )}

      {status === STATUS.ERROR && error && (
        <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
          {error}
        </div>
      )}

      {status === STATUS.DONE && result && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-4 text-sm text-emerald-800 dark:border-emerald-900 dark:bg-emerald-950 dark:text-emerald-300">
          <p className="font-semibold">Ya está terminado el informe.</p>
          <p className="mt-1">
            Te lo dejo guardado en esta ruta:{' '}
            <code className="rounded bg-emerald-100 px-1.5 py-0.5 font-mono text-xs dark:bg-emerald-900">
              {result.report_path}
            </code>
          </p>
          {formatCost(result.cost_summary) && (
            <p className="mt-1 text-xs text-emerald-700/80 dark:text-emerald-400/80">
              Coste de esta ejecución: ${formatCost(result.cost_summary)}
            </p>
          )}
          {result.summary && (
            <details className="mt-3">
              <summary className="cursor-pointer text-xs font-medium text-emerald-700 dark:text-emerald-400">
                Ver resumen del informe
              </summary>
              <pre className="mt-2 max-h-96 overflow-auto whitespace-pre-wrap text-xs text-emerald-900 dark:text-emerald-200">
                {result.summary}
              </pre>
            </details>
          )}
        </div>
      )}
    </main>
  )
}
