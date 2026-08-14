import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState('loading')
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('http://192.168.217.163:3001/health')
      .then(res => res.json())
      .then(data => {
        setStatus('connected')
        setData(data)
      })
      .catch(err => {
        setStatus('error')
        console.error('Backend error:', err)
      })
  }, [])

  return (
    <div className="App">
      <h1>ContainerGuard v2.0</h1>
      <p>Status: {status}</p>
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  )
}

export default App
