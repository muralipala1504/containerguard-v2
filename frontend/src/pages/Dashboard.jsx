import { useState, useEffect } from 'react'
import { getDashboardStats } from '../api'

function StatCard({ label, value, color }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className={'text-4xl font-bold ' + color}>{value ?? '—'}</p>
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const load = async () => {
    try { const r = await getDashboardStats(); setStats(r.data); setError(null) }
    catch { setError('Cannot reach cloud API') }
  }
  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t) }, [])
  return (
    <div>
      <div className="flex justify-between mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <span className="text-xs text-gray-500">Auto-refresh 5s</span>
      </div>
      {error && <div className="bg-red-900/40 border border-red-700 text-red-300 rounded-lg px-4 py-3 mb-6 text-sm">Cannot reach API</div>}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Agents" value={stats?.total_agents} color="text-emerald-400" />
        <StatCard label="Active Agents" value={stats?.active_agents} color="text-blue-400" />
        <StatCard label="Total Events" value={stats?.total_events} color="text-violet-400" />
        <StatCard label="API Status" value={stats ? 'Online' : 'Offline'} color={stats ? 'text-emerald-400' : 'text-red-400'} />
      </div>
      {stats?.agents?.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-gray-400 mb-3">Registered Agents</h2>
          <div className="flex flex-wrap gap-2">
            {stats.agents.map(id => <span key={id} className="bg-gray-800 text-emerald-300 text-xs font-mono px-3 py-1 rounded-full">{id}</span>)}
          </div>
        </div>
      )}
    </div>
  )
}
