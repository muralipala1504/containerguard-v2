import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import Events from './pages/Events'

const NAV = [
  { id: 'dashboard', label: '📊 Dashboard' },
  { id: 'agents', label: '🖥️ Agents' },
  { id: 'events', label: '⚡ Events' },
]

export default function App() {
  const [page, setPage] = useState('dashboard')
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center gap-8">
        <span className="text-lg font-bold text-emerald-400">ContainerGuard</span>
        <div className="flex gap-2">
          {NAV.map(n => (
            <button key={n.id} onClick={() => setPage(n.id)}
              className={page === n.id ? 'px-4 py-1.5 rounded text-sm font-medium bg-emerald-600 text-white' : 'px-4 py-1.5 rounded text-sm font-medium text-gray-400 hover:text-white hover:bg-gray-800'}>
              {n.label}
            </button>
          ))}
        </div>
      </nav>
      <main className="p-6">
        {page === 'dashboard' && <Dashboard />}
        {page === 'agents' && <Agents />}
        {page === 'events' && <Events />}
      </main>
    </div>
  )
}
