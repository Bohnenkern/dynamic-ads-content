import { useState, useEffect } from 'react'
import './App.css'
import api from './services/api'

function App() {
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const response = await api.get('/')
      setMessage(response.data.message)
    } catch (error) {
      console.error('Error fetching data:', error)
      setMessage('Error connecting to API')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Dynamic Ads Content</h1>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <p>{message}</p>
        )}
      </header>
    </div>
  )
}

export default App
