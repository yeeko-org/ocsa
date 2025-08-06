
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
    console.log("Project locations fetched", res);
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
    // Aquí va toda la lógica de añadir fuentes y capas que describí arriba
    // 1. Añadir fuente con clustering
    map.value.addSource('proyectos', {
      type: 'geojson',
      data: data,
      cluster: true,
      clusterMaxZoom: 2,
      clusterRadius: 50
    });

    // 2. Añadir capas (clusters, counts, puntos, líneas)
    // Ejemplo para puntos no clusterizados:
    // map.value.addLayer({
    //     id: 'unclustered-point',
    //     type: 'symbol',
    //     source: 'proyectos',
    //     filter: ['!', ['has', 'point_count']],
    //     layout: {
    //       'icon-image': ['default-icon' ],
    //       'icon-size': 1.2,
    //       'icon-allow-overlap': true
    //     }
    // });
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
    })

    // Capa de ejemplo para líneas (no se clusterizan)
    map.value.addLayer({
      id: 'proyectos-lineas',
      type: 'line',
      source: 'proyectos',
      filter: ['all',
        ['==', '$type', 'LineString']
      ],
      paint: {
        'line-color': '#ee0d0d',
        'line-width': 2
      }
    })

    // 3. Añadir eventos de clic
    map.value.on('click', 'unclustered-point', (e) => {
      const properties = e.features[0].properties;
      // Deserializar si viene como string JSON desde PostGIS
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
    map.value.on('mouseenter', ['unclustered-point', 'proyectos-lineas'], () => {
      map.value.getCanvas().style.cursor = 'pointer';
    });
    map.value.on('mouseleave', ['unclustered-point', 'proyectos-lineas'], () => {
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