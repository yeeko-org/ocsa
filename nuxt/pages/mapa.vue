
<script setup>

import mapboxgl from 'mapbox-gl';
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
import { ref, onMounted, onUnmounted } from 'vue';
import {storeToRefs} from "pinia";
import ProjectCardMap from "~/components/map/ProjectCardMap.vue";
import {getElement} from "~/composables/save_elements.js";
const { getProjectLocations, fetchCatalogs } = mainStore
const { schemas, extractivism_types_dict, cats } = storeToRefs(mainStore)

definePageMeta({
  layout: 'default',
})

const mapContainer = ref(null);
let map = ref(null);
const selectedProject = ref(null);
const selectedFullProject = ref(null);
const projectLocations = ref([]);

onMounted(async () => {
  getProjectLocations().then((res) => {
    fetchCatalogs().then(() => {
      hydrateProjectLocations(res);
    });
  });
});

onUnmounted(() => {
  if (map.value) {
    map.value.remove();
    map.value = null;
  }
});

const extractivism_types_list = computed(() => {
  if (!cats.value) return [];
  return cats.value.extractivism_type || [];
});

const project_collection = computed(() => {
  return schemas.value.collections_dict['project']
})

function hydrateProjectLocations(project_locations) {
  const random_color = "#e548be"
  project_locations.features.forEach(feature => {
    const props = feature.properties;
    if (props.project.megaproject_type) {
      const mp_t = props.project.megaproject_type
      props.color = extractivism_types_dict.value[mp_t]?.color || '#808080';
      props.extractivism_type = extractivism_types_dict.value[mp_t]?.id || null;
    } else {
      props.color = '#03fcd7'; // Gris por defecto si no hay tipo
      props.extractivism_type = null;
    }
  });
  projectLocations.value = project_locations;
  buildMap();
}

function buildMap() {
  const project_locations = projectLocations.value;

  if (!mapContainer.value) return;
  mapboxgl.accessToken = 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';

  map.value = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/rickrebel/cm6ls9un800kr01qqdu1g48nq',
    center: [-102.552784, 23.634501], // Centro de México
    zoom: 4.5
  });

  map.value.on('load', () => {
    // Separate points, lines, multilinestrings, and polygons from the data
    const geometry_types = [
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
    ]
    let data = {}
    const selected_et = selectedExtractivismTypes.value;
    const select_all = selected_et.length === 0;
    geometry_types.forEach(dt => {
      data[dt.collection] = {
        type: 'FeatureCollection',
        features: project_locations.features.filter(f => {
          const et = f.properties.extractivism_type;
          return (select_all || selected_et.includes(et)) &&
            f.geometry.type === dt.type
        })
      }
    });

    geometry_types.forEach(dt => {
      map.value.addSource(dt.source, {
        type: 'geojson',
        data: data[dt.collection],
        ...(dt.type === "Point" ? {
          cluster: true,
          clusterMaxZoom: 2,
          clusterRadius: 20
        } : {})
      });
    });

    map.value.addLayer({
      id: 'proyectos-poligonos-fill',
      type: 'fill',
      source: 'proyectos-poligonos',
      paint: {
        'fill-color': ['get', 'color'],
        'fill-opacity': 0.25,
      }
    });

    map.value.addLayer({
      id: 'unclustered-point',
      type: 'circle',
      source: 'proyectos',
      filter: ['!', ['has', 'point_count']],
      paint: {
        'circle-color': ['get', 'color'],
        'circle-radius': 6,
        'circle-stroke-width': 1,
        'circle-stroke-color': '#ffffff'
      }
    });

    const addLineLayer = (id, source, line_width=2.5) => {
      map.value.addLayer({
        id: id,
        type: 'line',
        source: source,
        paint: {
          'line-color': ['get', 'color'],
          'line-width': line_width
        }
      });
    };

    addLineLayer('proyectos-lineas', 'proyectos-lineas');
    addLineLayer('proyectos-multilineas', 'proyectos-multilineas');

    addLineLayer(
      'proyectos-poligonos-outline', 'proyectos-poligonos', 0.2);

    function buildFullProjectData(properties) {
      const projectData = typeof properties.project === 'string'
          ? JSON.parse(properties.project)
          : properties.project;
      console.log('Building full project data for:', projectData);
      selectedProject.value = { ...properties, project: projectData };
      selectedFullProject.value = null;
      getElement(project_collection.value, projectData.id).then(response => {
        selectedFullProject.value = response;
      })

    }

    geometry_types.forEach(gt => {
      map.value.on('click', gt.main_layer, (e) => {
        console.log('Feature clicked:', e.features[0]);
        buildFullProjectData(e.features[0].properties);
      });
      map.value.on('mouseenter', gt.main_layer, () => {
        map.value.getCanvas().style.cursor = 'pointer';
      });
      map.value.on('mouseleave', gt.main_layer, () => {
        map.value.getCanvas().style.cursor = '';
      });
    });

  //   map.value.loadImage(
  //           '/wind_power.svg',
  //           (error, image) => {
  //               if (error) throw error;
  //
  //               // Add the image to the map style.
  //               map.value.addImage('wind_power', image);
  //
  //               // Add a layer to use the image to represent the data.
  //               map.value.addLayer({
  //                   'id': 'points',
  //                   'type': 'symbol',
  //                   'source': 'proyectos',
  //                   'layout': {
  //                       'icon-image': 'wind_power', // reference the image
  //                       'icon-size': 0.25
  //                   }
  //               });
  //           }
  //       );
  });
}

const selectedExtractivismTypes = ref([]);


</script>

<template>
  <v-sheet
    color="#FFFFFF86"
    class="sheet-filters px-3"
  >
    <div v-if="false" class="text-h6 pt-2">
      Filtros
    </div>

    <v-chip-group
      v-model="selectedExtractivismTypes"
      column
      multiple
      @update:modelValue="buildMap()"
    >
      <div class="text-subtitle-1 pt-1 pr-3 font-weight-medium">
        Tipos de extractivismo:
      </div>
      <v-chip
        v-for="e_type in extractivism_types_list"
        :key="e_type.id"
        :value="e_type.id"
        :color="e_type.color"
        :base-color="`${e_type.color}C9`"
        class="mt-0 mb-2 text-black"
        variant="flat"
        filter
      >
        {{ e_type.short_name || e_type.name }}
      </v-chip>

    </v-chip-group>
  </v-sheet>
  <ProjectCardMap
    v-if="selectedProject"
    :selectedProject="selectedProject"
    :full_main="selectedFullProject"
    @update:selectedProject="selectedProject = $event"
  />

  <div class="map-container" ref="mapContainer">

  </div>
</template>

<style>
@import 'mapbox-gl/dist/mapbox-gl.css';

.map-container {
  width: 100%;
  height: 100vh;
}

.sheet-filters {
  position: absolute !important;
  top: 4px;
  left: 10px;
  z-index: 1;
  margin-right: 40px;
}


</style>