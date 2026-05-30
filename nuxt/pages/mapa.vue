<script setup>
import mapboxgl from 'mapbox-gl';
import {storeToRefs} from "pinia";
import MainFilterMap from "~/components/map/MainFilterMap.vue";
import { useMapStore } from "~/store/map.js";
import { useMapLayers } from "~/components/map/useMapLayers.js";
import { setupInteractions } from "~/components/map/useMapInteractions.js";
import { useMapClusters } from "~/components/map/useMapClusters.js";
import ProjectsPanelMap from "~/components/map/ProjectsPanelMap.vue";
import MapTopControls from "~/components/map/MapTopControls.vue";
import MapLayerSwitch from "~/components/map/MapLayerSwitch.vue";

definePageMeta({
  layout: 'map',
})

const mapContainer = ref(null);
let map = ref(null);

const mapStore = useMapStore()
const { loadData, hydrateProjectLocations } = mapStore
const {
  projectLocations,
  readyGets,
  selectedExtractivismTypes,
  targetProjectId,
} = storeToRefs(mapStore)

const {
  initializeMapLayers,
  updateMapData
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

watch(readyGets, (newVal) => {
  if (newVal === 2) {
    hydrateProjectLocations();
    initBuildMap();
  }
});

watch(selectedExtractivismTypes, updateMapData);

watch(targetProjectId, (newId) => {
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
      // El detalle vive ahora en el panel abajo-izq: reservamos ese
      // costado (y el inferior para el pill) en vez de la derecha.
      padding: { top: 80, bottom: 120, left: 420, right: 80 },
      maxZoom: 14,
      duration: 1500
    });
  }
});

function buildPreMap() {
  if (!mapContainer.value) return;
  // mapboxgl.accessToken= 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';
  mapboxgl.accessToken = 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';

  map.value = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/rickrebel/cm6ls9un800kr01qqdu1g48nq',
    // center: [-102.552784, 23.634501], // Centro de México
    // zoom: 4.5,
    // Encuadre inicial por bounding box: Mapbox calcula el zoom según
    // el tamaño del contenedor, así México siempre abarca la pantalla.
    bounds: [[-118.4, 14.5], [-86.7, 32.7]], // [SW, NE] de México
    fitBoundsOptions: { padding: 20 },
    logoPosition: 'bottom-right',
  });
  map.value.addControl(new mapboxgl.NavigationControl(), 'bottom-right');
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
  setupInteractions(map);
  setupClusterMarkers();
}

</script>

<template>
  <MapTopControls/>

  <!-- Sesión 3: aquí se monta el rail de íconos de filtro (borde izq) -->
  <!-- Sesión 3: aquí se monta la franja de cápsulas de filtros activos -->

  <MainFilterMap/>
  <ProjectsPanelMap/>
  <MapLayerSwitch/>

  <div class="map-container" ref="mapContainer">

  </div>

</template>

<style>
@import 'mapbox-gl/dist/mapbox-gl.css';

html {
  overflow: hidden;
}

.map-container {
  width: 100%;
  /* Sin app-bar: el mapa ocupa todo el viewport (dvh = mejor en móvil). */
  height: 100dvh;
}


</style>