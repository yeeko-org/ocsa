<script setup>
import mapboxgl from 'mapbox-gl';
import {storeToRefs} from "pinia";
import ExtractivismLegend from "~/components/map/filters/custom/ExtractivismLegend.vue";
import { useMapStore } from "~/store/map.js";
import { useLayers } from "~/components/map/engine/useLayers.js";
import { setupInteractions } from "~/components/map/engine/mapInteractions.js";
import { useClusters } from "~/components/map/engine/useClusters.js";
import ProjectsPanel from "~/components/map/panel/ProjectsPanel.vue";
import TopControls from "~/components/map/TopControls.vue";
import LayerSwitch from "~/components/map/engine/LayerSwitch.vue";
import FilterRail from "~/components/map/filters/FilterRail.vue";
import FilterChips from "~/components/map/filters/FilterChips.vue";
import { useMapFilterUrl } from "~/components/map/filters/useMapFilterUrl.js";
import { useMapStyle, MAP_STYLE } from "~/components/map/engine/useMapStyle.js";
import { SHEET_REST_PX, SHEET_MID_SNAP } from "~/store/map.js";
import { useDisplay } from "vuetify";

definePageMeta({
  layout: 'map',
})

const mapContainer = ref(null);
let map = ref(null);
// `map.loaded()` vuelve a ser false mientras cargan teselas después del
// evento 'load'; si los datos llegan en ese hueco, un `on('load')` tardío
// nunca dispara. Esta bandera recuerda que el evento ya ocurrió.
let mapLoadFired = false;
const { smAndDown } = useDisplay()

const mapStore = useMapStore()
const { loadData, hydrateProjectLocations } = mapStore
const {
  projectLocations,
  readyGets,
  targetProjectId,
  topBandHeight,
  sheetCoveredPx,
} = storeToRefs(mapStore)

// Padding de fitBounds: reserva lo que el chrome tapa del mapa. Escritorio:
// el panel abajo-derecha y el pill inferior. Teléfono: la banda superior y
// el sheet en su snap medio (al que sube al seleccionar), con un margen
// para que el proyecto no quede pegado al borde.
function fitPadding() {
  if (!smAndDown.value)
    return { top: 80, bottom: 120, left: 80, right: 420 }
  return {
    top: topBandHeight.value + 16,
    bottom: Math.round(window.innerHeight * SHEET_MID_SNAP) + 16,
    left: 24,
    right: 24,
  }
}

// Padding lógico del mapa en teléfono: la cámara, fitBounds y getBounds
// trabajan sobre la región que ni la banda superior ni el sheet tapan. Se
// reaplica en cada cambio de snap.
function applyPadding() {
  if (!map.value || !smAndDown.value) return
  map.value.setPadding({
    top: topBandHeight.value,
    bottom: sheetCoveredPx.value,
    left: 0,
    right: 0,
  })
}
watch([topBandHeight, sheetCoveredPx], applyPadding)

// Sin desenfoque en equipos modestos: la clase la lee map-glass.css.
const LOW_END_CLASS = 'map-low-end'
function isLowEndDevice() {
  const mem = navigator.deviceMemory
  const cores = navigator.hardwareConcurrency
  return (mem != null && mem <= 2) || (cores != null && cores <= 4)
}

const {
  initializeMapLayers,
  updateMapData
} = useLayers(map);

const { setupClusterMarkers } = useClusters(map);

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

// Si la URL trae actores, carga el payload de inmediato para reconciliar sus
// nombres (llegan como "Actor #id"); ensureActors() llama reconcileActorNames.
if (mapStore.filters.actors.length) mapStore.ensureActors();

onMounted(() => {
  if (isLowEndDevice()) document.documentElement.classList.add(LOW_END_CLASS)
  buildPreMap();
  loadData();
});

