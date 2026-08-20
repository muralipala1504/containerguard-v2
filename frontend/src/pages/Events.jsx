import { useState, useEffect } from 'react'
import { getEvents, getAgents } from '../api'

const COLORS = { remediation_success: 'text-emerald-400', remediation_failed: 'text-red-400' }
const ICONS = { restart_container: '🔄', restart_pod: '⚙️', alert: '🔔' }

function Row({ e }) {
  const color = COLORS[e.event_type] || 'text-gray-400'
  const icon = ICONS[e.action] || '⚡'
  const badge = e.status === 'success'
    ? 'border-emerald-700 text-emerald-400 bg-emerald-900/30'
    : 'border-red-700 text-red-400 bg-red-900/30'
  return (
    <div className="flex items-start gap-4 py-3 border-b border-gray-800 last:border-0">
      <span className="text-xl mt-0.5">{icon}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <span className={'text-sm font-semibold ' + color}>{e.event_type}</span>
          <span className="text-xs text-gray-500 font-mono">{e.resource_type}/{e.resource_name}</span>
        </div>
        <p className="text-gray-300 text-sm">{e.message}</p>
        <p className="text-xs text-gray-600 mt-0.5">Agent: {e.agent_id} · {new Date(e.timestamp).toLocaleTimeString()}</p>
      </div>
      <span className={'text-xs px-2 py-0.5 rounded-full border shrink-0 mt-1 ' + badge}>{e.status}</span>
    </div>
  )
}

export default function Events() {
  const [events, setEvents] = useState([])
  const [agents, setAgents] = useState([])
  const [filter, setFilter] = useState('')
  const [error, setError] = useState(null)
  const load = async () => {
    try {
      const [ev, ag] = await Promise.all([getEvents(filter||null, 50), getAgents()])
      setEvents(ev.data.events); setAgents(ag.data.agents); setError(null)
    } catch { setError('Cannot reach cloud API') }
  }
  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t) }, [filter])
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Events</h1>
        <div className="flex items-center gap-3">
          <select value={filter} onChange={e => setFilter(e.target.value)}
            className="bg-gray-800 border border-gray-700 text-sm text-gray-300 rounded-lg px-3 py-1.5">
            <option value="">All Agents</option>
            {agents.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
          <span className="text-xs text-gray-500">{events.length} events</span>
        </div>
      </div>
      {error && <div className="bg-red-900/40 border border-red-700 text-red-300 rounded-lg px-4 py-3 mb-4 text-sm">Cannot reach API</div>}
      <div className="bg-gray-900 border border-gray-800 rounded-xl px-5">
        {events.length === 0 && <p className="py-6 text-gray-500 text-sm text-center">No events yet.</p>}
        {events.map(e => <Row key={e.id} e={e} />)}
      </div>
    </div>
  )
}
