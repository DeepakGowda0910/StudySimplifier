import api from './client'

export const generateQuiz = (data) => api.post('/quiz/generate', data).then(r => r.data)
export const submitQuiz = (data) => api.post('/quiz/submit', data).then(r => r.data)
export const getMistakes = () => api.get('/quiz/mistakes').then(r => r.data)
export const getEloRatings = () => api.get('/quiz/elo').then(r => r.data)
export const getQuizHistory = () => api.get('/quiz/history').then(r => r.data)
