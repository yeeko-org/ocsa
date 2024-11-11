import { defineStore } from 'pinia'
import ApiService from "./common";
import colorMixin from "~/mixins/colorMixin";
// import { mande } from 'mande'
import { menu_content } from "~/composables/menu.js";
import * as d3 from 'd3';

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

const calculateSchemas = (data) => {
  let filter_groups = data.filter_groups.map(fg => {
    fg.links = data.collection_links.filter(cl =>
      cl.filter_group === fg.key_name)
    return {...fg, ...fg.addl_config}
  })
  let collections = data.collections.map(coll => {
    coll.catalog_groups =  filter_groups.reduce((arr, new_fg) => {
      if (new_fg.main_collection !== coll.snake_name)
        return arr
      if (new_fg.category_group)
        new_fg.category_groups = data[`${new_fg.category_group}s`] || []
      return [...arr, new_fg]
    }, [])
    coll.categories = data.collection_links.filter(
      cl => cl.child === coll.snake_name && cl.link_type === 'category')
    coll.child_relations = data.collection_links.filter(cl =>
      cl.parent === coll.snake_name && cl.link_type)
    coll.parent_relations = data.collection_links.filter(cl =>
      cl.child === coll.snake_name && cl.link_type !== 'category'
    )
    return coll
  })
  // console.log("collections", collections)
  let collections_dict = collections.reduce((obj, coll) => {
    obj[coll.snake_name] = coll
    obj[coll.model_name] = coll
    return obj
  }, {})
  const filters_dict = filter_groups.reduce((obj, fg) => {
    obj[fg.key_name] = fg
    return obj
  }, {})
  // console.log("filters_dict", filters_dict)
  // LINK TYPES
  // category
  // grouper
  // relational

  // FILTER FIELDS
  // category_group
  // category_type
  // category_subtype

  // COLLECTION LEVELS
  // primary
  // secondary
  // relational
  // category_group
  // category_type
  // category_subtype
  return {
    "collections": collections,
    "collections_dict": collections_dict,
    "filter_groups": filter_groups,
    "levels": data.levels,
    "collection_links": data.collection_links,
    "filters_dict": filters_dict,
  }
}

const calculateNewCats = (data, schemas) => {
  let all_nodes = {}
  schemas.filter_groups.forEach(fg => {
    if (fg.key_name === 'geographicals')
      return
    const is_multiple = fg.links.some(l => l.is_multiple)
    // console.log("filter_group:", fg.key_name, is_multiple)
    // v-else-if="!filter_box.category_group && !filter_box.category_type"
    const subtype_key = fg.category_subtype
    const type_key = fg.category_type
    const group_key = fg.category_group
    let subtypes = data[`${subtype_key}s`] || data[subtype_key]
    if (subtype_key === 'country')
      subtypes = data.countries
    let types = data[`${type_key}s`] || []
    let groups = data[`${group_key}s`] || []
    let root = {
      new_id: "root",
      parent: null,
      name: "root",
    }
    root = {...root, ...fg}
    let new_types = []
    let types_dict = {}
    subtypes = subtypes.map(st => {
      if (is_multiple){
        let all_types = st[`${type_key}s`]
        all_types.forEach(t => {
          if (!types_dict[t])
            types_dict[t] = []
          types_dict[t].push(st)
        })
        if (all_types.length === 1)
          st.parent_id = `type_${all_types[0]}`
        else{
          const first_type = types.find(t => t.id === all_types[0])
          let new_type_key = ''
          if (!first_type){
            new_type_key = 'other'
          }
          else if (group_key)
            new_type_key = first_type[`${group_key}`]
          const join_id = all_types.join('_')
          const names = all_types.map(t =>
            types.find(tt => tt.id === t).name)
          st.parent_id = `type_${join_id}`
          if (!new_types.find(t => t.id === join_id)){
            let new_type = {
              id: join_id,
              name: `Mixto: ${names ? names.join(', ') : 'desconocidos'}`,
              original_types: all_types.map(t =>
                types.find(tt => tt.id === t)),
              parent_id: `type_${all_types[0]}`,
              new_id: `type_${join_id}`,
              color: "black",
              icon: "group_work",
              is_mix: true,
            }
            if (group_key)
              new_type[group_key] = new_type_key
            new_types.push(new_type)
          }
        }
      }
      else{
        const value = st[type_key]
        st.parent_id = type_key ? `type_${value}` : "root"
      }
      st.new_id = `subtype_${st.id}`
      return st
    })
    types = [...types, ...new_types]
    types = types.map(t => {
      if (group_key && !t[group_key]) {
        console.log("No group key", t)
      }
      t.parent_id = group_key ? `group_${t[group_key]}` : "root"
      t.new_id = `type_${t.id}`
      if (is_multiple)
        t.all_childs = types_dict[t.id]
      return t
    })
    groups = groups.map(g => {
      g.parent_id = "root"
      g.new_id = `group_${g.id}`
      return g
    })
    const all_data = [...subtypes, ...types, ...groups, root]

    try{
      all_nodes[fg.key_name] = d3.stratify()
        .id(d => d.new_id)
        .parentId(d => d.parent_id)
        (all_data)
      // find id 'subtype_1' and get all children
      // console.log("new_cats", new_cats[fg.key_name].find(d => d.id === 'subtype_1').descendants())
    }
    catch (e){
      console.log("Error", e)
      console.log("all_data", all_data)
      console.log("subtype_key", subtype_key)
      console.log("type_key", type_key)
      console.log("group_key", group_key)

      console.log("subtypes", subtypes)
      console.log("types", types)
      console.log("groups", groups)
    }
  })
  // console.log("new_cats", all_nodes)
  return all_nodes
}


