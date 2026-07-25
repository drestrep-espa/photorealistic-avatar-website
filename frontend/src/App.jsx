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
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="mx-auto flex min-h-screen w-full max-w-2xl flex-col px-6 py-12">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight">Pre-revisión normativa</h1>
        </header>

        <nav className="mb-8 flex gap-1 border-b border-slate-200 dark:border-slate-800">
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

        {activeTab === TABS.REVIEW ? <ReviewTab /> : <ChatTab />}
      </div>
    </div>
  )
}

function TabButton({ label, isActive, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`-mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors ${
        isActive
          ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
          : 'border-transparent text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
      }`}
    >
      {label}
    </button>
  )
}
