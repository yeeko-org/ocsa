// import ApiService from "./common";
// import { mande } from 'mande'
import { defineStore } from 'pinia'
import colorMixin from "~/mixins/colorMixin";
import * as d3 from 'd3';
import axios from "axios";
import {status_filters} from "~/composables/filters.js";
let request = axios.CancelToken.source();

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
    return {...fg, ...fg.addl_config}
  })
  const filters_dict = filter_groups.reduce((obj, fg) => {
    obj[fg.key_name] = fg
    return obj
  }, {})
  const has_fields = [
    "comments", "description", "help_text", "order", "color", "icon"]
  // const name_fields = ["name", "title", "description"]
  const name_fields = ["name", "title"]
  let collections = data.collections.map(coll => {
    coll.catalog_groups = filter_groups.reduce((arr, new_fg) => {
      if (new_fg.main_collection !== coll.snake_name)
        return arr
      const cat_group = new_fg.category_group || new_fg.special_group
      if (cat_group)
        new_fg.category_groups = data[cat_group] || []
      return [...arr, new_fg]
    }, [])
    const valid_relations = ['one_to_many', 'many_to_many']
    coll.child_relation_fields = coll.fields.filter(field => {
      return valid_relations.includes(field.relation_type)
    })
    const primary_key = coll.fields.find(f => f.primary_key)
    coll.pk = primary_key ? primary_key.name : 'id'
    name_fields.forEach(field => {
      if (coll.name_field)
        return
      if (coll.fields.some(f => f.name === field))
        coll.name_field = field
    })
    coll.has = has_fields.reduce((obj, field) => {
      obj[field] = coll.fields.some(f => f.name === field)
      return obj
    }, {})
    const other_fields = has_fields.concat([coll.pk, coll.name_field])
    coll.other_fields = coll.fields.filter(f =>
      !other_fields.includes(f.name) && f.relation_type === 'simple')

    const all_filters = coll.all_filters || []

    let available_sorts = [
      {
        title: "Más recientes",
        value: "-id"
      },
      {
        title: "Más antiguos",
        value: "id"
      },
    ]

    let collection_filters = all_filters.reduce((arr, filter) => {
      if (!filter.filter_name){
        arr.push({...filter, order: 12, is_custom: true})
        return arr
      }
      const filter_data = filters_dict[filter.filter_name]
      if (!filter_data){
        console.error("No filter data", filter.filter_name)
        return arr
      }
      const new_filter = {...filter_data, ...filter}
      // if (filter_data.category_group){
      //   const category_groups = data[filter_data.category_group] || []
      //   category_groups.forEach(cat_group => {
      //     const short_name = `${new_filter.short_prev} ${cat_group.name}`
      //     const name = `${new_filter.prev} ${cat_group.name}`
      //     let current_filter = {
      //       name,
      //       short_name,
      //       category_group_value: cat_group.id,
      //       original_name: new_filter.name
      //     }
      //     arr.push({...new_filter, ...cat_group, ...current_filter})
      //   })
      //   return arr
      // }
      arr.push(new_filter)
      if (filter_data.category_group){
        console.log("collection", coll.snake_name)
        console.log("new_filter with category_group", new_filter)
      }
      return arr
    }, [])
    coll.is_category = coll.level.includes('category_')
    if (coll.is_category){
      const fg = filter_groups.find(fg => fg[coll.level] === coll.snake_name)
      // const fg = filters_dict[coll.snake_name]
      if (fg){
        coll.filter_group = fg
        const short_level = coll.level.replace('category_', '')
        const new_filter_group = {
          ...fg,
          short_name: `${fg.short_prev} ${fg.name}`,
          name: `${fg.prev} ${fg.name}`,
          original_name: fg.name,
          forced_level: short_level,
          order: 1,
          hide_in_filter: false,
        }
        collection_filters.push(new_filter_group)
      }
    }

    const status_groups = coll.fields.reduce((arr, field)=>{
      if (field.related_model === 'StatusControl')
        arr.push(field.name)
      return arr
    }, [])
    coll.status_groups = status_groups
    status_groups.forEach(sg => {
      const status = status_filters[sg]
      collection_filters.push(status)
      available_sorts.push({
        value: `${status.collection}__order`,
        title: `Status ${status.name}`
      })
    })
    if (coll.name_field)
      available_sorts.push({
        title: "Nombre / Título",
        value: coll.name_field
      })
    if (coll.has.order)
      available_sorts.push({
        title: "Orden",
        value: "order"
      })
    collection_filters = collection_filters.sort((a, b) => a.order - b.order)

    coll.collection_filters = collection_filters
    coll.available_sorts = available_sorts
    return coll
  })

  let collections_dict = collections.reduce((obj, coll) => {
    obj[coll.snake_name] = coll
    obj[coll.model_name] = coll
    return obj
  }, {})
  return {
    "collections": collections,
    "collections_dict": collections_dict,
    "filter_groups": filter_groups,
    "levels": data.levels,
    "filters_dict": filters_dict,
  }
}

