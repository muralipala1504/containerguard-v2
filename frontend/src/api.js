import axios from 'axios'
const API = axios.create({ baseURL: 'http://192.168.217.163:8000', timeout: 5000 })
export const getAgents = () => API.get('/api/agents')
export const getEvents = (agentId=null, limit=50) => API.get('/api/events', { params: agentId ? {agent_id: agentId, limit} : {limit} })
export const getDashboardStats = () => API.get('/api/dashboard/stats')
