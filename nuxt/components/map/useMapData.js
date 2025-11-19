// components/map/useMapData.js
import { ref, watch, computed } from 'vue';
import { useMainStore } from "~/store/index.js";
import { storeToRefs } from "pinia";

export function useMapData() {
  const mainStore = useMainStore()
  const { getProjectLocations, fetchCatalogs } = mainStore
  const { megaproject_types_dict, cats } = storeToRefs(mainStore)

  const projectLocations = ref([]);
  const ready_gets = ref(0);
  const selectedExtractivismTypes = ref([]);

  function hydrateProjectLocations() {
    const random_color = "#755f4c"
    projectLocations.value.features.forEach(feature => {
      const props = feature.properties;
      if (props.project.megaproject_type) {
        const mp_t = props.project.megaproject_type
        const megaproject_type_obj = megaproject_types_dict.value[mp_t] || {}
        const extractivism_obj = megaproject_type_obj.first_extractivism_type;
        props.color = extractivism_obj?.color || '#808080';
        props.icon = extractivism_obj?.icon || 'harbor';
        props.icon_pin = `${props.icon}-pin`;
        props.extractivism_type = extractivism_obj?.id || null;
        const extr_types = megaproject_type_obj.extractivism_types || [];
        props.extractivism_types = extr_types || [];
        props.power = extr_types.length === 1 ? 2 : 1;
        // props.two_extractivism_types = extr_types || [];
        // if (extr_types.length === 1) {
        //   props.two_extractivism_types = [extr_types[0], extr_types[0]];
        // }
      } else {
        props.color = '#03fcd7'; // Gris por defecto si no hay tipo
        props.extractivism_type = null;
        props.extractivism_types = [];
      }
    });
  }

  function loadData() {
    // const locations = await getProjectLocations();
    // projectLocations.value = locations;
    // // projectLocations.value = await getProjectLocations();
    // ready_gets.value += 1;
    getProjectLocations().then(locations => {
      projectLocations.value = locations;
      // locations.features.forEach(loc => {
      //   if (loc.properties.id === 2513 || loc.properties.id === 12306) {
      //     console.log("\n\nProject location:", loc);
      //   }
      // });
      ready_gets.value += 1;
    });

    // fetchCatalogs();
    // ready_gets.value += 1;
    fetchCatalogs().then(() => {
      ready_gets.value += 1;
    });
  }

  const extractivism_type_props = computed(() => {
    const et_props = {"colors": [], "icons": [], "ids": []};
    cats.value.extractivism_type.forEach(et => {
      et_props.colors.push(et.color);
      et_props.icons.push(et.icon);
      et_props.ids.push(et.id);
    });
    return et_props;
  });

  return {
    projectLocations,
    ready_gets,
    selectedExtractivismTypes,
    megaproject_types_dict,
    extractivism_type_props,
    hydrateProjectLocations,
    loadData
  }
}
