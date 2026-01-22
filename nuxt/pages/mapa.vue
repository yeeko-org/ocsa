<script setup>
import mapboxgl from 'mapbox-gl';
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {onMounted, onUnmounted, ref, watch} from 'vue';
import ProjectCardMap from "~/components/map/ProjectCardMap.vue";
import MainFilterMap from "~/components/map/MainFilterMap.vue";
import { useMapData } from "~/components/map/useMapData.js";
import { useMapLayers } from "~/components/map/useMapLayers.js";
import { setupInteractions } from "~/components/map/useMapInteractions.js";
import { useMapClusters } from "~/components/map/useMapClusters.js";

const mainStore = useMainStore()
const { getSimple } = mainStore
const { target_project_id } = storeToRefs(mainStore)

definePageMeta({
  layout: 'default',
})

const mapContainer = ref(null);
let map = ref(null);
const selectedParentProject = ref(null);
const selectedChildProject = ref(null);
const childProject = ref(null);
const parentProject = ref(null);

const {
  projectLocations,
  ready_gets,
  selectedExtractivismTypes,
  extractivism_type_props,
  hydrateProjectLocations,
  loadData
} = useMapData();

const {
  initializeMapLayers,
  updateMapData: updateLayersData
} = useMapLayers(map);

const { setupClusterMarkers } = useMapClusters(map);

// onMounted(async () => {
onMounted(() => {
  buildPreMap();
  // console.log("Mounted mapa.vue");
  loadData();
});

onUnmounted(() => {
  if (map.value) {
    map.value.remove();
    map.value = null;
  }
});

watch(ready_gets, (newVal) => {
  if (newVal === 2) {
    hydrateProjectLocations();
    initBuildMap();
  }
});

watch(target_project_id, (newId) => {
  if (!newId || !map.value) return;

  // 1. Filtrar todas las geometrías asociadas a ese ID
  const features = projectLocations.value.features.filter(f =>
    f.properties.project.id === newId
  );

  if (features.length === 0) return;

  // 2. Calcular Bounding Box para hacer zoom
  const bounds = new mapboxgl.LngLatBounds();

  features.forEach(feature => {
    const geometry = feature.geometry;
    if (geometry.type === 'Point') {
      bounds.extend(geometry.coordinates);
    } else if (geometry.type === 'Polygon') {
      geometry.coordinates.forEach(ring => {
        ring.forEach(coord => bounds.extend(coord));
      });
    } else if (geometry.type === 'MultiPolygon') {
      geometry.coordinates.forEach(polygon => {
        polygon.forEach(ring => {
          ring.forEach(coord => bounds.extend(coord));
        });
      });
    } else if (geometry.type === 'LineString') {
      geometry.coordinates.forEach(coord => bounds.extend(coord));
    } else if (geometry.type === 'MultiLineString') {
      geometry.coordinates.forEach(line => {
        line.forEach(coord => bounds.extend(coord));
      });
    }
  });

  // 3. Mover el mapa
  if (!bounds.isEmpty()) {
    map.value.fitBounds(bounds, {
      padding: { top: 100, bottom: 100, left: 100, right: 350 },
      maxZoom: 14,
      duration: 1500
    });
  }

  // 4. Abrir la tarjeta del proyecto
  // Usamos las propiedades del primer feature encontrado
  buildFullProjectData(features[0].properties);
});

function buildPreMap() {
  if (!mapContainer.value) return;
  // mapboxgl.accessToken= 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';
  mapboxgl.accessToken = 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';

  map.value = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/rickrebel/cm6ls9un800kr01qqdu1g48nq',
    center: [-102.552784, 23.634501], // Centro de México
    zoom: 4.5
  });
  map.value.addControl(new mapboxgl.NavigationControl(), 'bottom-right');
}

function updateMapData() {
  updateLayersData(
    projectLocations, selectedExtractivismTypes);
}

function initBuildMap() {
  if (map.value.loaded()) {
    console.log("Map already loaded, initializing directly.");
    buildMap();
  } else {
    map.value.on('load', () => {
      console.log("Map loaded.");
      buildMap();
    });
    map.value.on('error', (e) => {
      console.error("Map loading error:", e);
    });
  }
}

function buildMap(){
  initializeMapLayers();
  updateMapData();
  setupInteractions(map, buildFullProjectData);
  setupClusterMarkers(selectedExtractivismTypes, extractivism_type_props);
}

function buildFullProjectData(properties) {
  const projectData = typeof properties.project === 'string'
      ? JSON.parse(properties.project)
      : properties.project;
  // console.log('Building full project data for:', projectData);
  parentProject.value = null;
  childProject.value = null;
  selectedChildProject.value = null
  selectedParentProject.value = null;
  if (projectData.parent_project){
    // console.log('Project has parent, fetching parent project data.');
    selectedChildProject.value = { ...properties, project: projectData };
  }
  else{
    selectedParentProject.value = { ...properties, project: projectData };
  }
  getSimple(['project_map', projectData.id]).then(res => {
    // console.log('Fetched full project data:', res);
    if (res.parent_project_full){
      selectedParentProject.value = {
        color: '',
        project: res.parent_project_full
      };
      parentProject.value = res.parent_project_full;
      const new_project = separateCollections(res, selectedChildProject.value.project);
      childProject.value = {color: '', project: new_project};
    }
    else{
      parentProject.value = res;
    }
  })
}

function separateCollections(all_project_data, current_project) {
  // console.log('Separating collections for project:', current_project.id);
  // console.log('All project data:', all_project_data);
  const mentions = all_project_data.mentions.filter(mention => {
    return mention.project === current_project.id;
  });
  const mention_ids = mentions.map(mention => mention.id);
  const events = all_project_data.events.filter(event => {
    return mention_ids.includes(event.mention);
  });
  const impacts = all_project_data.impacts.filter(impact => {
    return mention_ids.includes(impact.mention);
  });
  return { ...current_project, mentions, events, impacts };

}

function openChildProject(project) {
  selectedChildProject.value = {color: '', project: project};
  const new_project = separateCollections(parentProject.value, project);
  childProject.value = {color: '', project: new_project};
}

</script>

<template>
  <MainFilterMap
    v-model:selectedExtractivismTypes="selectedExtractivismTypes"
    @update:selectedExtractivismTypes="updateMapData"
  />
  <ProjectCardMap
    v-if="selectedParentProject"
    :selectedProject="selectedParentProject"
    :childProject="childProject?.project"
    :full_main="parentProject"
    @update:selectedProject="selectedParentProject = $event"
    @open-child-project="openChildProject($event)"
  />
  <ProjectCardMap
    v-if="childProject"
    :selectedProject="selectedChildProject"
    :full_main="childProject?.project"
    is_child
    @update:selectedProject="childProject = $event"
  />

  <div class="map-container" ref="mapContainer">

  </div>

</template>

<style>
@import 'mapbox-gl/dist/mapbox-gl.css';
.mapboxgl-popup {
  width: 220px;
}

.map-container {
  width: 100%;
  height: 100vh;
}


</style>