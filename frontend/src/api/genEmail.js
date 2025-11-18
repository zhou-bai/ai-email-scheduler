import { http } from './request'

const AUTH_PREFIX = '/api/v1/emails'


export async function generateEmail(payload) {
    const res = await http.post(`${AUTH_PREFIX}/generate`, payload)
  return res
}

export async function sendEmail(payload) {
  const res = await http.post(`${AUTH_PREFIX}/send`, payload)
  return res
}