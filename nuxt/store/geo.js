import { defineStore } from 'pinia'
import { geoService } from "~/services/geo.service.js";
import { ref } from 'vue';

export const useGeoNewStore = defineStore('geo_new', () => {
  const states = ref([]);
  const states_full = ref({});
  const municipalities_full = ref({});

  async function getMunicipalities(state_id) {
    if (!states_full.value[state_id]?.length){
      const response = await geoService.getMunicipalities(state_id);
      states_full.value[state_id] = response.data.municipalities
    }
    return states_full.value[state_id]
  }

  async function getLocalities(municipality_id) {
    if (!municipalities_full.value[municipality_id]?.length){
      const response = await geoService.getLocalities(municipality_id);
      municipalities_full.value[municipality_id] = response.data.localities
    }
    return municipalities_full.value[municipality_id]
  }

  return {
    states,
    states_full,
    municipalities_full,
    getMunicipalities,
    getLocalities
  }
});