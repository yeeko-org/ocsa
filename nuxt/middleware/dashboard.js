import {useMainStore} from "~/store/index.js";

export default defineNuxtRouteMiddleware((to, from, next) => {
  // console.log('TO', to)
  if (to.path === '/') {
    console.log('redirecting to dashboard')
    return navigateTo('/dashboard')
  }

  const mainStore = useMainStore()
  // console.log('FROM', from)
  const { fetchCatalogs, cats_ready, setCollection, setFilterGroup } = mainStore
  if (to.params.group)
    setCollection(to.params.group)
  else if (to.params.model)
    setFilterGroup(to.params.model)
  if (cats_ready) {
    // next()
    return
  }
  fetchCatalogs()
  //   .then(() => {
  //   next()
  // })
  // console.log('Middleware dashboard.js called', to)
  console.log('after cats')
  // if (to.params.id === '1') {
  //   return abortNavigation()
  // }
  // In a real app you would probably not redirect every route to `/`
  // however it is important to check `to.path` before redirecting or you
  // might get an infinite redirect loop
})