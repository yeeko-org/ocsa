<script setup>

import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import {location_types} from "~/composables/location_types.js";

const props = defineProps({
  location_type: {
    type: String,
    required: true,
    validator: (value) => ['point', 'line', 'polygon'].includes(value)
  },
  full_main: Object,
  close_position: Object
});

const emit = defineEmits(['update:location', 'close-dialog']);

const mapContainer = ref(null);
const map = ref(null);
const draw = ref(null);
const isMapInitialized = ref(false);
const isSatelliteView = ref(true);


const location_type_full = computed(() => location_types.find(
    loc => loc.id === props.location_type));

const is_point = computed(() => location_type_full.value?.is_point);
const is_full_point = computed(() =>
    props.full_main && props.full_main.latitude && props.full_main.longitude);
// Process the existing location data if available

const existingGeometry = computed(() => {
  const loc = props.full_main;
  if (props.full_main) {
    if (is_point.value && is_full_point.value) {
      return {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [parseFloat(loc.longitude), parseFloat(loc.latitude)]
        },
        properties: {}
      };
    }
    else if (!is_point.value && props.full_main.geojson){
      if (props.full_main.geojson.type === 'Feature')
        return props.full_main.geojson
      else if (props.full_main.geojson.type === 'FeatureCollection')
        return props.full_main.geojson.features[0]
      else
        return props.full_main.geojson
    }
  }
  return null;
});

onMounted(() => {
  initializeMap();
});

// Initialize the MapBox map
function initializeMap() {
  if (isMapInitialized.value) return;
  // console.log("existingGeometry", existingGeometry.value);
  mapboxgl.accessToken = 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q';
  // console.log("process.env", process.env)
  // mapboxgl.accessToken = process.env.NUXT_MAPBOX_TOKEN;

  // Default center (can be adjusted based on your region)
  const defaultCenter = [-101.81312434928653, 22.64061934572902];

  // Use existing coordinates if available for a point
  const has_center = existingGeometry.value
      && existingGeometry.value.geometry.type === 'Point'
  let center = defaultCenter
  let zoom = 4
  if (has_center){
    center = existingGeometry.value.geometry.coordinates
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
    style: isSatelliteView.value
      ? 'mapbox://styles/rickrebel/cm83y5cbp004301s5861t18gi'
      : 'mapbox://styles/rickrebel/cm6ls9un800kr01qqdu1g48nq',
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
    if (existingGeometry.value) {
      zoomToFeature(existingGeometry.value.geometry);
    }
  });
}

// Set up the MapBox drawing tools
function setupDrawTools(skipAddingExistingGeometry = false) {
  // Create and add the draw control
  const loc = props.full_main;
  let is_edit;
  if (is_point.value)
    is_edit = is_full_point.value
  else
    is_edit = !!loc.geojson

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

  if (existingGeometry.value && !skipAddingExistingGeometry)
    draw.value.add(existingGeometry.value);


  if (!is_edit){
    const draw_mode = location_type_full.value?.draw_mode || 'simple_select'
    draw.value.changeMode(draw_mode);
  }

  map.value.on('draw.create', updateDrawing);
  map.value.on('draw.update', updateDrawing);
  map.value.on('draw.delete', clearDrawing);

}

function updateDrawing(e) {

  const features = draw.value.getAll().features;
  // console.log("Features:", features);
  // If there's more than one feature
  if (features.length > 1) {
    const updatedFeature = e.features[0];
    draw.value.deleteAll();
    // Add back only the updated feature
    draw.value.add(updatedFeature);
    // console.log("Replaced other locations with the updated one");
  }

  const drawnFeatures = e.features || [];
  if (drawnFeatures.length > 0) {
    const feature = drawnFeatures[0];
    if (feature.geometry.type === 'Point') {
      const point_source = map.value.getSource('point-source');
      // console.log("point_source", point_source);
      if (!point_source) {
        map.value.addSource('point-source', {
          type: 'geojson',
          data: {
            type: 'FeatureCollection',
            features: [feature]
          }
        });
      }
      else {
        point_source.setData({
          type: 'FeatureCollection',
          features: [feature]
        });
      }
    }
    emit('update:location', feature);
  }
}
// Handle deletion of drawings
function clearDrawing() {
  // console.log("Drawing cleared", map.value)
  map.value.getSource('point-source').setData({
    type: 'FeatureCollection',
    features: []
  });
}

// Zoom to the appropriate area based on geometry type
function zoomToFeature(geometry) {
  if (!map.value || !geometry) return;

  if (geometry.type === 'Point') {
    // For points, zoom to approximately 3km around
    map.value.flyTo({
      center: geometry.coordinates,
      zoom: 14
    });
  } else {
    const bounds = calculateBounds(geometry);
    map.value.fitBounds(bounds, {
      padding: 50
    });
  }
}

// Calculate bounds for a geometry
function calculateBounds(geometry) {
  let coordinates = [];

  if (geometry.type === 'LineString')
    coordinates = geometry.coordinates
  else if (geometry.type === 'Polygon')
    coordinates = geometry.coordinates[0] // Outer ring of the polygon
  else
    return null

  const lngs = coordinates.map(coord => coord[0]);
  const lats = coordinates.map(coord => coord[1]);

  return [
    [Math.min(...lngs), Math.min(...lats)], // SW corner
    [Math.max(...lngs), Math.max(...lats)]  // NE corner
  ];
}

function toggleMapStyle(val) {
  if (!map.value) return;

  const newStyle = isSatelliteView.value
    ? 'mapbox://styles/rickrebel/cm83y5cbp004301s5861t18gi'
    : 'mapbox://styles/rickrebel/cm6ls9un800kr01qqdu1g48nq'

  try {
    const features = draw.value ? draw.value.getAll().features : [];
    const feature = features.length > 0 ? features[0] : null;

    if (draw.value) {
      map.value.removeControl(draw.value);
      draw.value = null;
    }

    map.value.setStyle(newStyle);

    map.value.once('styledata', () => {
      setupDrawTools(true);
      if (feature)
        draw.value.add(feature);

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
    <v-card-title class="text-h5 d-flex">
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
