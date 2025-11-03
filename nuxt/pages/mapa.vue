
<script setup>

import mapboxgl from 'mapbox-gl';
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
import {ref, onMounted, onUnmounted, watch} from 'vue';
import {storeToRefs} from "pinia";
import ProjectCardMap from "~/components/map/ProjectCardMap.vue";
import {getElement} from "~/composables/save_elements.js";
const { getProjectLocations, fetchCatalogs } = mainStore
const { schemas, megaproject_types_dict, cats } = storeToRefs(mainStore)

definePageMeta({
  layout: 'default',
})

const mapContainer = ref(null);
let map = ref(null);
const selectedProject = ref(null);
const selectedFullProject = ref(null);
const projectLocations = ref([]);
const ready_gets = ref(0);
const selectedExtractivismTypes = ref([]);

onMounted(async () => {
  getProjectLocations().then((res) => {
    projectLocations.value = res;
    ready_gets.value += 1;
  });
  fetchCatalogs().then(() => {
    ready_gets.value += 1;
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

function hydrateProjectLocations() {
  const random_color = "#e548be"
  console.log("megaproject_types_dict", megaproject_types_dict.value);
  Object.entries(megaproject_types_dict.value).forEach(([key, value]) => {
    if (key === 6 || key === '6')
      console.log(`Extractivism type: ${key}`, value);
    // console.log(`Megaproject type: ${value.megaproject_type.id}`, value.megaproject_type);
  });
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
      props.extractivism_types = megaproject_type_obj.extractivism_types || [];
    } else {
      props.color = '#03fcd7'; // Gris por defecto si no hay tipo
      props.extractivism_type = null;
      props.extractivism_types = [];
    }
  });
  buildMap();
}


watch(ready_gets, (newVal) => {
  if (newVal === 2) {
    hydrateProjectLocations();
  }
});

function buildMap() {
  const project_locations = projectLocations.value;
  if (!mapContainer.value) return;
  // mapboxgl.accessToken= 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';
  mapboxgl.accessToken = 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';

  map.value = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/rickrebel/cm6ls9un800kr01qqdu1g48nq',
    center: [-102.552784, 23.634501], // Centro de México
    zoom: 4.5
  });

  map.value.addControl(new mapboxgl.NavigationControl());

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
        "main_layer": "unclustered-point-circle"
      },
    ]
    let data = {}
    const selected_et = selectedExtractivismTypes.value;
    const select_all = selected_et.length === 0;
    // let ready_prints = 0
    console.log("selected_et", selected_et);
    const features_filtered = project_locations.features.filter(f => {
      if (select_all) return true;
      const extractivism_types = f.properties.extractivism_types;
      const some_filtered = selected_et.some(set =>
        (extractivism_types.includes(set))
      );
      // if (some_filtered && ready_prints < 10) {
      //   console.log("extractivism_types", extractivism_types);
      //   console.log("Feature:", f);
      //   ready_prints += 1;
      // }
      return some_filtered;
    });

    geometry_types.forEach(dt => {
      data[dt.collection] = {
        type: 'FeatureCollection',
        features: features_filtered.filter(f =>
          f.geometry.type === dt.type)
      }
    });
    let cluster_properties = {};
    cats.value.extractivism_type.forEach(et => {
      cluster_properties[`sum_extractivism_type_${et.id}`] = [
        '+',
        [
          'case',
          ['in', et.id, ['get', 'extractivism_types']],
          1,
          0
        ]
      ];
    });

    geometry_types.forEach(dt => {
      map.value.addSource(dt.source, {
        type: 'geojson',
        data: data[dt.collection],
        ...(dt.type === "Point" ? {
          cluster: true,
          clusterMaxZoom: 10,
          clusterRadius: 24,
          clusterProperties: cluster_properties
        } : {})
      });
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
    addLineLayer(
      'proyectos-poligonos-outline', 'proyectos-poligonos', 0.2);
    addLineLayer('proyectos-lineas', 'proyectos-lineas');
    addLineLayer('proyectos-multilineas', 'proyectos-multilineas');


    map.value.addLayer({
      id: 'proyectos-poligonos-fill',
      type: 'fill',
      source: 'proyectos-poligonos',
      filter: ['!', ['has', 'point_count']],
      paint: {
        'fill-color': ['get', 'color'],
        'fill-opacity': 0.25,
      }
    });


    map.value.addLayer({
        id: 'clusters',
        type: 'circle',
        source: 'proyectos',
        filter: ['has', 'point_count'],
        // filter: ['=', 'cluster', true],
        paint: {
            'circle-opacity': 0.6,
            'circle-color': [
                'step',
                ['get', 'point_count'],
                '#51bbd6',
                20, '#f1f075',
                60, '#f28cb1'
            ],
            'circle-radius': [
                'step',
                ['get', 'point_count'],
                15,
                20, 22,
                60, 29
            ],
            'circle-emissive-strength': 1
        }
    });

    map.value.addLayer({
        id: 'cluster-count',
        type: 'symbol',
        source: 'proyectos',
        filter: ['has', 'point_count'],
        layout: {
            'text-field': ['get', 'point_count_abbreviated'],
            // 'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
            'text-size': 12
        }
    });

    map.value.addLayer({
      id: 'unclustered-point-circle',
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


    map.value.addLayer({
      id: 'unclustered-point',
      type: 'symbol',
      source: 'proyectos',
      filter: ['!', ['has', 'point_count']],
      layout: {
        'icon-image': [
            'image',
            ['get', 'icon_pin'],
            { params: { icon_color: ['get', 'color'] } }
        ],
        // 'icon-size': 0.6,
        'icon-size': [
          "interpolate",
          ["linear"],
          ["zoom"],
          5, 0.7,
          11, 1,
          15, 1.4
        ]
      },
    });



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

    // map.value.loadImage(
    //   '/wind_power.svg',
    //   (error, image) => {
    //     if (error) throw error;
    //
    //     // Add the image to the map style.
    //     map.value.addImage('wind_power', image);
    //
    //     // Add a layer to use the image to represent the data.
    //     map.value.addLayer({
    //       'id': 'points',
    //       'type': 'symbol',
    //       'source': 'proyectos',
    //       'layout': {
    //         'icon-image': 'wind_power', // reference the image
    //         'icon-size': 0.25
    //       }
    //     });
    //   }
    // );
  });
}

function buildFullProjectData(properties) {
  const projectData = typeof properties.project === 'string'
      ? JSON.parse(properties.project)
      : properties.project;
  console.log('Building full project data for:', projectData);
  selectedProject.value = { ...properties, project: projectData };
  console.log("selectedProject", selectedProject.value);
  selectedFullProject.value = null;
  getElement(project_collection.value, projectData.id).then(response => {
    selectedFullProject.value = response;
  })

}


</script>

<template>
  <v-sheet
    color="#FFFFFF60"
    class="sheet-filters px-3 pt-2"
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
        class="mt-0 mb-2"
        variant="flat"
        filter
      >
        {{ e_type.short_name || e_type.name }}
        <template v-slot:prepend>
          <v-icon color="white" class="mr-1">{{ e_type.icon }}</v-icon>
        </template>
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
  top: 0;
  left: 0;
  z-index: 1;
  margin-right: 40px;
}


</style>