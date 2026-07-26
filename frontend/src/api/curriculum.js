import api from './client'

// Student curriculum
export const getStudentDashboard = () => api.get('/school/student/dashboard').then(r => r.data)
export const getCurriculum = () => api.get('/school/student/curriculum').then(r => r.data)
export const getLesson = (lessonId) => api.get(`/school/student/lessons/${lessonId}`).then(r => r.data)
export const completeLesson = (lessonId, data) =>
  api.post(`/school/student/lessons/${lessonId}/complete`, data).then(r => r.data)
export const getMyProgress = () => api.get('/school/student/progress').then(r => r.data)
export const askTutor = (data) => api.post('/school/student/ask', data).then(r => r.data)
