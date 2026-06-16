import api from './client'

export const getExams = () => api.get('/planner/exams').then(r => r.data)
export const createExam = (data) => api.post('/planner/exams', data).then(r => r.data)
export const deleteExam = (id) => api.delete(`/planner/exams/${id}`).then(r => r.data)
export const generatePlan = (data) => api.post('/planner/generate-plan', data).then(r => r.data)
export const getPlans = () => api.get('/planner/plans').then(r => r.data)
export const recordPomodoro = (subject, duration) => api.post(`/planner/pomodoro?subject=${subject || ''}&duration=${duration}`).then(r => r.data)
export const getPomodoroStats = () => api.get('/planner/pomodoro/stats').then(r => r.data)
