import api from './client'

export const getProfile = () => api.get('/user/profile').then(r => r.data)
export const updateProfile = (data) => api.put('/user/profile', data).then(r => r.data)
export const getStats = () => api.get('/user/stats').then(r => r.data)
export const recordSession = (data) => api.post('/user/study-session', data).then(r => r.data)
export const getAnalytics = () => api.get('/user/analytics').then(r => r.data)
export const getLeaderboard = () => api.get('/user/leaderboard').then(r => r.data)
export const getAchievements = () => api.get('/user/achievements').then(r => r.data)
