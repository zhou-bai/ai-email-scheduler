import { http, setToken } from './request'

const AUTH_PREFIX = '/api/auth'

export async function login({ email, password }) {
  const res = await http.post(`${AUTH_PREFIX}/login`, { email, password })
  if (res?.token) setToken(res.token)
  return res
}

export async function register({ name, email, password }) {
  const res = await http.post(`${AUTH_PREFIX}/register`, { name, email, password })
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



