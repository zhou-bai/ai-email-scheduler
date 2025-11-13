// 轻量 fetch 封装，集中处理 Base URL、Headers、Token 与错误

const BASE_URL = import.meta?.env?.VITE_API_BASE_URL || 'http://localhost:8000'
const AUTH_TOKEN_KEY = 'authToken'

export function getToken() {
  try {
    return localStorage.getItem(AUTH_TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

export function setToken(token) {
  try {
    if (token) {
      localStorage.setItem(AUTH_TOKEN_KEY, token)
    } else {
      localStorage.removeItem(AUTH_TOKEN_KEY)
    }
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new Event('auth-change'))
    }
  } catch {
    // 忽略存储异常
  }
}

export async function request(path, options = {}) {
  const url = path.startsWith('http') ? path : `${BASE_URL}${path}`

  const headers = new Headers(options.headers || {})
  if (!headers.has('Content-Type') && options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  const token = getToken()
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  const resp = await fetch(url, {
    method: options.method || 'GET',
    headers,
    body: options.body && headers.get('Content-Type') === 'application/json'
      ? JSON.stringify(options.body)
      : options.body,
    credentials: 'omit',
    signal: options.signal
  })

  const contentType = resp.headers.get('content-type') || ''
  const isJson = contentType.includes('application/json')
  const data = isJson ? await resp.json().catch(() => ({})) : await resp.text()

  if (!resp.ok) {
    const message = isJson ? (data?.message || '请求失败') : (data || '请求失败')
    const error = new Error(message)
    error.status = resp.status
    error.data = data
    throw error
  }

  return data
}

export const http = {
  get: (path, params, options = {}) => {
    const query = params
      ? '?' + new URLSearchParams(params).toString()
      : ''
    return request(`${path}${query}`, { ...options, method: 'GET' })
  },
  post: (path, body, options = {}) =>
    request(path, { ...options, method: 'POST', body }),
  put: (path, body, options = {}) =>
    request(path, { ...options, method: 'PUT', body }),
  patch: (path, body, options = {}) =>
    request(path, { ...options, method: 'PATCH', body }),
  delete: (path, body, options = {}) =>
    request(path, { ...options, method: 'DELETE', body })
}


