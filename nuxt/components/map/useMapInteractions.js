// components/map/useMapInteractions.js
import mapboxgl from 'mapbox-gl';
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";

export function setupInteractions(map, buildFullProjectData) {
  const mainStore = useMainStore()
  const {
    cats, geometry_types, megaproject_types_dict } = storeToRefs(mainStore)
  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false,
    anchor: 'top'
  });

  geometry_types.value.forEach(gt => {
    map.value.on('click', gt.main_layer, (e) => {
      console.log('Feature clicked:', e.features[0]);
      buildFullProjectData(e.features[0].properties);
    });
    if (gt.type === "Point") return;
    map.value.on('mouseenter', gt.main_layer, () => {
      map.value.getCanvas().style.cursor = 'pointer';
    });
    map.value.on('mouseleave', gt.main_layer, () => {
      map.value.getCanvas().style.cursor = '';
    });
  });

  map.value.on('mouseenter', 'unclustered-point', (e) => {
    map.value.getCanvas().style.cursor = 'pointer';
    // console.log('Feature hovered:', e);
    const props = e.features[0].properties;
    // console.log("props:", props);
    const projectData = JSON.parse(props.project);
    const extractivism_types = JSON.parse(props.extractivism_types);
    const megaproject_type = megaproject_types_dict.value[
      projectData.megaproject_type];
    // console.log('Project data:', projectData);
    // console.log('cats.extractivism_type', cats.value.extractivism_type);
    // console.log("extractivism_types:", extractivism_types);
    const coordinates = e.features[0].geometry.coordinates.slice();
    let description = `
      <div class="font-weight-bold mb-2">
        ${projectData.name || 'Proyecto sin nombre'}
      </div>
      <div class="mb-1">
        <div class="text-caption text-grey-darken-1">
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
              class="material-icons notranslate"
              style="font-size: 14px;
              vertical-align: middle;"
            >
              ${et_obj.icon}
            </i>
            <span style="vertical-align: middle;">

              ${et_obj.short_name || et_obj.name}
            </span>
          </div>
        `;
      }
    });
    description += `
      <div class="mt-2 font-caption text-grey">
        (Dale click para ver más detalles)
      </div>
    `;

    popup.setLngLat(coordinates).setHTML(description).addTo(map.value);
  });

  map.value.on('mouseleave', 'unclustered-point', () => {
    map.value.getCanvas().style.cursor = '';
    popup.remove();
  });
}