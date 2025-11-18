import { http, setToken } from './request'

const AUTH_PREFIX = '/api/v1/simple'

export async function login({ email, password }) {
  const res = await http.post(`${AUTH_PREFIX}/login`, { email, password })
  if (res?.access_token) setToken(res.access_token)
  return res
}

export async function register({ nickname, email, password }) {
  const res = await http.post(`${AUTH_PREFIX}/register`, { nickname, email, password })
  if (res?.token) setToken(res.token)
  return res
}

export async function logout() {
  try {
    await http.post(`${AUTH_PREFIX}/logout`)
  } finally {
    setToken('')
  }
}



import request from './email.js'

export const getGoogleAuthUrl = () => {
  return request.get('/api/v1/auth/google/url')
}
