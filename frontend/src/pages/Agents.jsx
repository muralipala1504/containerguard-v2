import { useState, useEffect } from 'react'
import { getAgents } from '../api'

const timeAgo = dt => {
  if (!dt) return 'Never'
  const d = Math.floor((Date.now() - new Date(dt)) / 1000)
  if (d < 60) return d + 's ago'
  if (d < 3600) return Math.floor(d/60) + 'm ago'
  return Math.floor(d/3600) + 'h ago'
}

export default function Agents() {
  const [agents, setAgents] = useState([])
  const [error, setError] = useState(null)
  const load = async () => {
    try { const r = await getAgents(); setAgents(r.data.agents); setError(null) }
    catch { setError('Cannot reach cloud API') }
  }
  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t) }, [])
  return (
    <div>
      <div className="flex justify-between mb-6">
        <h1 className="text-2xl font-bold">Agents</h1>
        <span className="text-xs text-gray-500">{agents.length} registered</span>
      </div>
      {error && <div className="bg-red-900/40 border border-red-700 text-red-300 rounded-lg px-4 py-3 mb-4 text-sm">Cannot reach API</div>}
      <div className="grid gap-4">
        {agents.map(a => (
          <div key={a.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex justify-between items-center">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <span className="font-mono text-emerald-300 text-sm">{a.id}</span>
                <span className={a.status === 'active' ? 'text-xs px-2 py-0.5 rounded-full border border-emerald-700 text-emerald-400' : 'text-xs px-2 py-0.5 rounded-full border border-red-700 text-red-400'}>{a.status}</span>
              </div>
              <p className="text-white font-medium">{a.name}</p>
              <p className="text-gray-500 text-sm">{a.location}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">Last heartbeat</p>
              <p className="text-sm text-gray-300">{timeAgo(a.last_heartbeat)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
