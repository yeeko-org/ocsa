// components/map/useMapLayers.js
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";

export function useMapLayers(map) {
  const mainStore = useMainStore()
  const { geometry_types, cats } = storeToRefs(mainStore)
  function initializeMapLayers() {
    // Separate points, lines, multilinestrings, and polygons from the data
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

    geometry_types.value.forEach(dt => {
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
        ],
        'icon-offset': [0, -15],
        'visibility': 'visible',
        'icon-allow-overlap': true
      },
    });
  }

  function updateMapData(projectLocations, selectedExtractivismTypes) {
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
    geometry_types.value.forEach(dt => {
      data[dt.source] = {
        type: 'FeatureCollection',
        features: features_filtered.filter(f => f.geometry.type === dt.type)
      };
    });

    geometry_types.value.forEach(dt => {
      const source = map.value.getSource(dt.source);
      if (source) {
        source.setData(data[dt.source]);
      }
    });
  }

  return {
    initializeMapLayers,
    updateMapData
  }
}