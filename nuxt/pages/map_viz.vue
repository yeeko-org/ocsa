
<script setup>

import mapboxgl from 'mapbox-gl';
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const { getProjectLocations } = mainStore
import { ref, onMounted, onUnmounted } from 'vue';
import {storeToRefs} from "pinia";

definePageMeta({
  layout: 'default',
})

// Tu componente de tarjeta (asumiendo que existe)
// import ProjectDetailCard from './ProjectDetailCard.vue';

const mapContainer = ref(null);
let map = ref(null);
const selectedProject = ref(null);

onMounted(async () => {
  getProjectLocations().then((res) => {
    // console.log("Project locations fetched", res);
    buildMap(res);
  });


});

function buildMap(data) {
  if (!mapContainer.value) return;
  mapboxgl.accessToken = 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';

  map.value = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/rickrebel/cm6ls9un800kr01qqdu1g48nq',
    center: [-102.552784, 23.634501], // Centro de México
    zoom: 4.5
  });

  map.value.on('load', () => {
    // Separate points and lines from the data
    const points = {
      type: 'FeatureCollection',
      features: data.features.filter(f => f.geometry.type === 'Point')
    };
    
    const lines = {
      type: 'FeatureCollection',
      features: data.features.filter(f => f.geometry.type === 'LineString')
    };

    // 1. Add source with clustering for points only
    map.value.addSource('proyectos', {
      type: 'geojson',
      data: points,
      cluster: true,
      clusterMaxZoom: 2, // Increased from 2 to 14 to prevent points from disappearing
      clusterRadius: 20
    });

    // 2. Add separate source for lines (no clustering)
    map.value.addSource('proyectos-lineas', {
      type: 'geojson',
      data: lines
    });

    // 3. Add layer for unclustered points
    map.value.addLayer({
      id: 'unclustered-point',
      type: 'circle',
      source: 'proyectos',
      filter: ['!', ['has', 'point_count']],
      paint: {
        'circle-color': '#007cbf',
        'circle-radius': 6,
        'circle-stroke-width': 1,
        'circle-stroke-color': '#ffffff'
      }
    });

    // 4. Add layer for lines
    map.value.addLayer({
      id: 'proyectos-lineas',
      type: 'line',
      source: 'proyectos-lineas',
      filter: ['all',
        ['==', '$type', 'LineString']
      ],
      paint: {
        'line-color': '#ee0d0d',
        'line-width': 2
      }
    });

    // 5. Add click events
    map.value.on('click', 'unclustered-point', (e) => {
      const properties = e.features[0].properties;
      const projectData = typeof properties === 'string'
          ? JSON.parse(properties)
          : properties;
      selectedProject.value = projectData;
    });

    map.value.on('click', 'proyectos-lineas', (e) => {
      const properties = e.features[0].properties;
      const projectData = typeof properties === 'string' ? JSON.parse(properties) : properties;
      selectedProject.value = projectData;
    });

    // Cambiar cursor a puntero
    map.value.on('mouseenter', 'unclustered-point', () => {
      map.value.getCanvas().style.cursor = 'pointer';
    });
    map.value.on('mouseleave', 'unclustered-point', () => {
      map.value.getCanvas().style.cursor = '';
    });
    map.value.on('mouseenter', 'proyectos-lineas', () => {
      map.value.getCanvas().style.cursor = 'pointer';
    });
    map.value.on('mouseleave', 'proyectos-lineas', () => {
      map.value.getCanvas().style.cursor = '';
    });
  });
}

onUnmounted(() => {
  if (map.value) {
    map.value.remove();
    map.value = null;
  }
});


</script>

<template>
  <div class="map-container" ref="mapContainer"></div>
<!--  <ProjectDetailCard -->
<!--    v-if="selectedProject" -->
<!--    :project="selectedProject"-->
<!--    @close="selectedProject = null"-->
<!--  />-->
</template>

<style>
@import 'mapbox-gl/dist/mapbox-gl.css';

.map-container {
  width: 100%;
  height: 100vh;
}
</style>