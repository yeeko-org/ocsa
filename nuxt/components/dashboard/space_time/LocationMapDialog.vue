<script setup>

import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import {LOCATION_TYPES} from "~/composables/location_types.js";
import {MAP_STYLE, SATELLITE_STYLE} from "~/components/map/engine/useMapStyle.js";

const props = defineProps({
  location_type: {
    type: String,
    required: true,
    validator: (value) => ['point', 'line', 'polygon'].includes(value)
  },
  full_main: Object,
  close_position: Object,
  can_expand: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['update:location', 'close-dialog']);

const is_expanded = defineModel('expanded', {type: Boolean, default: false});

const mapContainer = ref(null);
const map = ref(null);
const draw = ref(null);
const isMapInitialized = ref(false);
const isSatelliteView = ref(true);


const location_type_full = computed(() => LOCATION_TYPES.find(
    loc => loc.id === props.location_type));

const is_point = computed(() => location_type_full.value?.is_point);
const is_full_point = computed(() =>
    props.full_main && props.full_main.latitude && props.full_main.longitude);
// Process the existing location data if available

const simple_type = computed(() => location_type_full.value?.geometry_type);

// mapbox-gl-draw sólo sabe editar geometrías simples, así que una Multi*
// guardada se separa en una feature por parte para poder dibujarla.
function splitGeometry(geometry) {
  if (!geometry) return []
  const {type, coordinates} = geometry
  if (!type.startsWith('Multi'))
    return [geometry]
  const part_type = type.replace('Multi', '')
  return coordinates.map(coords => ({type: part_type, coordinates: coords}))
}

function asFeature(geometry) {
  return {type: 'Feature', geometry, properties: {}}
}

const existingFeatures = computed(() => {
  const loc = props.full_main;
  if (!loc) return [];
  if (is_point.value) {
    if (!is_full_point.value) return [];
    return [asFeature({
      type: 'Point',
      coordinates: [parseFloat(loc.longitude), parseFloat(loc.latitude)]
    })];
  }
  const geojson = loc.geojson;
  if (!geojson) return [];
  let geometries;
  if (geojson.type === 'FeatureCollection')
    geometries = geojson.features.map(f => f.geometry);
  else if (geojson.type === 'Feature')
    geometries = [geojson.geometry];
  else
    geometries = [geojson];
  return geometries
    .filter(Boolean)
    .flatMap(splitGeometry)
    .map(asFeature);
});

onMounted(() => {
  initializeMap();
});

// Mapbox no detecta por sí solo el cambio de ancho del contenedor
watch(is_expanded, async () => {
  await nextTick();
  map.value?.resize();
});

// Initialize the MapBox map
function initializeMap() {
  if (isMapInitialized.value) return;
  // console.log("existingFeatures", existingFeatures.value);
  mapboxgl.accessToken = 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';
  // console.log("process.env", process.env)
  // mapboxgl.accessToken = process.env.NUXT_MAPBOX_TOKEN;

  // Default center (can be adjusted based on your region)
  const defaultCenter = [-101.81312434928653, 22.64061934572902];

  // Use existing coordinates if available for a point
  const first_feature = existingFeatures.value[0]
  const has_center = first_feature?.geometry?.type === 'Point'
  let center = defaultCenter
  let zoom = 4
  if (has_center){
    center = first_feature.geometry.coordinates
    zoom = 13
  }
  else if (props.close_position){
    const close_pos = props.close_position
    // console.log("close_pos", close_pos)
    center = [close_pos.longitude, close_pos.latitude]
    zoom = close_pos.state ? 12 : 13
  }

  map.value = new mapboxgl.Map({
    container: mapContainer.value,
    style: isSatelliteView.value ? SATELLITE_STYLE : MAP_STYLE,
    center: center,
    zoom: zoom
  });

  map.value.on('load', () => {
    setupDrawTools();
    isMapInitialized.value = true;

    // add stylo to points
    map.value.addSource('point-source', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: []
      }
    });

    map.value.addLayer({
      id: 'point-layer',
      type: 'circle',
      source: 'point-source',
      paint: {
        'circle-radius': [
          'case', ['==', ['get', 'selected'], true],
          8, // If selected
          5 // If not selected
        ],
        'circle-color': [
          'case', ['==', ['get', 'selected'], true],
          '#9a3fce', // If selected
          '#25d0a8' // If not selected
        ],
        'circle-stroke-width': 2,
        'circle-stroke-color': '#FFFFFF',
      }
    });

    // Zoom to the appropriate area based on location type
    zoomToFeatures(existingFeatures.value);
  });
}

