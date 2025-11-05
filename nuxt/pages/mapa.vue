
<script setup>

import mapboxgl from 'mapbox-gl';
import * as d3 from 'd3';
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

function hydrateProjectLocations() {
  const random_color = "#755f4c"
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
      const extr_types = megaproject_type_obj.extractivism_types || [];
      props.extractivism_types = extr_types || [];
      props.power = extr_types.length === 1 ? 2 : 1;
      // props.two_extractivism_types = extr_types || [];
      // if (extr_types.length === 1) {
      //   props.two_extractivism_types = [extr_types[0], extr_types[0]];
      // }
    } else {
      props.color = '#03fcd7'; // Gris por defecto si no hay tipo
      props.extractivism_type = null;
      props.extractivism_types = [];
    }
  });
  buildPreMap();
  buildMap();
}


watch(ready_gets, (newVal) => {
  if (newVal === 2) {
    hydrateProjectLocations();
  }
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
  map.value.addControl(new mapboxgl.NavigationControl());
}

function updateMapData() {
  const project_locations = projectLocations.value;

  const selected_et = selectedExtractivismTypes.value;
  const select_all = selected_et.length === 0;

  const features_filtered = project_locations.features.filter(f => {
    if (select_all)
      return true;
    const extractivism_types = f.properties.extractivism_types;
    return selected_et.some(set => extractivism_types.includes(set));
  });

  let data = {};
  geometry_types.forEach(dt => {
    data[dt.source] = {
      type: 'FeatureCollection',
      features: features_filtered.filter(f => f.geometry.type === dt.type)
    };
  });

  geometry_types.forEach(dt => {
    const source = map.value.getSource(dt.source);
    if (source) {
      source.setData(data[dt.source]);
    }
  });
}

function buildMap() {
  // const project_locations = projectLocations.value;

  map.value.on('load', () => {
    initializeMapLayers();
    updateMapData();
  });
}

function initializeMapLayers() {
  // Separate points, lines, multilinestrings, and polygons from the data
  const selected_et = selectedExtractivismTypes.value;
  const select_all = selected_et.length === 0;

  // let data = {}
  // const selected_et = selectedExtractivismTypes.value;
  // const select_all = selected_et.length === 0;
  // let ready_prints = 0
  // console.log("selected_et", selected_et);
  // const features_filtered = project_locations.features.filter(f => {
  //   if (select_all) return true;
  //   const extractivism_types = f.properties.extractivism_types;
  //   const some_filtered = selected_et.some(set =>
  //     (extractivism_types.includes(set))
  //   );
  //   // if (some_filtered && ready_prints < 10) {
  //   //   console.log("extractivism_types", extractivism_types);
  //   //   console.log("Feature:", f);
  //   //   ready_prints += 1;
  //   // }
  //   return some_filtered;
  // });

  // geometry_types.forEach(dt => {
  //   data[dt.collection] = {
  //     type: 'FeatureCollection',
  //     features: features_filtered.filter(f =>
  //       f.geometry.type === dt.type)
  //   }
  // });

  let cluster_properties = {};
  cats.value.extractivism_type.forEach(et => {
    cluster_properties[`sum_${et.id}`] = [
      '+',
      [
        'case',
        ['in', et.id, ['get', 'extractivism_types']],
        ['get', 'power'],
        0
      ]
    ];
  });

  geometry_types.forEach(dt => {
    map.value.addSource(dt.source, {
      type: 'geojson',
      data: { type: 'FeatureCollection', features: [] },
      ...(dt.type === "Point" ? {
        cluster: true,
        clusterMaxZoom: 10,
        clusterRadius: 20,
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
      'fill-opacity': 0.3,
    }
  });

  // map.value.addLayer({
  //     id: 'clusters',
  //     type: 'circle',
  //     source: 'proyectos',
  //     filter: ['has', 'point_count'],
  //     // filter: ['=', 'cluster', true],
  //     paint: {
  //         'circle-opacity': 0.6,
  //         'circle-color': [
  //             'step',
  //             ['get', 'point_count'],
  //             '#51bbd6',
  //             20, '#f1f075',
  //             60, '#f28cb1'
  //         ],
  //         'circle-radius': [
  //             'step',
  //             ['get', 'point_count'],
  //             15,
  //             20, 22,
  //             60, 29
  //         ],
  //         'circle-emissive-strength': 1
  //     }
  // });

  // map.value.addLayer({
  //     id: 'cluster-count',
  //     type: 'symbol',
  //     source: 'proyectos',
  //     filter: ['has', 'point_count'],
  //     layout: {
  //         'text-field': ['get', 'point_count_abbreviated'],
  //         // 'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
  //         'text-size': 12
  //     }
  // });

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

  const markers = {};
  let markersOnScreen = {};

  map.value.on('render', () => {
    if (!map.value.isSourceLoaded('proyectos'))
      return;
    if (select_all)
      updateMarkers();
    else{
      console.log("no hay markers por filtro");
    }
  });

  function updateMarkers() {
    const newMarkers = {};
    const features = map.value.querySourceFeatures('proyectos');
    // console.log("Cluster features on screen:", features);

    for (const feature of features) {
      const coords = feature.geometry.coordinates;
      const props = feature.properties;
      if (!props.cluster) continue;
      const id = props.cluster_id;

      let marker = markers[id];
      if (!marker) {
        // createDonutChart(props);
        const el = createDonutChart(props);
        marker = markers[id] = new mapboxgl.Marker({
            element: el
        }).setLngLat(coords);
      }
      newMarkers[id] = marker;

      if (!markersOnScreen[id])
        marker.addTo(map.value);
    }

    for (const id in markersOnScreen) {
      if (!newMarkers[id])
        markersOnScreen[id].remove();
    }
    markersOnScreen = newMarkers;
  }

}

const extractivism_type_props = computed(() => {
  const et_props = {"colors": [], "icons": [], "ids": []};
  cats.value.extractivism_type.forEach(et => {
    et_props.colors.push(et.color);
    et_props.icons.push(et.icon);
    et_props.ids.push(et.id);
  });
  return et_props;
});


const r_scale = d3.scalePow().exponent(1 / 3)
  .domain([2,300])
  .range([15,32]);

const font_scale = d3.scalePow().exponent(1 / 3)
  .domain([2,300])
  .range([12,16]);


function createDonutChart(props) {
  // console.log("Creating donut chart for cluster:", props);
  // Prepare data

  const et_props = extractivism_type_props.value;

  let counts = et_props.ids.map(et_id => props[`sum_${et_id}`] || 0);

  // Calculate total using D3 (or simple reduce)
  const total = d3.sum(counts);
  const max = d3.max(counts);
  const only_one = total === max;
  let unique_et = null
  et_props.ids.forEach((et_id, index) => {
    if (counts[index] === max && only_one) {
      unique_et = et_id;
    }
  });
  const unique_et_full = cats.value.extractivism_type.find(
    et => et.id === unique_et);

  let r = r_scale(props.point_count);
  if (only_one) {
    r = r * 0.9;
  }
  const fontSize = font_scale(props.point_count);


  const r0 = Math.round(only_one ? r : r  * 0.6);
  const w = r * 2;

  // Create container element
  const el = document.createElement('div');

  // Create SVG using D3
  const svg = d3.select(el)
    .append('svg')
    .attr('width', w)
    .attr('height', w)
    .attr('viewBox', `-1 -1 ${w + 2} ${w + 2}`)
    .attr('text-anchor', 'middle')
    .style('font', `${fontSize}px sans-serif`)
    .style('display', 'block');

  // Create D3 pie layout
  const pie = d3.pie()
    .sort(null)
    .value(d => d);

  // Create a group for the donut, centered
  const g = svg.append('g')
    .attr('transform', `translate(${r}, ${r})`);

  if (!only_one) {
    // Create D3 arc generator for donut
    const arc = d3.arc()
      .innerRadius(r0)
      .outerRadius(r);

    // Draw donut segments
    g.selectAll('path')
      .data(pie(counts))
      .enter()
      .append('path')
      .attr('d', arc)
      .attr('fill', (d, i) => et_props.colors[i])
      .on('mouseenter', function(event, d) {
          d3.select(this).attr('opacity', 0.7);
      })
      .on('mouseleave', function(event, d) {
          d3.select(this).attr('opacity', 1);
      });
  }

  // Add white center circle
  g.append('circle')
    .attr('r', r0)
    .attr('fill', only_one && unique_et_full ? unique_et_full.color : '#ffffff');

  // Add center text
  g.append('text')
    .attr('dominant-baseline', 'central')
    .text(props.point_count)
    .attr('fill', only_one && unique_et_full ? '#ffffff' : '#000000')
    .attr('style', only_one && unique_et_full ? 'text-shadow: 1px 1px 3px #000000;' : '');
    // .style('text-shadow', only_one && unique_et_full ? '1px 1px 3px #000000;' : '');

  return el;


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
      @update:modelValue="updateMapData()"
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