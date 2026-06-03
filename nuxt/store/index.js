// import ApiService from "./common";
// import { mande } from 'mande'
import { defineStore } from 'pinia'
import axios from "axios";
let request = axios.CancelToken.source();
import { useGeoNewStore } from "~/store/geo.js";
import { calculateNewCats, hydrateFilterGroup } from "~/composables/nodes.js";
import { calculateSchemas } from "~/composables/cats.js";
import { calculate_status } from "~/composables/filters.js";

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
    status: {},
    impact_groups: {social: [], environmental: []},
    current_filter_group: null,
    current_filter_group_data: null,
    current_collection: null,
    current_collection_data: null,
    // groups: menu_content,
    full_geo: {"state": {}, "municipality": {}},
    activities: [],
    spend_groups: [],
    content_paragraphs: {},
    // Índice de facetas por proyecto para el filtrado del mapa en cliente
    // (Sesión 4.1, api-contract §1). { built_at, facets: { [projId]: {e,i,s,p} } }
    projectFacets: null,
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
            const geoNewStore = useGeoNewStore();
            // console.log("fetchCatalogs data", data)
            // this.extractivism_types = data.extractivism_type
            this.cats = data
            geoNewStore.$patch({ states: data.state })
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
      const { $api } = useNuxtApp()
      try {
        let response = await $api.get(`/${group}/${id}/`);
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
      const { $api } = useNuxtApp()
      try {
        let response = await $api.patch(`/${collection}/${id}/`, data);
        return response.data
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    async patchCatalog([collection_data, id, data]) {
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
      const { $api } = useNuxtApp()
      try {
        await $api.delete(`/${group}/${id}/`)
        return {success: true}
      } catch (error) {
        const data = error.response?.data
        if (error.response?.status === 400 && data?.report_data)
          return {report_data: data.report_data}
        console.error(error)
        return {errors: data}
      }
    },
    async confirmDeleteSimple([group, id]) {
      const { $api } = useNuxtApp()
      try {
        await $api.delete(`/${group}/${id}/confirm-delete/`)
        return {success: true}
      } catch (error) {
        console.error(error)
        return {errors: error.response?.data}
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
          }}
        );
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
    async sendPreCapture(note_id) {
      const { $api } = useNuxtApp()
      try {
        let response = await $api.post(`note/${note_id}/start_pre_capture/`);
        return response.data
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    async savePreCapture({data, note_id}) {
      const { $api } = useNuxtApp()
      try {
        let response = await $api.post(`note/${note_id}/edit_pre_capture/`, data);
        return response.data
      } catch (error) {
        console.error(error);
        return {errors: error.response.data}
      }
    },
    async getPreCapture({note_id, path}) {
      const { $api } = useNuxtApp()
      try {
        let response = await $api.post(`note/${note_id}/pre_capture_by_path/`,
          {path}
        )
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
    // Índice directo de facetas por proyecto (evento/afectación/subtipo/
    // participación). Se pide una sola vez por sesión: el front construye el
    // índice invertido en memoria a partir de esto (store/map.js).
    async fetchProjectFacets() {
      if (this.projectFacets) return this.projectFacets
      const { $api } = useNuxtApp()
      try {
        const { data } = await $api.get('/map/project_facets/')
        this.projectFacets = data
        return data
      } catch (error) {
        console.error(error)
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
    event_types_dict(state) {
      if (!state.all_nodes)
        return {}
      let event_types_dict = {}
      // console.log("leaves", state.all_nodes.event_types.leaves())
      state.all_nodes.event_types.leaves().forEach(et => {
        event_types_dict[et.data.id] = et.parent.data.id
      })
      return event_types_dict
    },
    collections_summary(state) {
      if (!state.schemas.collections_dict){
        return {}
      }
      return Object.values(state.schemas.collections_dict).reduce((obj, coll) => {
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
      return state.cats.event_group.find(eg => eg.name.toLowerCase().includes('violencia') )
    },
    // purpose
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
    event_group_show_purpose(state) {
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