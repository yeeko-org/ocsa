import { defineStore } from 'pinia'
import ApiService from "./common";
import colorMixin from "~/mixins/colorMixin";
// import { mande } from 'mande'


const calculate_status = (status_control) => {
  return status_control.reduce((obj, st) => {
    st = colorMixin.methods.getComplementColor(st)
    if (obj[st.group])
      obj[st.group].push(st)
    else
      obj[st.group] = [st]
    return obj
  }, {})
}

const calculate_impact_groups = (impact_types) => {
  return impact_types.reduce((obj, it) => {
    const group = it.is_social ? 'social' : 'environmental'
    obj[group].push(it)
    obj['all'].push(it)
    return obj
  }, {"social": [], "environmental": [], "all": []})
}

const build_positions = () => {
  return {
    "oppose": {
      icon: "record_voice_over", color: "lime", order: 1, name: "En contra"},
    "neutral": {
      icon: "gavel", color: "blue-grey", order: 2, name: "Neutral"},
    "support": {
      icon: "thumb_up", color: "teal", order: 3, name: "A favor"},
    "undefined": {
      icon: "help", color: "black", order: 4, name: "No definido"},
    "other": {
      icon: "help", color: "black", order: 5, name: "Otro"}
  }
}

const calc_megaproject_types = (data) => {
  let extractivism_types = data.extractivism_types.reduce((obj, mp) => {
    obj[mp.id] = mp
    return obj
  }, {})
  const mp_types = data.megaproject_types.map(mpt => {
    const extrac_types = mpt.deployment_capital_types
    if (!extrac_types){
      console.log("No deployment capital types 1", mpt)
      return mpt
    }
    const count = extrac_types.length
    if (count === 1)
      mpt.extractivism_obj = extractivism_types[extrac_types[0]]
    else if (count > 1){
      const names = extrac_types.map(et => extractivism_types[et].name)
      const id = extrac_types.join('-')
      const extractivism_obj = {
        id: id,
        name: `Mixto: ${names.join(', ')}`,
        color: "black",
        icon: "group_work",
        original_types: extrac_types.map(et => extractivism_types[et]),
        description: "Varios tipos de capital",
        help_text: "VARIOS"
      }
      extractivism_types[id] = extractivism_obj
      mpt.extractivism_obj = extractivism_obj
    }
    else
      console.log("No deployment capital types 2", mpt)
    return mpt
  })
  return [mp_types, extractivism_types]
}

export const useMainStore = defineStore('main', {
  state: () => ({
    counter: 0,
    cats: {},
    userData: {},
    projects: [],
    positions: build_positions(),
    status: {},
    status_project: {},
    impact_groups: {social: [], environmental: []},
    megaproject_types: [],
    extractivism_types: {},
  }),
  actions: {
    increment() {
      // `this` is the store instance
      this.counter++
    },
    fetchCatalogs() {
      ApiService.get('/catalogs/all/')
        .then(({data}) => {
          console.log("fetchCatalogs data", data)
          this.cats = data
          this.status = calculate_status(data.status_control)
          this.status_project = calculate_status(data.status_project)
          this.impact_groups = calculate_impact_groups(data.impact_types)
          const result = calc_megaproject_types(data)
          this.megaproject_types = result[0]
          this.extractivism_types = result[1]
          console.log("impact_groups", this.impact_groups)
          return data
        })
        .catch(error => {
          console.error(error)
        })
    },
    // fetchProjects(params) {
    //   console.log('fetchProjects', params)
    //   ApiService.get('/projects/', params)
    //     .then(response => {
    //       console.log(response)
    //       this.projects = response.data
    //       return response
    //     })
    //     .catch(error => {
    //       console.error(error)
    //     })
    // },
    async fetchProjects(params) {
      console.log('fetchProjects', params)
      try {
        const result = await ApiService.get('/project/', {params: params})
        // this.projects = result.data.results
        return result.data
      } catch (error) {
        console.error(error)
      }
    },
    async fetchElements([group, params]) {
      console.log('fetchElements', group, params)
      try {
        const result = await ApiService.get(`/${group}/`, {params: params})
        // this.projects = result.data.results
        return result.data
      } catch (error) {
        console.error(error)
      }
    },
    getSimple([group, id]) {
      return ApiService.get(`/${group}/${id}/`)
        .then(response => {
          return response.data
        })
        .catch(error => {
          console.error(error)
        })
    },
    getProject(id) {
      return ApiService.get(`/project/${id}/`)
        .then(response => {
          return response.data
        })
        .catch(error => {
          console.error(error)
        })
    },
    fetchNotes(params) {
      console.log('fetchNotes', params)
      return ApiService.get('/note/', {params: params})
        .then(response => {
          return response.data
        })
        .catch(error => {
          console.error(error)
        })
    },
    getNote(id) {
      return ApiService.get(`/note/${id}/`)
        .then(response => {
          return response.data
        })
        .catch(error => {
          console.error(error)
        })
    }
    // async registerUser(login, password) {
    //   const api = mande('/api/users')
    //   try {
    //     this.userData = await api.post({ login, password })
    //     // showTooltip(`Welcome back ${this.userData.name}!`)
    //   } catch (error) {
    //     // showTooltip(error)
    //     // let the form component display the error
    //     return error
    //   }
    // },
  },
  getters: {
    double() {
      return this.counter * 2
    },
    status_not() {
      if (!this.cats || !this.cats.status_control)
        return {}
      return this.cats.status_control.reduce((obj, st) => {
        st = colorMixin.methods.getComplementColor(st)
        if (obj[st.group])
          obj[st.group].push(st)
        else
          obj[st.group] = [st]
        return obj
      }, {})
    },
    status_dict(state) {
      if (!state.cats.status_control)
        return {}
      let status_dict = {}
      Object.keys(state.status).forEach(group_key=>{
        status_dict[group_key] = {}
        state.status[group_key].forEach(st=>{
          status_dict[group_key][st.name] = st
        })
      })
      console.log("status_dict", status_dict)
      return status_dict
    },
    event_types() {
      if (!this.cats || !this.cats.impact_types)
        return []
      return this.cats.impact_types.reduce((obj, it) => {
        const group = it.is_social ? 'social' : 'environmental'
        obj[group].push(it)
        return obj
      }, {"social": [], "environmental": []})
    },
  },
})