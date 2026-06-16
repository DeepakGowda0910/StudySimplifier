import api from './client'

export const getCategories = () => api.get('/study/categories').then(r => r.data)
export const getCourses = (cat) => api.get(`/study/courses/${encodeURIComponent(cat)}`).then(r => r.data)
export const getStreams = (cat, course) => api.get(`/study/streams/${encodeURIComponent(cat)}/${encodeURIComponent(course)}`).then(r => r.data)
export const getSubjects = (cat, course, stream) => api.get(`/study/subjects/${encodeURIComponent(cat)}/${encodeURIComponent(course)}/${encodeURIComponent(stream)}`).then(r => r.data)
export const getTopics = (cat, course, stream, subj) => api.get(`/study/topics/${encodeURIComponent(cat)}/${encodeURIComponent(course)}/${encodeURIComponent(stream)}/${encodeURIComponent(subj)}`).then(r => r.data)
export const getChapters = (cat, course, stream, subj, topic) => api.get(`/study/chapters/${encodeURIComponent(cat)}/${encodeURIComponent(course)}/${encodeURIComponent(stream)}/${encodeURIComponent(subj)}/${encodeURIComponent(topic)}`).then(r => r.data)
export const generate = (data) => api.post('/study/generate', data).then(r => r.data)
export const chat = (data) => api.post('/study/chat', data).then(r => r.data)
export const uploadDocument = (formData) => api.post('/study/upload-document', formData, { headers: { 'Content-Type': 'multipart/form-data' }, timeout: 120000 }).then(r => r.data)
