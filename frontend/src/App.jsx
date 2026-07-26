import { useState } from 'react'
import ReviewTab from './ReviewTab.jsx'
import ChatTab from './ChatTab.jsx'

const TABS = {
  REVIEW: 'review',
  CHAT: 'chat',
}

export default function App() {
  const [activeTab, setActiveTab] = useState(TABS.REVIEW)

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#f4f7fb] text-slate-900">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-[radial-gradient(circle_at_top_left,rgba(79,70,229,0.12),transparent_42%),radial-gradient(circle_at_top_right,rgba(14,165,233,0.10),transparent_38%)]" />

      <div className="relative mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        <header className="mb-7 flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-indigo-600 text-white shadow-lg shadow-indigo-600/20">
            <ScaleIcon />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-indigo-600">
              Asistente urbanístico
            </p>
            <h1 className="text-2xl font-bold tracking-tight sm:text-[1.7rem]">
              Pre-revisión normativa
            </h1>
          </div>
        </header>

        <nav
          aria-label="Secciones principales"
          className="mb-7 grid w-full grid-cols-2 gap-1 rounded-2xl border border-slate-200/80 bg-white/80 p-1.5 shadow-sm backdrop-blur sm:w-fit"
        >
          <TabButton
            label="Revisión de proyecto"
            isActive={activeTab === TABS.REVIEW}
            onClick={() => setActiveTab(TABS.REVIEW)}
          />
          <TabButton
            label="Preguntas sobre normativa"
            isActive={activeTab === TABS.CHAT}
            onClick={() => setActiveTab(TABS.CHAT)}
          />
        </nav>

        <div
          className={activeTab === TABS.REVIEW ? 'contents' : 'hidden'}
          aria-hidden={activeTab !== TABS.REVIEW}
        >
          <ReviewTab />
        </div>
        <div
          className={activeTab === TABS.CHAT ? 'contents' : 'hidden'}
          aria-hidden={activeTab !== TABS.CHAT}
        >
          <ChatTab />
        </div>
      </div>
    </div>
  )
}

function TabButton({ label, isActive, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-xl px-5 py-2.5 text-sm font-semibold transition-all ${
        isActive
          ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/15'
          : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800'
      }`}
    >
      {label}
    </button>
  )
}

function ScaleIcon() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      className="h-6 w-6"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v18M5 6h14M7 6 3.5 13h7L7 6Zm10 0-3.5 7h7L17 6ZM8 21h8" />
    </svg>
  )
}
