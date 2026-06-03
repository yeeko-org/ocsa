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
import MapFilterRail from "~/components/map/MapFilterRail.vue";
import MapFilterChips from "~/components/map/MapFilterChips.vue";
import { useMapFilterUrl } from "~/components/map/useMapFilterUrl.js";
import { useMapStyle, MAP_STYLE } from "~/components/map/useMapStyle.js";

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
  targetProjectId,
} = storeToRefs(mapStore)

const {
  initializeMapLayers,
  updateMapData
} = useMapLayers(map);

const { setupClusterMarkers } = useMapClusters(map);

// Alterna mapa ↔ satélite. setStyle borra las capas custom, así que las
// reconstruimos al cargar el nuevo estilo.
const { isSatelliteView, isSwitching, toggleMapStyle } = useMapStyle(map, {
  onStyleReload: rebuildAfterStyleChange
});

function rebuildAfterStyleChange() {
  initializeMapLayers();
  updateMapData();
}

// Filtros ↔ URL: hidrata desde los query params al cargar y los mantiene
// sincronizados (vistas compartibles, decisions §15).
useMapFilterUrl();

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

// Filtrado centralizado: `visibleProjectIds` es un computed que devuelve un Set
// nuevo ante cualquier cambio de filtros (y al poblarse el índice de facetas),
// así que un watch por identidad basta para re-pintar (sin deep).
watch(() => mapStore.visibleProjectIds, updateMapData);

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
      // El panel de proyectos vive abajo-derecha: reservamos ese costado
      // (y el inferior para el pill) para que el encuadre no quede tapado.
      padding: { top: 80, bottom: 120, left: 80, right: 420 },
      maxZoom: 12,
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
    style: MAP_STYLE,
    // center: [-102.552784, 23.634501], // Centro de México
    // zoom: 4.5,
    // Encuadre inicial por bounding box: Mapbox calcula el zoom según
    // el tamaño del contenedor, así México siempre abarca la pantalla.
    bounds: [[-118.4, 14.5], [-86.7, 32.7]], // [SW, NE] de México
    fitBoundsOptions: { padding: 20 },
    // Controles y leyendas de Mapbox abajo-izquierda (el panel de proyectos
    // ocupa la esquina inferior derecha). La atribución por defecto sale
    // abajo-derecha, así que la desactivamos y la re-añadimos a la izquierda.
    logoPosition: 'bottom-left',
    attributionControl: false,
  });
  map.value.addControl(new mapboxgl.AttributionControl(), 'bottom-left');
  map.value.addControl(new mapboxgl.NavigationControl(), 'bottom-left');
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
  // Carga diferida del índice de facetas: ya pintamos el mapa, no bloquea el
  // primer paint. Al llegar, visibleProjectIds cambia y el watch re-pinta.
  mapStore.ensureFacets();
}

</script>

<template>
  <MapTopControls/>

  <MapFilterRail/>
  <MapFilterChips/>

  <!-- Leyenda de extractivismo: sheet semitransparente flotante, siempre
       visible (decisions §5). En md+, a la derecha de la isla superior;
       en sm/xs, franja bajo la isla. -->
  <MainFilterMap/>
  <ProjectsPanelMap/>
  <MapLayerSwitch
    :is_satellite="isSatelliteView"
    :is_switching="isSwitching"
    @toggle="toggleMapStyle"/>

  <div class="map-container" ref="mapContainer">

  </div>

</template>

<style>
@import 'mapbox-gl/dist/mapbox-gl.css';

.map-container {
  width: 100%;
  /* Sin app-bar: el mapa ocupa todo el viewport (dvh = mejor en móvil). */
  height: 100dvh;
}


</style>