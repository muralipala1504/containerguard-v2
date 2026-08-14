import { useState, useEffect } from 'react'
import { getAPIURL } from '../utils/api'
import '../styles/Dashboard.css'

const API_URL = getAPIURL()

export default function Dashboard({ user, token, onLogout }) {
  const [monitoring, setMonitoring] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchMonitoring()
    const interval = setInterval(fetchMonitoring, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchMonitoring = async () => {
    try {
      const res = await fetch(`${API_URL}/api/monitoring/all`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await res.json()
      setMonitoring(data)
      setError('')
    } catch (err) {
      setError('Failed to fetch monitoring data')
    } finally {
      setLoading(false)
    }
  }

  const k8sPods = monitoring?.k8s?.pods || []
  const dockerContainers = monitoring?.docker?.containers || []
  const dockerInfo = monitoring?.docker?.info || {}

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>ContainerGuard v2.0</h1>
        <div className="header-right">
          <span>Welcome, {user?.name}!</span>
          <button onClick={onLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <div className="filters">
        <button
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All ({k8sPods.length + dockerContainers.length})
        </button>
        <button
          className={filter === 'k8s' ? 'active' : ''}
          onClick={() => setFilter('k8s')}
        >
          Kubernetes ({k8sPods.length})
        </button>
        <button
          className={filter === 'docker' ? 'active' : ''}
          onClick={() => setFilter('docker')}
        >
          Docker ({dockerContainers.length})
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {loading && <div className="loading">Loading...</div>}

      {!loading && (
        <>
          {(filter === 'all' || filter === 'docker') && (
            <section className="section">
              <h2>Docker Status</h2>
              {dockerInfo.containers !== undefined && (
                <div className="stats">
                  <div className="stat">
                    <span>Total Containers</span>
                    <span className="value">{dockerInfo.containers}</span>
                  </div>
                  <div className="stat">
                    <span>Running</span>
                    <span className="value">{dockerInfo.runningContainers}</span>
                  </div>
                  <div className="stat">
                    <span>Stopped</span>
                    <span className="value">{dockerInfo.stoppedContainers}</span>
                  </div>
                  <div className="stat">
                    <span>Images</span>
                    <span className="value">{dockerInfo.images}</span>
                  </div>
                </div>
              )}

              <div className="containers-list">
                {dockerContainers.map((c) => (
                  <div key={c.id} className="container-card">
                    <div className="container-header">
                      <span className="name">{c.name}</span>
                      <span className={`status ${c.status}`}>{c.status}</span>
                    </div>
                    <p className="image">{c.image}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {(filter === 'all' || filter === 'k8s') && (
            <section className="section">
              <h2>Kubernetes Pods</h2>
              <div className="containers-list">
                {k8sPods.map((p) => (
                  <div key={p.name} className="container-card">
                    <div className="container-header">
                      <span className="name">{p.name}</span>
                      <span className={`status ${p.status?.toLowerCase()}`}>
                        {p.status}
                      </span>
                    </div>
                    <p className="namespace">NS: {p.namespace}</p>
                    <p className="image">{p.image}</p>
                  </div>
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  )
}
