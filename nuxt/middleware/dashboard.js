import {useMainStore} from "~/store/index.js";
import {useAuthStore} from "~/store/auth.js";
// import Cookie from "js-cookie";

export default defineNuxtRouteMiddleware((to, from, next) => {
  // console.log('TO', to)
  if (to.path === '/') {
    console.log('redirecting to dashboard')
    return navigateTo('/dashboard')
  }

  const mainStore = useMainStore()
  const authStore = useAuthStore()
  // console.log('FROM', from)
  const {
    fetchCatalogs,
    cats_ready,
    setCollection,
    setFilterGroup,
  } = mainStore
  const { is_logged, checkAuthSimple, authCookie, purgeAuth } = authStore

  // console.log("is_logged", is_logged)
  // console.log("authCookie", authCookie)
  // console.log("Cookie", useCookie())
  // if (!is_logged) {
  //   console.log('redirecting to login')
  //   return navigateTo('/login')
  // }
  if (!authCookie) {
    // console.log('redirecting to login')
    purgeAuth()
    return navigateTo('/login')
  }
  if (!is_logged) {
    // console.log('checking auth')
    checkAuthSimple()
  }

  if (to.params.group)
    setCollection(to.params.group)
  else if (to.params.model)
    setFilterGroup(to.params.model)
  if (cats_ready) {
    // next()
    return
  }
  fetchCatalogs()
  console.log('after cats')

  console.log('after_check_auth')

  //   .then(() => {
  //   next()
  // })
  // console.log('Middleware dashboard.js called', to)
  // if (to.params.id === '1') {
  //   return abortNavigation()
  // }
  // In a real app you would probably not redirect every route to `/`
  // however it is important to check `to.path` before redirecting or you
  // might get an infinite redirect loop
})