// Set up the MapBox drawing tools
function setupDrawTools(skipAddingExistingGeometry = false) {
  // Create and add the draw control
  const is_edit = existingFeatures.value.length > 0

  draw.value = new MapboxDraw({
    displayControlsDefault: false,
    controls: {
      // point: is_point.value && !is_edit,
      point: is_point.value,
      line_string: props.location_type === 'line',
      polygon: props.location_type === 'polygon',
      trash: true
    },
    styles: [
      // Point style
      // {
      //   id: 'gl-draw-point',
      //   type: 'circle',
      //   filter: ['all', ['==', '$type', 'Point']],
      //   paint: {
      //     // 'circle-radius': 8,
      //     'circle-radius': [
      //       'case', ['==', ['get', 'selected'], true], // Check if selected
      //       8, // If selected
      //       5 // If not selected
      //     ],
      //     // 'circle-color': '#9a3fce',
      //     'circle-color': [
      //         'case', ['==', ['get', 'selected'], true], // Check if selected
      //         '#9a3fce', // If selected
      //         '#3f51b5' // If not selected
      //     ],
      //     'circle-stroke-width': 2,
      //     'circle-stroke-color': '#FFFFFF'
      //   }
      // },
      {
        id: 'gl-draw-point-inactive',
        type: 'circle',
        filter: ['all',
          ['==', '$type', 'Point'],
          ['==', 'meta', 'feature'],
          ['!=', 'active', 'true']
        ],
        paint: {
          'circle-radius': 5,
          'circle-color': '#25d0a8', // Blue
          'circle-stroke-width': 2,
          'circle-stroke-color': '#FFFFFF'
        }
      },
      // Point styles - active/selected
      {
        id: 'gl-draw-point-active',
        type: 'circle',
        filter: ['all',
          ['==', '$type', 'Point'],
          ['==', 'meta', 'feature'],
          ['==', 'active', 'true']
        ],
        paint: {
          'circle-radius': 8,
          'circle-color': '#9a3fce', // Purple
          'circle-stroke-width': 2,
          'circle-stroke-color': '#FFFFFF'
        }
      },
      // Polygon styles
      {
        id: 'gl-draw-polygon-fill',
        type: 'fill',
        filter: ['all', ['==', '$type', 'Polygon'], ['!=', 'mode', 'static']],
        paint: {
          'fill-color': '#9a3fce',
          'fill-outline-color': '#9a3fce',
          'fill-opacity': 0.3
        }
      },
      // Polygon outline
      {
        id: 'gl-draw-polygon-stroke',
        type: 'line',
        filter: ['all', ['==', '$type', 'Polygon'], ['!=', 'mode', 'static']],
        layout: {
          'line-cap': 'round',
          'line-join': 'round'
        },
        paint: {
          'line-color': '#9a3fce',
          'line-width': 2
        }
      },
      // Vertex points
      {
        id: 'gl-draw-polygon-and-line-vertex-active',
        type: 'circle',
        filter: ['all', ['==', 'meta', 'vertex'], ['==', '$type', 'Point'], ['!=', 'mode', 'static']],
        paint: {
          'circle-radius': 6,
          'circle-color': '#fff',
          'circle-stroke-color': '#9a3fce',
          'circle-stroke-width': 2
        }
      },
      // Line string
      {
        id: 'gl-draw-line',
        type: 'line',
        filter: ['all', ['==', '$type', 'LineString'], ['!=', 'mode', 'static']],
        layout: {
          'line-cap': 'round',
          'line-join': 'round'
        },
        paint: {
          'line-color': '#9a3fce',
          'line-width': 2
        }
      },
      // Midpoints
      {
        id: 'gl-draw-polygon-midpoint',
        type: 'circle',
        filter: ['all', ['==', 'meta', 'midpoint'], ['==', '$type', 'Point']],
        paint: {
          'circle-radius': 4,
          'circle-color': '#9a3fce',
          'circle-stroke-color': '#fff',
          'circle-stroke-width': 1
        }
      }
    ]
  });

  map.value.addControl(draw.value);

  if (existingFeatures.value.length && !skipAddingExistingGeometry)
    draw.value.add({
      type: 'FeatureCollection',
      features: existingFeatures.value
    });


  if (!is_edit){
    const draw_mode = location_type_full.value?.draw_mode || 'simple_select'
    draw.value.changeMode(draw_mode);
  }

  map.value.on('draw.create', updateDrawing);
  map.value.on('draw.update', updateDrawing);
  map.value.on('draw.delete', clearDrawing);

}

