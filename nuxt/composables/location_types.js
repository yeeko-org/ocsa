export const location_types = [
  {
    id: 'point',
    name: 'Punto',
    icon: 'location_on',
    is_point: true,
    geometry_type: 'Point',
    mapbox_btn: 'draw_point',
    helps: ['Haz clic en el mapa para colocar un punto.']
  },
  {
    id: 'line',
    name: 'Línea',
    icon: 'timeline',
    is_point: false,
    geometry_type: 'LineString',
    mapbox_btn: 'draw_line_string',
    helps: [
      'Haz clic para empezar a dibujar una línea.',
      'Haz clic de nuevo para agregar cada punto.',
      'Haz doble clic para finalizar la línea.',
      // 'Puedes dibujar múltiples líneas.', // Added
    ],
  },
  {
    id: 'polygon',
    name: 'Polígono',
    icon: 'map',
    is_point: false,
    geometry_type: 'Polygon',
    mapbox_btn: 'draw_polygon',
    helps: [
      'Haz clic para empezar a dibujar un polígono.',
      'Haz clic de nuevo para agregar cada punto.',
      'Haz doble clic para finalizar el polígono.',
      // 'Puedes dibujar múltiples polígonos.', // Added
    ],
  },
]
