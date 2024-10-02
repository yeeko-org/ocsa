import { defineStore } from 'pinia'
import ApiService from "./common";
import colorMixin from "~/mixins/colorMixin";
// import { mande } from 'mande'
import { menu_content } from "~/composables/menu.js";

const group_list = [
  {name: "Notas", key: "note", color: 'deep-purple', icon: 'newspaper'},
  {name: "Proyectos", key: "project", color: 'purple', icon: 'factory'},
  {name: "Actores", key: "actor", color: 'blue', icon: 'people'},
  {name: "Eventos", key: "event", color: 'light-blue', icon: 'notifications_active'},
]

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

const buildFullMenu = () => {
  return menu_content.reduce((arr, group) => {
    arr.push(group)
    if (group.catalogs)
      group.catalogs.forEach(catalog => {
        arr.push({...catalog, parent: group})
      })
    return arr
  }, [])

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
  extractivism_types['other'] = {
    id: 'other',
    name: 'No definidos (con subtipos)',
    color: 'black',
    icon: 'help',
    description: 'Otro tipo de capital',
    help_text: 'OTRO'
  }
  const mp_types = data.megaproject_types.map(mpt => {
    const extrac_types = mpt.extractivism_types
    if (!extrac_types){
      console.log("No extractivism types 1", mpt)
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
      mpt.extractivism_obj = extractivism_types['other']
    return mpt
  })
  return [mp_types, extractivism_types]
}

const compute_counts = (result, original_elements) => {
  result.data.results = result.data.results.map(nmp => {
    const mp = original_elements.find(mp => mp.id === nmp.id)
    // mp.count = nmp.count
    return {...mp, count: nmp.count}
  })
  return result.data
}

const calc_event_subtypes = (data) => {
  let event_types = data.event_types.reduce((obj, it) => {
    it.event_group = data.event_groups.find(eg => eg.id === it.group)
    obj[it.id] = it
    return obj
  }, {})
  const event_subtypes = data.event_subtypes.map(subtype => {
    const ev_types = subtype.event_types
    if (!ev_types) {
      console.log("No event types 1", subtype)
      return subtype
    }
    const count = ev_types.length
    if (count === 1)
      subtype.event_type_obj = event_types[ev_types[0]]
    else if (count > 1) {
      const names = ev_types.map(et => event_types[et].name)
      const id = ev_types.join('-')
      const event_obj = {
        id: id,
        name: `Mixto: ${names.join(', ')}`,
        original_types: ev_types.map(et => event_types[et]),
        help_text: "VARIOS",
        event_group: event_types[ev_types[0]].event_group
      }
      event_types[id] = event_obj
      subtype.event_type_obj = event_obj
    } else {
      console.log("No event types 2", subtype)
      // subtype.event_obj = event_types['other']
    }
    return subtype
  })
  return [event_subtypes, event_types]

}

export const useMainStore = defineStore('main', {
  state: () => ({
    counter: 0,
    cats: {},
    cats_ready: false,
    userData: {},
    projects: [],
    positions: build_positions(),
    status: {},
    status_project: {},
    impact_groups: {social: [], environmental: []},
    extractivism_types: {},
    megaproject_types: [],
    event_types: {},
    event_subtypes: [],
    groups: menu_content,
    all_groups: buildFullMenu(),
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
          this.cats_ready = true
          this.status = calculate_status(data.status_control)
          this.status_project = calculate_status(data.status_project)
          this.impact_groups = calculate_impact_groups(data.impact_types)
          const result = calc_megaproject_types(data)
          this.megaproject_types = result[0]
          this.extractivism_types = result[1]
          const result_event = calc_event_subtypes(data)
          this.event_subtypes = result_event[0]
          this.event_types = result_event[1]
          // console.log("impact_groups", this.impact_groups)
          return data
        })
        .catch(error => {
          console.error(error)
        })
    },
    async fetchElements([group, params]) {
      // console.log('fetchElements', group, params)
      try {
        const result = await ApiService.get(`/${group}/`, {params: params})
        if (group.includes('catalogs/')){
          const real_group = group.split('/')[1]
          if (real_group === 'extractivism_type')
            return compute_counts(result, this.megaproject_types)
        }
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
    impact_types() {
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