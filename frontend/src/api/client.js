import axios from 'axios'
import toast from 'react-hot-toast'

const api = axios.create({ baseURL: '/api', timeout: 60000 })

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('studysmart-auth')
  if (raw) {
    try {
      const { state } = JSON.parse(raw)
      if (state?.token) config.headers.Authorization = `Bearer ${state.token}`
    } catch {}
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('studysmart-auth')
      window.location.href = '/login'
    } else if (err.response?.status >= 500) {
      toast.error('Server error. Please try again.')
    }
    return Promise.reject(err)
  }
)

export default api
