import { defineStore } from 'pinia'

import axios from "axios";
let request = axios.CancelToken.source();

export const useGeoStore = defineStore('geo', {
  state: () => ({
    countries: [],
    states_full: {},
    states: [],
    municipalities_full: {},
    loading: false,
    error: null,
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
  }),
  actions: {
    setStates(states) {
      this.states = states
    },
    async getGeo([group, id]) {
      const { $api } = useNuxtApp()
      const geo_state = group === 'state' ? 'states_full' : 'municipalities_full'
      // if (this.full_geo[group][id])
      if (this[geo_state][id])
        return
      // this.full_geo[group][id] = []
      this[geo_state][id] = []
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
    async getState(id) {
      const { $api } = useNuxtApp()
      // if (this.full_geo[group][id])
      if (this.states_full[id])
        return
      this[states_full][id] = []
      // this.setHeader()
      try {
        let response = await $api.get(`space_time/state/${id}/`);
        this.full_geo.states_full[id] = response.data.municipalities
        return response.data
      } catch (error) {
        console.error(error)
        ;
      }
    },
  },
});