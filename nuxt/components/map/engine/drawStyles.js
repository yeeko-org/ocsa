// Estilos del editor de dibujo (mapbox-gl-draw): sustituyen por completo a
// los de la librería, así que cada estado (activo/inactivo, vértice,
// punto medio) necesita su propia capa.
export const DRAW_STYLES = [
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
      'circle-color': '#25d0a8',
      'circle-stroke-width': 2,
      'circle-stroke-color': '#FFFFFF'
    }
  },
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
      'circle-color': '#9a3fce',
      'circle-stroke-width': 2,
      'circle-stroke-color': '#FFFFFF'
    }
  },
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
  {
    id: 'gl-draw-polygon-and-line-vertex-active',
    type: 'circle',
    filter: ['all',
      ['==', 'meta', 'vertex'],
      ['==', '$type', 'Point'],
      ['!=', 'mode', 'static']
    ],
    paint: {
      'circle-radius': 6,
      'circle-color': '#fff',
      'circle-stroke-color': '#9a3fce',
      'circle-stroke-width': 2
    }
  },
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
