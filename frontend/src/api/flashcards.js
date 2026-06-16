import api from './client'

export const getAll = () => api.get('/flashcards/').then(r => r.data)
export const getDue = () => api.get('/flashcards/due').then(r => r.data)
export const create = (data) => api.post('/flashcards/', data).then(r => r.data)
export const generate = (data) => api.post('/flashcards/generate', data).then(r => r.data)
export const review = (id, data) => api.post(`/flashcards/${id}/review`, data).then(r => r.data)
export const remove = (id) => api.delete(`/flashcards/${id}`).then(r => r.data)
