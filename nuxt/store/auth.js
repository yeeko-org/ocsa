import ApiService from "./common";
// const cookieparser = process.server ? require('cookieparser') : undefined
// const Cookie = process.client ? require('js-cookie') : undefined
// const Cookie = require('js-cookie')
// import router from '@/router'
// import Cookie from "js-cookie";

const state = () => ({
  counter: 1,
  user_details_ocsa: undefined,
  auth_arropa: null,
  is_authenticated: false,
  is_logged: false,
})

const mutations = {
  SET_TOKEN(state, token) {
    state.auth_arropa = token;
    //ApiService.defaults.headers.common['Authorization'] = `Token ${token}`;
    //ApiService.defaults.headers.common['Authorization'] = "Token 1b38bcac3c4f57a1b57bf48a954111bd54a3f3cf";
  },
  SET_RESET_SUCCESSFUL(state) {
    state.reset_successful = true
  },
  SET_AUTH(state, user) {
    //console.log("SETEAMOS EL USER")
    //console.log(user)
    state.is_authenticated = true;
    state.user_details_ocsa = user;
    state.is_logged = Date.now();
    // Cookie.set('auth_arropa', user.token)
    //console.log(Cookie)
    state.auth_arropa = user.token;
    //console.log()
    //ApiService.saveToken(state.user_details_ocsa.token);
    // Setea los valores del userId de la cookie de Google Analytics
    //setGAUserId(user['id'])
  },
  SET_ORGANIZATION(state, organization) {
    state.user_details_ocsa.profile.organization = organization;
  },
  SET_RESET_HASH(state, hash) {
    state.hash_password = hash
  },
  PURGE_AUTH(state) {
    console.log("!!!SE EJECUTA PURGE_AUTH")
    state.is_authenticated = false;
    state.user_details_ocsa = undefined;
    state.auth_arropa = null;
    // Cookie.remove('auth_arropa')
  },
}

const actions = {
  FROM_SERVER_INIT({commit}, [auth_arropa, psid]){
    //console.log("FROM_SERVER_INIT")
    commit('SET_TOKEN', auth_arropa)
    //commit('SET_PSID', psid)
  },
  SET_HEADER({state}){
    //console.log(state.auth_arropa)
    if (state.auth_arropa){
      let token =  state.auth_arropa
      ApiService.defaults.headers.common['Authorization'] = `Token ${token}`;
    }
    //this.$axios.setToken(token, 'Token')
  },
  CHECK_AUTH_SIMPLE(context){
    console.log("CHECK_AUTH_SIMPLE")
    //console.log("CHECK_AUTH_SIMPLE")
    return new Promise (resolve => {
      //primero comprobamos que exista token de usuario
      if (context.state.auth_arropa) {
        //console.log("hay token")
        let last_login = context.state.is_logged
        if (!!last_login && last_login + (3600*24*1000) > Date.now()){
          console.log("NO hay datos recientes")
          return resolve()
        }
        else{
          console.log("hay datos recientes")
          //Si hay token de usuario, obtiene su info
          context.dispatch('GET_CURRENT_USER')
            .then((dataUser) => {
              resolve(dataUser)
            })
            //Si hay cualquier error se intenta loguear por facebook
            .catch((err) => {
              console.log(err)
            })
        }
      }
      else
        //Si no hay token, directamente intenta generar un login con Facebook
        console.log("NO ESTÁ LOGUEADO")
    })
  },
  LOGIN_MAIL({dispatch}, params){
    return new Promise((resolve) => {
      ApiService.post('/auth/login/', params)
        .then(({data}) => {
          // console.log(data)
          dispatch('HAS_LOGGED', data)
          return resolve(data)
        })
        .catch(err =>{
          // console.log(err)
          return resolve({error:err})
        })
    })
  },
  REGISTER_MAIL({dispatch}, params){
    return new Promise((resolve) => {
      ApiService.post('/auth/register/', params)
        .then(({data}) => {
          dispatch('HAS_LOGGED', data)
          return resolve(data)
        })
    })
  },
  GET_CURRENT_USER({dispatch, state}) {
    let getLogin = () =>
      new Promise(resolve => {
        dispatch('SET_HEADER')
        resolve(ApiService.get('/login/')
          .then(({ data, status }) => {
            if (status !== 204)
              return dispatch('HAS_LOGGED', data)
            else
              return dispatch('HAS_NOT_LOGGED', 'Not Content(204)')
          })
          .catch(error => dispatch('HAS_NOT_LOGGED',
            `ServerError: ${error}`))
        )
      })
    if (state.user_details_ocsa){
      console.log("ya hay logueado, se hace asíncrono el tema")
      //getLogin()
      return state.user_details_ocsa
    }
    else{
      console.log("en el nuxt no hay datos del usuario")
      console.log(state)
      //return getLogin()
      //this.$router.replace({ name: 'Login' });
    }

  },
  SEND_PASSWORD_RESET(context, params){
    return new Promise((resolve) => {
      ApiService.post('/auth/request_password_recovery/', params)
        .then(({data}) => {
          return resolve(data)
        })
        .catch(err =>{
          console.log(err)
          return resolve({error:true})
        })
    })
  },
  CHANGE_PASSWORD({state, commit, dispatch}, params){
    return new Promise((resolve) => {
      ApiService.post('/auth/password_recovery/', params)
        .then(({data}) => {
          dispatch("HAS_LOGGED", data)
          return resolve(data)
        })
        .catch(err =>{
          console.log(err)
          return resolve({error:true})
        })

    })
  },
  LOGOUT(context) {
    context.commit('PURGE_AUTH') // Elimina todas las credenciales
    // return router.push({ path: '/' })
  },
  HAS_NOT_LOGGED({commit}, error_message) {
    console.log(error_message)
    commit('PURGE_AUTH');
    console.log({error:error_message})
  },
  HAS_LOGGED({commit, dispatch, state}, userData) {
    commit('PURGE_AUTH');
    commit('SET_AUTH', userData)
    if (userData.profile && userData.profile.organization){
      console.log("seteamos la organización")
      commit("arropa/SET_ORGANIZATION_ID", userData.profile.organization.id, {root: true})
    }
    dispatch('REDIRECT_LOGIN');
  },
  REDIRECT_LOGIN({state, commit}){
    console.log("REDIRECT_LOGIN")
    // console.log("router2", router)
    // let route_name = router.currentRoute.value.name
    // console.log("route_name", route_name)
    // if (route_name === 'login' || route_name === 'first_init')
    //   return router.push({ path: '/profile'})
    // this.$router.push({ path: '/dashboard'})
  }
}


export default {
  namespaced: true,
  state,
  mutations,
  actions,
}
