import request from './email.js'

export const getGoogleAuthUrl = () => {
  return request.get('/api/v1/auth/google/url')
}
