import api from './client'

// Auth
export const schoolRegister = (data) => api.post('/school/register', data).then(r => r.data)
export const schoolLogin = (data) => api.post('/school/login', data).then(r => r.data)
export const schoolJoin = (data) => api.post('/school/join', data).then(r => r.data)

// Admin
export const getAdminOverview = () => api.get('/school/admin/overview').then(r => r.data)
export const generateInvites = (data) => api.post('/school/admin/invites', data).then(r => r.data)
export const listInvites = () => api.get('/school/admin/invites').then(r => r.data)
export const listTeachers = () => api.get('/school/admin/teachers').then(r => r.data)
export const removeTeacher = (id) => api.delete(`/school/admin/teachers/${id}`).then(r => r.data)
export const listStudents = (grade = null) =>
  api.get('/school/admin/students', { params: grade ? { grade } : {} }).then(r => r.data)
export const createClass = (data) => api.post('/school/admin/classes', data).then(r => r.data)
export const listClasses = () => api.get('/school/admin/classes').then(r => r.data)
export const promoteGrade = (data) => api.post('/school/admin/promote', data).then(r => r.data)
export const getReports = () => api.get('/school/admin/reports').then(r => r.data)
export const updateAiProvider = (provider) =>
  api.put('/school/admin/school/ai-provider', null, { params: { provider } }).then(r => r.data)

// Teacher
export const getTeacherDashboard = () => api.get('/school/teacher/dashboard').then(r => r.data)
export const getMyClasses = () => api.get('/school/teacher/classes').then(r => r.data)
export const getClassStudents = (classId) =>
  api.get(`/school/teacher/classes/${classId}/students`).then(r => r.data)
export const getClassProgress = (classId) =>
  api.get(`/school/teacher/classes/${classId}/progress`).then(r => r.data)
export const createAssignment = (data) => api.post('/school/teacher/assignments', data).then(r => r.data)
export const getStudentProgressDetail = (studentId) =>
  api.get(`/school/teacher/students/${studentId}/progress`).then(r => r.data)
