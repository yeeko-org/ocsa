import mapboxgl from 'mapbox-gl';
import { useMainStore } from "~/store/index.js";
import { useMapStore } from "~/store/map.js";
import {storeToRefs} from "pinia";
import { GEOMETRY_TYPES } from "~/composables/location_types.js";

export function setupInteractions(map) {
  const mainStore = useMainStore()
  const { targetProjectId } = storeToRefs(useMapStore())
  const {cats, megaproject_types_dict } = storeToRefs(mainStore)

  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false,
    anchor: 'top'
  });

  // Arma el HTML del tooltip a partir de las properties de una feature.
  // Fuente única para puntos, líneas y polígonos.
  function buildPopupHTML(props) {
    const projectData = JSON.parse(props.project);
    const extractivism_types = JSON.parse(props.extractivism_types);
    const megaproject_type = megaproject_types_dict.value[
      projectData.megaproject_type];
    let description = `
      <div class="font-weight-bold mb-2">
        ${projectData.name || 'Proyecto sin nombre'}
      </div>
      <div class="mb-1">
        <div class="text-body-small text-grey-darken-1">
          Tipo de megaproyecto:
        </div>
        <span class="font-weight-bold">
          ${megaproject_type ? megaproject_type.name : 'N/A'}
        </span>
      </div>
    `;
    extractivism_types.forEach(et_id => {
      const et_obj = cats.value.extractivism_type.find(
        et => et.id === et_id);
      if (et_obj) {
        description += `
          <div
            style="
              display: inline-block;
              background-color: ${et_obj.color}C9;
              color: #FFFFFF;
              padding: 2px 10px;
              border-radius: 20px;
              font-size: 12px;
              margin-right: 4px;
              margin-bottom: 4px;
            "
          >
            <i
              class="material-symbols-outlined notranslate"
              style="font-size: 14px;
              vertical-align: middle;"
            >${et_obj.icon}</i>
            <span style="vertical-align: middle;">${et_obj.short_name || et_obj.name}</span>
          </div>
        `;
      }
    });
    description += `
      <div class="mt-2 font-caption text-grey">
        (Da clic para ver sus detalles)
      </div>
    `;
    return description;
  }

  // Click: abre el detalle del proyecto. Aplica a la geometría principal de
  // cada tipo y al ícono de las líneas (para que dar clic en el ícono también
  // abra el detalle).
  const clickLayers = [
    ...GEOMETRY_TYPES.map(gt => gt.main_layer),
    'proyectos-lineas-icon'
  ];
  clickLayers.forEach(layerId => {
    map.value.on('click', layerId, (e) => {
      // Fuente de verdad: el panel observa targetProjectId y arma el detalle
      const props = e.features[0].properties;
      const project = typeof props.project === 'string'
        ? JSON.parse(props.project)
        : props.project;
      targetProjectId.value = project.id;
    });
  });

  // Hover del punto: el popup se ancla en la coordenada exacta de la feature.
  map.value.on('mouseenter', 'unclustered-point', (e) => {
    map.value.getCanvas().style.cursor = 'pointer';
    const coordinates = e.features[0].geometry.coordinates.slice();
    popup.setLngLat(coordinates)
      .setHTML(buildPopupHTML(e.features[0].properties))
      .addTo(map.value);
  });
  map.value.on('mouseleave', 'unclustered-point', () => {
    map.value.getCanvas().style.cursor = '';
    popup.remove();
  });

  // Hover de líneas y polígonos: no tienen una coordenada única, así que el
  // popup sigue al cursor con mousemove. Se incluye el ícono de la línea para
  // que sirva como blanco más grande que el trazo (2.5px).
  const hoverFollowLayers = [
    'proyectos-lineas',
    'proyectos-lineas-icon',
    'proyectos-poligonos-fill'
  ];
  hoverFollowLayers.forEach(layerId => {
    map.value.on('mousemove', layerId, (e) => {
      map.value.getCanvas().style.cursor = 'pointer';
      popup.setLngLat(e.lngLat)
        .setHTML(buildPopupHTML(e.features[0].properties))
        .addTo(map.value);
    });
    map.value.on('mouseleave', layerId, () => {
      map.value.getCanvas().style.cursor = '';
      popup.remove();
    });
  });
}