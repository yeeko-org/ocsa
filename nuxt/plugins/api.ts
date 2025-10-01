import axios from 'axios'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  const api = axios.create({
    baseURL: config.public.apiUrl,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  api.interceptors.request.use((config) => {
    const cookie_auth = useCookie('auth_ocsa')

    if (cookie_auth.value) {
      config.headers.Authorization = `Token ${cookie_auth.value}`
    }
    return config
  })
  return {
    provide: {
      api: api
    }
  }
})