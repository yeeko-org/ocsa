import { defineStore } from "pinia";
// import Cookie from "js-cookie";
import ApiService from "~/store/common.js";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    is_authenticated: false,
    is_logged: false,
    auth_ocsa: null,
    user_details_ocsa: null,
    is_logging_in: true,
    dialog_login: false
  }),
  actions: {
    setToken(token) {
      this.auth_ocsa = token
      //ApiService.defaults.headers.common['Authorization'] = `Token ${token}`;
      //ApiService.defaults.headers.common['Authorization
    },
    setAuth(user, from_mid=true) {
      console.log("setAuth")
      this.is_authenticated = true
      this.user_details_ocsa = user
      this.is_logged = Date.now()
      this.is_logging_in = false
      // Cookie.set('auth_ocsa', user.token)
      // console.log("Cookie", Cookie)
      // console.log("auth_ocsa", Cookie.get('auth_ocsa'))
      if (!from_mid){
        const token = useCookie('auth_ocsa')
        token.value = user.token
      }
      this.auth_ocsa = user.token
    },
    setHeader() {
      if (this.auth_ocsa) {
        let token = this.auth_ocsa
        ApiService.defaults.headers.common['Authorization'] = `Token ${token}`
      }
    },
    checkAuthSimple() {
      // const cookie_auth = Cookie.get('auth_ocsa')
      const cookie_auth = useCookie('auth_ocsa')

      // console.log("checkAuthSimple")
      return new Promise((resolve) => {
        if (this.is_logged) {
          // console.log("hay auth", this.auth_ocsa)
          let last_login = this.is_logged
          if (!!last_login && last_login + (3600*24*1000) > Date.now()){
            // console.log("NO hay datos recientes")
            this.purgeAuth()
            return resolve()
          }
          else{
            // console.log("hay datos recientes")
          }
        }
        else if (cookie_auth.value) {
          // console.log("hay cookie", this.auth_ocsa)
          this.auth_ocsa = cookie_auth.value
          this.setHeader()
          this.getLogin()
        }
        else {
          // console.log("NO ESTÁ LOGUEADO")
          return resolve()
        }
        return resolve(this.getCurrentUser())
      })
    },
    getCurrentUser() {
      if (this.user_details_ocsa){
        return this.user_details_ocsa
      }
      else{
        // console.log("en el nuxt no hay datos del usuario")
        return null
      }
    },
    getLogin() {
      // console.log("getLogin")
      // return new Promise((resolve) => {
      this.setHeader()
      ApiService.get('/login/')
        .then(({data, status}) => {
          if (status !== 204)
            return this.hasLogged(data)
          else
            return this.hasNotLogged('Not Content (204)')
        })
        .catch(err =>{
          console.log("LOGIN_ERROR", err)
          return this.hasNotLogged(`Server error: ${err}`)
        })
      // })
    },
    loginMail(params) {
      return new Promise((resolve) => {
        ApiService.post('/login/', params)
          .then(({data}) => {
            this.hasLogged(data, false)
            return resolve(data)
          })
          .catch(err =>{
            return resolve({error:err})
          })
      })
    },
    hasLogged(userData, from_mid=true) {
      this.purgeAuth(from_mid)
      this.setAuth(userData, from_mid)
      // if (userData.profile && userData.profile.organization){
      //   console.log("seteamos la organización")
      //   commit("arropa/SET_ORGANIZATION_ID", userData.profile.organization.id, {root: true})
      // }
      if (!from_mid){
        this.redirectLogin()
      }
    },
    hasNotLogged(error) {
      this.is_logging_in = false
      console.error(error)
      this.purgeAuth()
      return null
    },
    redirectLogin() {
      const router = useRouter()
      return router.push({ path: '/dashboard'})
      // return $router.push({ path: '/dashboard'})
    },
    purgeAuth(from_mid=true) {
      // console.log("purgeAuth")
      this.is_authenticated = false
      this.user_details_ocsa = null
      this.auth_ocsa = null
      // Cookie.remove('auth_ocsa')
      if (!from_mid){
        const token = useCookie('auth_ocsa')
        token.value = null
      }
    },
    logout() {
      const router = useRouter()
      // const route = useRoute()
      this.purgeAuth(false)
      return router.push({ path: '/login' })
    }
  },
  getters: {
    authCookie() {
      // console.log("Cookie", Cookie)
      // console.log("authCookie", Cookie.get('auth_ocsa'))
      const token = useCookie('auth_ocsa')
      return token.value
      // return true
    }
  }

});