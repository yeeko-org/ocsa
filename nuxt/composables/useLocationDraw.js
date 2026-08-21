import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import MapboxDraw from '@mapbox/mapbox-gl-draw'
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css'
import {LOCATION_TYPES} from '~/composables/location_types.js'
import {MAP_STYLE, SATELLITE_STYLE} from
    '~/components/map/engine/useMapStyle.js'
import {DRAW_STYLES} from '~/components/map/engine/drawStyles.js'

const ACCESS_TOKEN = 'pk.eyJ1Ijoicmlja3JlYmVsIiwiYSI6ImNrZDRtM2pkaDE2Mm4ycW8zbjl4NmhqNnkifQ.fXsECn7EtVBuGs9sidf94Q'

const DEFAULT_CENTER = [-101.81312434928653, 22.64061934572902]

/**
 * Edición de la geometría de una ubicación sobre Mapbox Draw.
 *
 * @param {Object} options
 * @param {Ref<string>} options.location_type id de LOCATION_TYPES
 * @param {Ref<Object>} options.full_main modelo de la ubicación
 * @param {Ref<Object>} options.close_position centro de respaldo (localidad
 *   o municipio) cuando la ubicación aún no tiene geometría
 * @param {Ref<HTMLElement>} options.container contenedor del mapa
 * @param {Function} options.onUpdate recibe la Feature ensamblada (o null)
 */
