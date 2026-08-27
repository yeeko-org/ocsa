export const LOCATION_TYPES = [
  {
    id: 'point',
    name: 'Punto',
    name_plural: 'puntos',
    icon: 'location_on',
    is_point: true,
    geometry_type: 'Point',
    draw_mode: 'draw_point',
    draw_icon: 'location_on',
    helps: ['Haz clic en el mapa para colocar un punto.']
  },
  {
    id: 'line',
    name: 'Línea',
    name_plural: 'líneas',
    icon: 'timeline',
    is_point: false,
    geometry_type: 'LineString',
    draw_mode: 'draw_line_string',
    draw_icon: 'polyline',
    helps: [
      'Haz clic para empezar a dibujar una línea.',
      'Haz clic de nuevo para agregar cada punto.',
      'Haz doble clic para finalizar la línea.',
      'Puedes dibujar múltiples líneas.',
    ],
  },
  {
    id: 'polygon',
    name: 'Polígono',
    name_plural: 'polígonos',
    icon: 'map',
    is_point: false,
    geometry_type: 'Polygon',
    draw_mode: 'draw_polygon',
    draw_icon: 'highlight_mouse_cursor',
    helps: [
      'Haz clic para empezar a dibujar un polígono.',
      'Haz clic de nuevo para agregar cada punto.',
      'Haz doble clic para finalizar el polígono.',
      'Puedes dibujar múltiples polígonos.',
    ],
  },
]

// Cada entrada es UNA fuente del mapa público. Mapbox pinta Polygon y
// MultiPolygon con la misma capa `fill`, y LineString y MultiLineString con
// la misma capa `line`, así que las variantes Multi* comparten fuente con su
// tipo simple en lugar de duplicar fuente y capas.
export const GEOMETRY_TYPES = [
  {
    "types": ["Polygon", "MultiPolygon"],
    "collection": "polygons",
    "source": "proyectos-poligonos",
    "main_layer": "proyectos-poligonos-fill"
  },
  {
    "types": ["LineString", "MultiLineString"],
    "collection": "lines",
    "source": "proyectos-lineas",
    "main_layer": "proyectos-lineas"
  },
  {
    "types": ["Point"],
    "collection": "points",
    "source": "proyectos",
    "main_layer": "unclustered-point"
  },
]