export const useMainStore = defineStore('main', {
  state: () => ({
    counter: 0,
    cats: null,
    all_nodes: {},
    schemas: {},
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
    current_filter_group: null,
    current_filter_group_data: null,
    current_collection: null,
    current_collection_data: null,
    groups: menu_content,
  }),
  actions: {
    increment() {
      // `this` is the store instance
      this.counter++
    },
    setFilterGroup(group) {
      this.current_filter_group = group
      if (this.cats_ready)
        this.setFilterGroupData()
    },
    setFilterGroupData() {
      this.current_filter_group_data = this.all_nodes[
        this.current_filter_group]
    },
    setCollection(group) {
      this.current_collection = group
      if (this.cats_ready)
        this.setCollectionData()
    },
    setCollectionData() {
      this.current_collection_data = this.schemas.collections_dict[
        this.current_collection]
    },
    fetchCatalogs() {
      console.log("fetchCatalogs init")
      return new Promise((resolve) => {
        ApiService.get('/catalogs/all/')
          .then(({data}) => {
            // console.log("fetchCatalogs data", data)
            this.cats = data
            this.schemas = calculateSchemas(data)
            // console.log("schemas", this.schemas)
            this.all_nodes = calculateNewCats(data, this.schemas)
            this.status = calculate_status(data.status_control)
            this.status_project = calculate_status(data.status_project)
            this.setCollectionData()
            this.setFilterGroupData()
            this.cats_ready = true
            console.log("fetchCatalogs end")
            resolve(data)
          })
          .catch(error => {
            console.error(error)
          })
      })
    },
    async fetchElements([group, params]) {
      // console.log('fetchElements', group, params)
      try {
        const result = await ApiService.get(`/${group}/`, {params: params})
        // if (group.includes('catalogs/')){
        //   const real_group = group.split('/')[1]
        // }
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
    // saveSimple([group, data]) {
    //   return ApiService.post(`/${group}/`, data)
    //     .then(response => {
    //       return response.data
    //     })
    //     .catch(error => {
    //       console.error(error)
    //     })
    // },
    saveSimple([collection, data]) {
      console.log("saveSimple", collection, data)
      const id = data.id
      const method = id ? 'put' : 'post'
      const last_id = id ? `${id}/` : ''
      return ApiService[method](`/${collection}/${last_id}`, data)
        .then(response => {
          return response.data
        })
        .catch(error => {
          console.error(error)
        })
    },
    deleteSimple([group, id]) {
      return ApiService.delete(`/${group}/${id}/`)
        .then(() => {
          return id
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
      // console.log("status_dict", status_dict)
      return status_dict
    },
  },
})