export function useLocationDraw(options) {
  const {location_type, full_main, close_position, container, onUpdate} =
      options

  const map = ref(null)
  const draw = ref(null)
  const isMapInitialized = ref(false)
  const isSatelliteView = ref(true)

  const location_type_full = computed(() => LOCATION_TYPES.find(
      loc => loc.id === location_type.value))

  const is_point = computed(() => location_type_full.value?.is_point)
  const is_full_point = computed(() =>
      full_main.value && full_main.value.latitude && full_main.value.longitude)

  const simple_type = computed(() => location_type_full.value?.geometry_type)

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
    const loc = full_main.value
    if (!loc) return []
    if (is_point.value) {
      if (!is_full_point.value) return []
      return [asFeature({
        type: 'Point',
        coordinates: [parseFloat(loc.longitude), parseFloat(loc.latitude)]
      })]
    }
    const geojson = loc.geojson
    if (!geojson) return []
    let geometries
    if (geojson.type === 'FeatureCollection')
      geometries = geojson.features.map(f => f.geometry)
    else if (geojson.type === 'Feature')
      geometries = [geojson.geometry]
    else
      geometries = [geojson]
    return geometries
      .filter(Boolean)
      .flatMap(splitGeometry)
      .map(asFeature)
  })

  function initializeMap() {
    if (isMapInitialized.value) return
    mapboxgl.accessToken = ACCESS_TOKEN

    // Un punto ya guardado manda sobre el centro de respaldo
    const first_feature = existingFeatures.value[0]
    const has_center = first_feature?.geometry?.type === 'Point'
    let center = DEFAULT_CENTER
    let zoom = 4
    if (has_center) {
      center = first_feature.geometry.coordinates
      zoom = 13
    }
    else if (close_position.value) {
      const close_pos = close_position.value
      center = [close_pos.longitude, close_pos.latitude]
      zoom = close_pos.state ? 12 : 13
    }

    map.value = new mapboxgl.Map({
      container: container.value,
      style: isSatelliteView.value ? SATELLITE_STYLE : MAP_STYLE,
      center: center,
      zoom: zoom
    })

    map.value.on('load', () => {
      setupDrawTools()
      isMapInitialized.value = true

      // Capa propia para los puntos: los estilos de draw no distinguen el
      // punto seleccionado con suficiente contraste sobre satélite.
      map.value.addSource('point-source', {
        type: 'geojson',
        data: {type: 'FeatureCollection', features: []}
      })

      map.value.addLayer({
        id: 'point-layer',
        type: 'circle',
        source: 'point-source',
        paint: {
          'circle-radius': [
            'case', ['==', ['get', 'selected'], true], 8, 5
          ],
          'circle-color': [
            'case', ['==', ['get', 'selected'], true], '#9a3fce', '#25d0a8'
          ],
          'circle-stroke-width': 2,
          'circle-stroke-color': '#FFFFFF',
        }
      })

      zoomToFeatures(existingFeatures.value)
    })
  }

  function setupDrawTools(skipAddingExistingGeometry = false) {
    const is_edit = existingFeatures.value.length > 0

    draw.value = new MapboxDraw({
      displayControlsDefault: false,
      controls: {
        point: is_point.value,
        line_string: location_type.value === 'line',
        polygon: location_type.value === 'polygon',
        trash: true
      },
      styles: DRAW_STYLES
    })

    map.value.addControl(draw.value)

    if (existingFeatures.value.length && !skipAddingExistingGeometry)
      draw.value.add({
        type: 'FeatureCollection',
        features: existingFeatures.value
      })

    if (!is_edit) {
      const draw_mode = location_type_full.value?.draw_mode || 'simple_select'
      draw.value.changeMode(draw_mode)
    }

    map.value.on('draw.create', updateDrawing)
    map.value.on('draw.update', updateDrawing)
    map.value.on('draw.delete', clearDrawing)
  }

  function updateDrawing(e) {
    // Sólo el punto es único: dibujar otro reemplaza al anterior. Líneas y
    // polígonos admiten varias partes, cada una editable por separado.
    if (is_point.value && draw.value.getAll().features.length > 1) {
      const latest = e.features[0]
      draw.value.deleteAll()
      draw.value.add(latest)
    }
    syncPointSource()
    emitLocation()
  }

  function clearDrawing() {
    syncPointSource()
    emitLocation()
  }

  function syncPointSource() {
    if (!is_point.value) return
    const point_source = map.value.getSource('point-source')
    if (!point_source) return
    point_source.setData({
      type: 'FeatureCollection',
      features: currentFeatures()
    })
  }

  // Sólo las partes del tipo de la ubicación: los controles de dibujo ya lo
  // garantizan, pero una geometría heredada podría traer otra cosa y el API
  // rechaza las mezclas.
  function currentFeatures() {
    if (!draw.value) return []
    return draw.value.getAll().features.filter(
        f => f.geometry.type === simple_type.value)
  }

  // El API guarda UNA sola Feature por ubicación: varias partes se ensamblan
  // aquí en una Multi* para que el estado del front ya tenga la forma final.
  function assembleFeature(features) {
    if (!features.length) return null
    if (features.length === 1) return features[0]
    return asFeature({
      type: `Multi${simple_type.value}`,
      coordinates: features.map(f => f.geometry.coordinates)
    })
  }

  function emitLocation() {
    onUpdate(assembleFeature(currentFeatures()))
  }

  function zoomToFeatures(features) {
    if (!map.value || !features?.length) return

    if (features.length === 1 && features[0].geometry.type === 'Point') {
      map.value.flyTo({
        center: features[0].geometry.coordinates,
        zoom: 14
      })
      return
    }
    const bounds = calculateBounds(features)
    if (bounds)
      map.value.fitBounds(bounds, {padding: 50})
  }

  // Aplana cualquier anidamiento de coordenadas (Point, LineString, Polygon o
  // sus Multi*) hasta la lista de pares [lng, lat].
  function flattenCoordinates(coordinates) {
    if (typeof coordinates[0] === 'number') return [coordinates]
    return coordinates.flatMap(flattenCoordinates)
  }

  function calculateBounds(features) {
    const coordinates = features
      .filter(f => f.geometry?.coordinates?.length)
      .flatMap(f => flattenCoordinates(f.geometry.coordinates))

    if (!coordinates.length) return null

    const lngs = coordinates.map(coord => coord[0])
    const lats = coordinates.map(coord => coord[1])

    return [
      [Math.min(...lngs), Math.min(...lats)], // esquina SO
      [Math.max(...lngs), Math.max(...lats)]  // esquina NE
    ]
  }

  // Cambiar de estilo recrea las capas: hay que rescatar las figuras y
  // volver a montar el control de dibujo sobre el estilo nuevo.
  function toggleMapStyle() {
    if (!map.value) return

    const newStyle = isSatelliteView.value ? SATELLITE_STYLE : MAP_STYLE

    try {
      const features = draw.value ? draw.value.getAll().features : []

      if (draw.value) {
        map.value.removeControl(draw.value)
        draw.value = null
      }

      map.value.setStyle(newStyle)

      map.value.once('styledata', () => {
        setupDrawTools(true)
        if (features.length)
          draw.value.add({type: 'FeatureCollection', features})
      })
    } catch (error) {
      console.error("Error toggling map style:", error)
      isSatelliteView.value = !isSatelliteView.value
    }
  }

  // Mapbox no detecta por sí solo el cambio de ancho del contenedor
  async function resize() {
    await nextTick()
    map.value?.resize()
  }

  onMounted(initializeMap)

  return {
    location_type_full,
    isSatelliteView,
    toggleMapStyle,
    resize,
  }
}
