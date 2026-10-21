import axios from 'axios'

export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()

  // Bajo ocsa.ibero.mx el API se consume same-origin vía el proxy /api-ocsa
  // del nginx de la Ibero (adr-0015); en SSR y en los demás dominios la URL
  // absoluta sigue siendo necesaria.
  const isIbero =
    import.meta.client && window.location.host === 'ocsa.ibero.mx'

  const api = axios.create({
    baseURL: isIbero ? '/api-ocsa' : config.public.apiUrl,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  api.interceptors.request.use(async (config) => {
    // Axios corre el interceptor fuera del contexto síncrono del plugin, y
    // ahí useCookie no encuentra la instancia de Nuxt. En SSR runWithContext
    // devuelve una promesa; en el cliente, el ref directo (el await no estorba).
    const cookie_auth = await nuxtApp.runWithContext(
      () => useCookie('auth_ocsa'))

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