function updateDrawing(e) {
  // Sólo el punto es único: dibujar otro reemplaza al anterior. Líneas y
  // polígonos admiten varias partes, cada una editable por separado.
  if (is_point.value && draw.value.getAll().features.length > 1) {
    const latest = e.features[0];
    draw.value.deleteAll();
    draw.value.add(latest);
  }
  syncPointSource();
  emitLocation();
}

// Handle deletion of drawings
function clearDrawing() {
  syncPointSource();
  emitLocation();
}

function syncPointSource() {
  if (!is_point.value) return;
  const point_source = map.value.getSource('point-source');
  if (!point_source) return;
  point_source.setData({
    type: 'FeatureCollection',
    features: currentFeatures()
  });
}

// Sólo las partes del tipo de la ubicación: los controles de dibujo ya lo
// garantizan, pero una geometría heredada podría traer otra cosa y el API
// rechaza las mezclas.
function currentFeatures() {
  if (!draw.value) return [];
  return draw.value.getAll().features.filter(
      f => f.geometry.type === simple_type.value);
}

// El API guarda UNA sola Feature por ubicación: varias partes se ensamblan
// aquí en una Multi* para que el estado del front ya tenga la forma final.
function assembleFeature(features) {
  if (!features.length) return null;
  if (features.length === 1) return features[0];
  return asFeature({
    type: `Multi${simple_type.value}`,
    coordinates: features.map(f => f.geometry.coordinates)
  });
}

function emitLocation() {
  emit('update:location', assembleFeature(currentFeatures()));
}

// Zoom to the appropriate area based on geometry type
function zoomToFeatures(features) {
  if (!map.value || !features?.length) return;

  if (features.length === 1 && features[0].geometry.type === 'Point') {
    // For points, zoom to approximately 3km around
    map.value.flyTo({
      center: features[0].geometry.coordinates,
      zoom: 14
    });
    return;
  }
  const bounds = calculateBounds(features);
  if (bounds)
    map.value.fitBounds(bounds, {
      padding: 50
    });
}

// Aplana cualquier anidamiento de coordenadas (Point, LineString, Polygon o
// sus Multi*) hasta la lista de pares [lng, lat].
function flattenCoordinates(coordinates) {
  if (typeof coordinates[0] === 'number') return [coordinates];
  return coordinates.flatMap(flattenCoordinates);
}

// Calculate bounds covering every part of every feature
function calculateBounds(features) {
  const coordinates = features
    .filter(f => f.geometry?.coordinates?.length)
    .flatMap(f => flattenCoordinates(f.geometry.coordinates));

  if (!coordinates.length) return null;

  const lngs = coordinates.map(coord => coord[0]);
  const lats = coordinates.map(coord => coord[1]);

  return [
    [Math.min(...lngs), Math.min(...lats)], // SW corner
    [Math.max(...lngs), Math.max(...lats)]  // NE corner
  ];
}

function toggleMapStyle(val) {
  if (!map.value) return;

  const newStyle = isSatelliteView.value ? SATELLITE_STYLE : MAP_STYLE

  try {
    const features = draw.value ? draw.value.getAll().features : [];

    if (draw.value) {
      map.value.removeControl(draw.value);
      draw.value = null;
    }

    map.value.setStyle(newStyle);

    map.value.once('styledata', () => {
      setupDrawTools(true);
      if (features.length)
        draw.value.add({type: 'FeatureCollection', features});
    });
  } catch (error) {
    console.error("Error toggling map style:", error);
    // Reset the toggle state in case of error
    isSatelliteView.value = !isSatelliteView.value;
  }
}

</script>

<template>
  <v-card>
    <v-card-title class="text-headline-small d-flex">
      {{ full_main.id ? 'Editar' : 'Agregar' }}
      {{ location_type_full.name || 'Ubicación' }}
      <v-switch
        v-model="isSatelliteView"
        color="primary"
        label="Vista satelital"
        hide-details
        density="compact"
        class="ml-3"
        @change="toggleMapStyle"
      ></v-switch>

      <v-spacer></v-spacer>
      <v-btn
        v-if="can_expand"
        variant="text"
        icon
        @click="is_expanded = !is_expanded"
        v-tooltip:bottom="is_expanded ? 'Restaurar' : 'Expandir mapa'"
      >
        <v-icon>
          {{ is_expanded ? 'fullscreen_exit' : 'fullscreen' }}
        </v-icon>
      </v-btn>
      <v-btn variant="text" @click="emit('close-dialog')" icon>
        <v-icon>close</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text>
      <div class="d-flex align-center mb-2">
      </div>
      <div
        ref="mapContainer"
        style="width: 100%; height: 500px; border-radius: 4px;"
      ></div>
    </v-card-text>
  </v-card>
</template>
