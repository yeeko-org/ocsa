import { useMainStore } from "~/store/index.js";
import { useMapStore } from "~/store/map.js";
import { storeToRefs } from "pinia";
import { GEOMETRY_TYPES } from "~/composables/location_types.js";

export function useLayers(map) {
  const mainStore = useMainStore()
  const { cats } = storeToRefs(mainStore)
  const mapStore = useMapStore()
  function initializeMapLayers() {
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

    GEOMETRY_TYPES.forEach(dt => {
      map.value.addSource(dt.source, {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
        ...(dt.types.includes("Point") ? {
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

    // Ícono del tipo de extractivismo al centro de cada línea. Se fuerza
    // 'viewport' para que el pin quede vertical (si no, Mapbox lo rota al
    // ángulo de la línea) y el icon-offset lo levanta por encima del trazo,
    // igual que el pin de los puntos.
    map.value.addLayer({
      id: 'proyectos-lineas-icon',
      type: 'symbol',
      source: 'proyectos-lineas',
      layout: {
        'symbol-placement': 'line-center',
        'icon-rotation-alignment': 'viewport',
        'icon-image': [
            'image',
            ['get', 'icon_pin'],
            { params: { icon_color: ['get', 'color'] } }
        ],
        'icon-size': [
          "interpolate",
          ["linear"],
          ["zoom"],
          5, 0.6,
          11, 0.9,
          15, 1.2
        ],
        'icon-offset': [0, -15],
        'icon-allow-overlap': true
      },
    });


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
        'icon-size': [
          "interpolate",
          ["linear"],
          ["zoom"],
          5, 0.7,
          11, 1,
          15, 1.4
        ],
        'icon-offset': [0, -15],
        'visibility': 'visible',
        'icon-allow-overlap': true
      },
    });
  }

  function updateMapData() {
    const project_locations = mapStore.projectLocations;

    // Filtrado centralizado: un único Set de project.id resuelve TODAS las
    // dimensiones (store/map.js). Sin filtros = todos los proyectos.
    const visible = mapStore.visibleProjectIds;
    const features_filtered = project_locations.features.filter(
      f => visible.has(f.properties.project.id));

    let data = {};
    GEOMETRY_TYPES.forEach(gt => {
      data[gt.source] = {
        type: 'FeatureCollection',
        features: features_filtered.filter(
          f => gt.types.includes(f.geometry.type))
      };
    });

    GEOMETRY_TYPES.forEach(gt => {
      const source = map.value.getSource(gt.source);
      if (source) {
        source.setData(data[gt.source]);
      }
    });
  }

  return {
    initializeMapLayers,
    updateMapData
  }
}