import { defineStore } from 'pinia'
import ApiService from "./common";
import colorMixin from "~/mixins/colorMixin";
// import { mande } from 'mande'
// import { menu_content } from "~/composables/menu.js";
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
  const has_fields = [
    "comments", "description", "help_text", "order", "color", "icon"]
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
    const primary_key = coll.fields.find(f => f.primary_key)
    coll.pk = primary_key ? primary_key.name : 'id'
    coll.name_field = coll.fields.some(f => f.name === 'name')
      ? 'name'
      : coll.fields.some(f => f.name === 'title')
        ? 'title'
        : null
    coll.has = has_fields.reduce((obj, field) => {
      obj[field] = coll.fields.some(f => f.name === field)
      return obj
    }, {})
    const other_fields = has_fields.concat([coll.pk, coll.name_field])
    coll.other_fields = coll.fields.filter(f =>
      !other_fields.includes(f.name) && f.relation_type === 'simple')
    return coll
  })

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

function getLastId(data) {
  const id = data.id || data.key_name
  const method = id ? 'put' : 'post'
  const last_id = id ? `${id}/` : ''
  return { method, last_id }
}

export const useMainStore = defineStore('main', {
  state: () => ({
    cats: null,
    all_nodes: {},
    schemas: {},
    cats_ready: false,
    positions: build_positions(),
    status: {},
    impact_groups: {social: [], environmental: []},
    current_filter_group: null,
    current_filter_group_data: null,
    current_collection: null,
    current_collection_data: null,
    // groups: menu_content,
    full_geo: {"state": {}, "municipality": {}},
  }),
  actions: {
    setHeader() {
      const cookie_auth = useCookie('auth_ocsa')
      if (cookie_auth.value) {
        ApiService.defaults.headers.common['Authorization'] = `Token ${cookie_auth.value}`
      }
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
    async getSimple([group, id]) {
      this.setHeader()
      try {
        let response = await ApiService.get(`/${group}/${id}/`);
        return response.data
      } catch (error) {
        console.error(error)
        ;
      }
    },
    async getGeo([group, id]) {
      if (this.full_geo[group][id])
        return
      this.full_geo[group][id] = []
      this.setHeader()
      try {
        let response = await ApiService.get(`space_time/${group}/${id}/`);
        // console.log("getGeo", response.data)
        // this.full_states[id] = response.data.municipalities
        const child = group === 'state' ? 'municipalities' : 'localities'
        this.full_geo[group][id] = response.data[child]
        return response.data
      } catch (error) {
        console.error(error)
        ;
      }
    },
    async saveSimple([collection, data]) {
      this.setHeader()
      const { method, last_id } = getLastId(data)
      try {
        let response = await ApiService[method](`/${collection}/${last_id}`, data);
        return response.data
      } catch (error) {
        console.error(error);
      }
    },
    async saveCatalog([collection_data, data]) {
      this.setHeader()
      const { method, last_id } = getLastId(data)
      const collection = collection_data.snake_name
      const full_url = `catalogs/${collection}/${last_id}`
      try {
        let response = await ApiService[method](full_url, data);
        let real_group = `${collection}s`
        if (collection === 'country')
          real_group = 'countries'
        if (method === 'post')
          this.cats[real_group].unshift(response.data)
        else {
          const elem_id = response.data.id ? 'id' : 'key_name'
          const index = this.cats[real_group].findIndex(
            el => el[elem_id] === response.data[elem_id])
          this.cats[real_group][index] = response.data
        }
        return response.data
      } catch (error) {
        console.error(error);
      }
    },
    async patchSimple([collection, id, data]) {
      this.setHeader()
      try {
        let response = await ApiService.patch(`/${collection}/${id}/`, data);
        return response.data
      } catch (error) {
        console.error(error);
      }
    },
    async deleteSimple([group, id]) {
      this.setHeader()
      try {
        await ApiService.delete(`/${group}/${id}/`);
        return id
      } catch (error) {
        console.error(error)
        ;
      }
    },
    async deleteCatalog([collection_data, id]) {
      this.setHeader()
      const collection = collection_data.snake_name
      const full_url = `catalogs/${collection}/${id}`
      try {
        await ApiService.delete(full_url);
        let real_group = `${collection}s`
        if (collection === 'country')
          real_group = 'countries'
        const index = this.cats[real_group].findIndex(
          el => el.id === id)
        this.cats[real_group].splice(index, 1)
        return id
      } catch (error) {
        console.error(error)
        ;
      }
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
    async saveFile([elem_id, file_data, coll_name]) {
      try {
        console.log('elem_id', elem_id)
        let response = await ApiService.post(
          `/${coll_name}/${elem_id}/add_file/`, file_data,
          {headers: {
            'Content-Type': 'multipart/form-data'
          }});
        return response.data
      } catch (error) {
        console.error(error);
      }
    },
  },
  getters: {
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