onUnmounted(() => {
  document.documentElement.classList.remove(LOW_END_CLASS)
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

// flush 'post': la selección también sube el sheet al snap medio y eso
// reaplica el padding con setPadding (un jumpTo, que detiene toda animación
// en curso). Este watcher corre después de ese, así el fitBounds no se
// cancela.
watch(targetProjectId, (newId) => {
  if (!newId || !map.value) return;

  // 1. Filtrar todas las geometrías asociadas a ese ID
  const all_features = projectLocations.value.features.filter(f =>
    f.properties.project.id === newId
  );
  // Se encuadra solo lo pintado. El fallback al conjunto completo cubre un
  // caso que no debería darse (el proyecto entra al panel por matchear el
  // filtro) pero que dejaría un fitBounds vacío.
  const in_states = all_features.filter(mapStore.featureMatchesStates);
  const features = in_states.length ? in_states : all_features;

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
      padding: fitPadding(),
      maxZoom: 12,
      duration: 1500
    });
  }
}, { flush: 'post' });

function buildPreMap() {
  if (!mapContainer.value) return;
  mapboxgl.accessToken = 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';

  map.value = new mapboxgl.Map({
    container: mapContainer.value,
    style: MAP_STYLE,
    // Encuadre inicial por bounding box: Mapbox calcula el zoom según
    // el tamaño del contenedor, así México siempre abarca la pantalla.
    bounds: [[-118.4, 14.5], [-86.7, 32.7]], // [SW, NE] de México
    fitBoundsOptions: { padding: 20 },
    // Rotación e inclinación bloqueadas: el norte siempre arriba.
    dragRotate: false,
    pitchWithRotate: false,
    // Escritorio: controles y leyendas de Mapbox abajo-izquierda (el panel
    // de proyectos ocupa la esquina inferior derecha). Teléfono: la
    // atribución abajo-derecha, ambos levantados sobre el sheet en reposo
    // (CSS abajo): setPadding no mueve los controles.
    logoPosition: 'bottom-left',
    attributionControl: false,
  });
  map.value.touchZoomRotate.disableRotation();
  map.value.touchPitch.disable();
  const phone = smAndDown.value
  map.value.addControl(
    new mapboxgl.AttributionControl({ compact: phone }),
    phone ? 'bottom-right' : 'bottom-left');
  // Teléfono: sin NavigationControl (el pellizco hace zoom; sin brújula
  // porque la rotación está bloqueada).
  if (!phone)
    map.value.addControl(
      new mapboxgl.NavigationControl({ showCompass: false }), 'bottom-left');
  map.value.once('load', () => {
    mapLoadFired = true;
    applyPadding();
  });
}

function initBuildMap() {
  if (mapLoadFired || map.value.loaded()) {
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
  // Sin popup de hover en teléfono: el toque solo selecciona el proyecto.
  setupInteractions(map, { hoverPopup: !smAndDown.value });
  setupClusterMarkers();
  // Carga diferida del índice de facetas: ya pintamos el mapa, no bloquea el
  // primer paint. Al llegar, visibleProjectIds cambia y el watch re-pinta.
  mapStore.ensureFacets();
}

</script>

<template>
  <TopControls/>

  <FilterRail/>
  <FilterChips/>

  <!-- Leyenda de extractivismo: sheet semitransparente flotante, siempre
       visible (decisions §5). En md+, a la derecha de la isla superior;
       en sm/xs, franja bajo la isla. -->
  <ExtractivismLegend/>
  <ProjectsPanel/>
  <LayerSwitch
    :is_satellite="isSatelliteView"
    :is_switching="isSwitching"
    @toggle="toggleMapStyle"/>

  <div
    class="map-container"
    :class="{ 'map-container--phone': smAndDown }"
    ref="mapContainer"
  >

  </div>

</template>

<style>
@import 'mapbox-gl/dist/mapbox-gl.css';

.map-container {
  width: 100%;
  /* Sin app-bar: el mapa ocupa todo el viewport (dvh = mejor en móvil). */
  height: 100dvh;
}

/* Teléfono: logo y atribución sobre el sheet en reposo (nunca tapados de
   forma permanente; el sheet a media o completa altura los cubre solo
   mientras el usuario lo tiene arriba). */
.map-container--phone .mapboxgl-ctrl-bottom-left,
.map-container--phone .mapboxgl-ctrl-bottom-right {
  bottom: v-bind(SHEET_REST_PX);
}


</style>