const hydrateFilterGroup = (fg, data, collections_dict) => {
    const group_key = fg.category_group
    const type_key = fg.category_type
    const subtype_key = fg.category_subtype
    let subtypes = data[subtype_key] || []
    let types = data[type_key] || []
    let groups = data[group_key] || []

    const subtype_collection = collections_dict[subtype_key]
    let type_field = subtype_collection.fields.find(field =>
      field.related_snake_name === fg.category_type)
    if (type_field)
      type_field.is_multiple = type_field.relation_type === 'many_to_many'

    let root = {
      new_id: "root",
      parent: null,
      name: "root",
    }
    root = {...root, ...fg}
    let new_types = []
    let types_dict = {}
    const first_group = groups[0]
    if (type_key){
      const some_is_empty = subtypes.some(st => {
        const type_value = st[type_field.name]
        if (Array.isArray(type_value))
          return !type_value.length
        return !type_value
      })
      if (some_is_empty){
        let new_type ={
          id: 0,
          new_id: "type_0",
          name: 'Desconocido ⚠️',
          original_types: null,
          color: "red",
          icon: "error_outline",
          is_mix: true,
        }
        if (group_key)
          new_type[group_key] = first_group.id
        new_types.push(new_type)
      }
    }

    subtypes = subtypes.map(st => {
      if (type_field && type_field.is_multiple){
        let all_types = st[type_field.name]
        all_types.forEach(t => {
          if (!types_dict[t])
            types_dict[t] = []
          types_dict[t].push(st)
        })
        if (all_types.length === 1)
          st.parent_id = `type_${all_types[0]}`
        else if (!all_types.length){
          st.parent_id = "type_0"
          // console.log("No first type", st)
        }
        else{
          let new_type_key = ''
          const join_id = all_types.join('_')
          const names = all_types.map(t =>
            types.find(tt => tt.id === t).name)
          if (group_key){
            const first_type = types.find(t => t.id === all_types[0])
            new_type_key = first_type[group_key]
          }
          st.parent_id = `type_${join_id}`
          if (!new_types.find(t => t.id === join_id)){
            let new_type = {
              id: join_id,
              name: `Mixto: ${names.join(', ')}`,
              original_types: all_types.map(t =>
                types.find(tt => tt.id === t)),
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
      else if (type_key)
        st.parent_id = `type_${st[type_field.name]}`
      else
        st.parent_id = "root"
      st.new_id = `subtype_${st.id}`
      return st
    })
    types = [...types, ...new_types]
    types = types.map(type => {
      if (group_key && !type[group_key]) {
        console.log("No group key", type)
      }
      type.parent_id = group_key ? `group_${type[group_key]}` : "root"
      type.new_id = `type_${type.id}`
      if (type_field.is_multiple)
        type.all_childs = types_dict[type.id]
      return type
    })
    groups = groups.map(g => {
      g.parent_id = "root"
      g.new_id = `group_${g.id}`
      return g
    })
    const all_data = [...subtypes, ...types, ...groups, root]

    try{
      return d3.stratify()
        .id(d => d.new_id)
        .parentId(d => d.parent_id)
        (all_data)
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
      return null
    }
}

const calculateNewCats = (data, schemas) => {
  let all_nodes = {}
  schemas.filter_groups.forEach(fg => {
    const hydrated_filter_group = hydrateFilterGroup(
      fg, data, schemas.collections_dict)
    if (hydrated_filter_group)
      all_nodes[fg.key_name] = hydrated_filter_group
  })
  return all_nodes
}

function getLastId(data) {
  if (data.elems_ids){
    return { method: 'patch', last_id: `${data.elems_ids[0]}/massive_patch/` }
  }
    // return { method: 'post', last_id: 'massive_edit/' }
  const id = data.id || data.key_name
  // const id = data.id
  const is_edit = data.id && !data.is_new
  const method = is_edit ? 'put' : 'post'
  const last_id = is_edit ? `${id}/` : ''
  return { method, last_id }
}

export const useMainStore = defineStore('main', {
  state: () => ({
    cats: null,
    // extractivism_types: {},
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
    geometry_types: [
      {
        "type": "Polygon",
        "collection": "polygons",
        "source": "proyectos-poligonos",
        "main_layer": "proyectos-poligonos-fill"
      },
      {
        "type": "LineString",
        "collection": "lines",
        "source": "proyectos-lineas",
        "main_layer": "proyectos-lineas"
      },
      {
        "type": "MultiLineString",
        "collection": "multiLineStrings",
        "source": "proyectos-multilineas",
        "main_layer": "proyectos-multilineas"
      },
      {
        "type": "Point",
        "collection": "points",
        "source": "proyectos",
        "main_layer": "unclustered-point"
      },
    ],
    activities: [],
    spend_groups: [],
  }),
  actions: {
    // setHeader() {
    //   const cookie_auth = useCookie('auth_ocsa')
    //   if (cookie_auth.value) {
    //     $api.defaults.headers.common['Authorization'] = `Token ${cookie_auth.value}`
    //   }
    // },
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
      const { $api } = useNuxtApp()
      return new Promise((resolve) => {
        $api.get('/catalogs/all/')
          .then(({data}) => {
            // console.log("fetchCatalogs data", data)
            // this.extractivism_types = data.extractivism_type
            this.cats = data
            this.schemas = calculateSchemas(data)
            // console.log("schemas", this.schemas)
            this.all_nodes = calculateNewCats(data, this.schemas)
            this.status = calculate_status(data.status_control)
            this.setCollectionData()
            this.setFilterGroupData()
            this.cats_ready = true
            resolve(data)
          })
          .catch(error => {
            console.error(error)
          })
      })
    },
    async getSimple([group, id]) {
      // this.setHeader()
      const { $api } = useNuxtApp()
      try {
        let response = await $api.get(`/${group}/${id}/`);
        return response.data
      } catch (error) {
        console.error(error)
        ;
      }
    },
    async getGeo([group, id]) {
      const { $api } = useNuxtApp()
      if (this.full_geo[group][id])
        return
      this.full_geo[group][id] = []
      // this.setHeader()
      try {
        let response = await $api.get(`space_time/${group}/${id}/`);
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
      // this.setHeader()
      const { $api } = useNuxtApp()
      const { method, last_id } = getLastId(data)
      try {
        let response = await $api[method](
          `/${collection}/${last_id}`, data,
          { timeout: 300000 }
        );
        return response.data
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    async saveCatalog([collection_data, data]) {
      // this.setHeader()
      const { $api } = useNuxtApp()
      const { method, last_id } = getLastId(data)
      const collection = collection_data.snake_name
      const full_url = `catalogs/${collection}/${last_id}`
      try {
        let response = await $api[method](full_url, data);
        if (method === 'post')
          this.cats[collection].unshift(response.data)
        else {
          const elem_id = response.data.id ? 'id' : 'key_name'
          const index = this.cats[collection].findIndex(
            el => el[elem_id] === response.data[elem_id])
          this.cats[collection][index] = response.data
        }
        this.all_nodes = calculateNewCats(this.cats, this.schemas)
        return response.data
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    async patchSimple([collection, id, data]) {
      // this.setHeader()
      const { $api } = useNuxtApp()
      try {
        let response = await $api.patch(`/${collection}/${id}/`, data);
        return response.data
      } catch (error) {
        console.error(error);
      }
    },
    async patchCatalog([collection_data, id, data]) {
      // this.setHeader()
      const { $api } = useNuxtApp()
      const collection = collection_data.snake_name
      const full_url = `catalogs/${collection}/${id}/`
      try {
        let response = await $api.patch(`${full_url}`, data);
        const index = this.cats[collection].findIndex(
          el => el.id === response.data.id)
        Object.keys(data).forEach(key => {
          this.cats[collection][index][key] = response.data[key]
        })
        const filter_group = collection_data.filter_group
        if (filter_group){
          this.all_nodes[filter_group.key_name] = hydrateFilterGroup(
            filter_group, this.cats, this.schemas.collections_dict)
        }
        // this.cats[collection][index] = response.data
        return response.data
      } catch (error) {
        console.error(error);
      }
    },
    async deleteSimple([group, id]) {
      // this.setHeader()
      const { $api } = useNuxtApp()
      try {
        await $api.delete(`/${group}/${id}/`);
        return {success: true}
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    async deleteCatalog([collection_data, id]) {
      // this.setHeader()
      const { $api } = useNuxtApp()
      const collection = collection_data.snake_name
      const full_url = `catalogs/${collection}/${id}/`
      try {
        await $api.delete(full_url);
        this.cleanDelete(collection, id)
        // return id
        return {success: true}
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    cleanDelete(collection, id) {
      const index = this.cats[collection].findIndex(
        el => el.id === id)
      this.cats[collection].splice(index, 1)
      this.all_nodes = calculateNewCats(this.cats, this.schemas)
    },
    async mergeSimple([params, category_name]) {
      // this.setHeader()
      const { $api } = useNuxtApp()
      try {
        let response = await $api.post(`generic_merge/`, params);
        if (category_name)
          this.cleanDelete(category_name, params.merge_id)
        return response.data
      } catch (error) {
        console.error(error);
        return {error_data: error.response.data}
      }
    },
    async fetchElements([group, params]) {
      const { $api } = useNuxtApp()
      return new Promise(resolve => {
        // this.setHeader()
        $api.get(`/${group}/`, {
          cancelToken: request.token, params: params })
          .then(({ data }) => {
            return resolve(data)
          })
          .catch(thrown => {
            if (axios.isCancel(thrown)) {
              request = null
              request = axios.CancelToken.source()
              return resolve({ cancelled: true })
            } else {
              console.error(thrown)
              return resolve({ errors: thrown.response.data })
            }
          })
      })
    },
    cancelFetch() {
      if (request)
        request.cancel("Operation canceled by the user.")
    },
    // async fetchElements([group, params]) {
    //   try {
    //     const result = await $api.get(`/${group}/`,
    //       {params: params, cancelToken: request.token})
    //     return result.data
    //   } catch ((thrown) => {
    //     if (axios.isCancel(thrown))
    //       console.log('Request canceled', thrown.message)
    //     else
    //       console.error(thrown)
    //   })
    // },
    async exportData([group, params]) {
      const { $api } = useNuxtApp()
      return new Promise((resolve, reject) => {
        // this.setHeader()
        $api.get(`/${group}/export_xls/`, {
          params: params,
          responseType: 'blob',
          cancelToken: request.token
        })
          .then(response => {
            const blob = new Blob([response.data],
              {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})
            const url = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.setAttribute('download', `export_${group}.xlsx`)
            document.body.appendChild(link)
            link.click()
            resolve({success: true})
          })
          .catch(thrown => {
            if (axios.isCancel(thrown)) {
              request = null
              request = axios.CancelToken.source()
              return resolve({cancelled: true})
            } else {
              console.error(thrown)
              reject(thrown)
            }
          })
      })
    },
    async saveFile([elem_id, file_data, coll_name]) {
      const { $api } = useNuxtApp()
      try {
        // console.log('elem_id', elem_id)
        let response = await $api.post(
          `/${coll_name}/${elem_id}/add_file/`, file_data,
          {headers: {'Content-Type': 'multipart/form-data'
          }});
        return response.data
      } catch (error) {
        console.error(error);
      }
    },
    async getRelatedActors(proj_id, group_id) {
      const { $api } = useNuxtApp()
      const params = group_id ? {participant_group: group_id} : {}
      try {
        let response = await $api.get(`/project/${proj_id}/related_actors/`,
          {params});
        return response.data
      } catch (error) {
        console.error(error)
        ;
      }
    },
    async saveCollection(data) {
      const { $api } = useNuxtApp()
      // this.setHeader()
      try {
        let response = await $api.put(`collection/${data.snake_name}/`, data);
        return response.data
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    async deleteOtherParents([collection, id]) {
      const { $api } = useNuxtApp()
      // this.setHeader()
      try {
        let response = await $api.delete(`/${collection}/${id}/delete_other_parents/`);
        return response.data
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    async saveSelected([id, data]) {
      const { $api } = useNuxtApp()
      // this.setHeader()
      try {
        let response = await $api.patch(`article/${id}/select/`, data);
        return response.data
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    async getProjectLocations(subgroup_name) {
      const { $api } = useNuxtApp()
      // this.setHeader()
      try {
        let response = await $api.get(`/project_location/?loc_type=${subgroup_name}`);
        return response.data
      } catch (error) {
        console.error(error)
        ;
      }
    },
    async sendReprocessScrapedRecord(scraped_id) {
      const { $api } = useNuxtApp()
      try {
        let response = await $api.post(
          `/scraped_record/${scraped_id}/reprocess/`);
        return response.data
      } catch (error) {
        console.error(error)
        ;
      }
    },
    async fetchActivities(params) {
      const { $api } = useNuxtApp()
      try {
        let response = await $api.get(`/activity/`, {params: params});
        this.activities = response.data.activities
        this.spend_groups = response.data.spend_groups
        return response.data
      } catch (error) {
        console.error(error)
        ;
      }
    },
    async saveOffline(params) {
      const { $api } = useNuxtApp()
      const method = params.id ? 'put' : 'post'
      const id = params.id ? `${params.id}/` : ''
      try {
        let response = await $api[method](`/offline_task/${id}`, params);
        return response.data
      } catch (error) {
        console.error(error)
        ;
      }
    }

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
      return status_dict
    },
    megaproject_types_dict(state) {
      if (!state.cats)
        return {}
      let extractivism_dict = {}
      state.cats.extractivism_type.forEach(et => {
        extractivism_dict[et.id] = {
          id: et.id,
          name: et.name,
          short_name: et.short_name || et.name,
          icon: et.icon,
          color: et.color || '#5d5d5d',
        }
      })
      let other_type = state.cats.extractivism_type.find(et =>
        et.name.toLowerCase() === 'otro')
      other_type = other_type ? {
        id: other_type.id,
        name: other_type.name,
        short_name: other_type.short_name || other_type.name,
        icon: other_type.icon,
        color: other_type.color || '#753E08',
        extractivism_types: [],
      } : {
        id: 'other',
        name: 'Otro',
        short_name: 'Otro',
        icon: 'help',
        color: '#ff0000',
        extractivism_types: [],
      }

      let mp_types_dict = {}
      // console.log("extractivism_dict", extractivism_dict)
      // console.log("megaproject_type", state.cats.megaproject_type)
      state.cats.megaproject_type.forEach(mp_t => {
        const first_extractivism = mp_t.extractivism_types[0]
        mp_types_dict[mp_t.id] = mp_t
        if (!first_extractivism)
          mp_types_dict[mp_t.id]["first_extractivism_type"] = other_type
        else{
          mp_types_dict[mp_t.id]["first_extractivism_type"] = extractivism_dict[first_extractivism]
        }
      })
      // console.log("mp_types_dict", mp_types_dict)
      return mp_types_dict
    },
    collections_summary(state) {
      return state.schemas.collections.reduce((obj, coll) => {
        obj[coll.snake_name] = {
          'value': coll.snake_name,
          'title': coll.name,
          'name': coll.name,
          'plural_name': coll.plural_name,
          'icon': coll.icon,
          'color': coll.color,
        }
        return obj
      })
    },
    event_group_violence(state) {
      if (!state.cats)
        return {}
      return state.cats.event_group.find(eg => eg.name === 'Violencia')
    },
    event_group_legal(state) {
      if (!state.cats)
        return {}
      return state.cats.event_group.find(eg => eg.name === 'Mecanismos legales')
    },
    displacement_event_types(state) {
      if (!state.cats)
        return []
      const has_dis = state.cats.event_type.filter(et => et.has_displacement)
      return has_dis.map(et => et.id)
    },
    displacement_impact_types(state) {
      if (!state.cats)
        return []
      const has_dis = state.cats.impact_type.filter(et => et.has_displacement)
      return has_dis.map(et => et.id)
    },
    internal_displacement(state) {
      if (!state.cats)
        return {}
      return state.cats.dimension.find(d => d.name.includes('nterno'))
    },
    other_discarded_reason(state) {
      if (!state.cats)
        return null
      return state.cats.discarded_reason.find(dr => dr.is_other)
    },
    event_group_show_position(state) {
      if (!state.cats)
        return []
      let event_groups = state.cats.event_group.filter(eg => eg.show_position)
      return event_groups.map(eg => eg.id)
    },
    all_users(state) {
      if (!state.cats)
        return []
      return state.cats.user
    },
    full_editors(state) {
      if (!state.cats)
        return []
      return state.cats.user.filter(user => user.full_editor || user.is_superuser)
    },
    ai_extractivism_types(state) {
      if (!state.cats)
        return {}
      let ai_types = {}
      state.cats.extractivism_type.forEach(et => {
        if (!et.ai_name)
          return
        const { id, name, icon, color, ai_name } = et;
        ai_types[ai_name] = { id, name, icon, color };
      })
      return ai_types
    },
    criteria(state) {
      if (!state.cats)
        return {}
      // opponents: list[int] = []
      // social_impacts: list[int] = []
      // ecological_impacts: list[int] = []
      // acts_of_violence: list[int] = []
      // collective_actions: list[int] = []
      // is_foreign: bool | None = None
      const values = {
        opponents: state.cats.participant_group[0],
        social_impacts: state.cats.impact_group.find(ig => ig.is_social),
        ecological_impacts: state.cats.impact_group.find(ig => !ig.is_social),
        acts_of_violence: state.cats.event_group.find(
          eg => eg.model_origin === 'HechosViolencia'),
        collective_actions: state.cats.event_group.find(
          eg => eg.model_origin === 'FormaAC'),
      }
      const fields = ["id", "name", "icon", "color"]
      return Object.entries(values).reduce((obj, [key, value]) => {
        // console.log("criteria key", key, value)
        // const { id, name, icon, color } = value
        // obj[key] = { id, name, icon, color }
        let new_value = {}
        fields.forEach(field => {
          if (value[field] !== undefined)
            new_value[field] = value[field]
        })
        obj[key] = new_value
        return obj
      }, {})
    },
    valid_options(){
      return [
        {
          "id": 1,
          "name": "No cumple",
          "order": 1,
          "icon": "close",
          "color": "red-lighten-3",
          "value": false,
        },
        {
          "id": 2,
          "name": "Sí cumple",
          "order": 2,
          "icon": "verified",
          "color": "success",
          "value": true,
        },
      ]
    },
  },
})