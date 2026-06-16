import api from './client'

export const getDailyAgenda = () => api.get('/agent/daily-agenda').then(r => r.data)
export const regenerateAgenda = () => api.post('/agent/regenerate-agenda').then(r => r.data)
export const getWeakSpots = () => api.get('/agent/weak-spots').then(r => r.data)
export const getPerformanceSummary = () => api.get('/agent/performance-summary').then(r => r.data)
export const generateKnowledgeGraph = (data) => api.post('/agent/knowledge-graph', data).then(r => r.data)
