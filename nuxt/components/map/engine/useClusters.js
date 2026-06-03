// components/map/useClusters.js
import mapboxgl from 'mapbox-gl';
import * as d3 from 'd3';
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {useMapStore} from "~/store/map.js";

export function useClusters(map) {
  const mainStore = useMainStore();
  const { cats } = storeToRefs(mainStore);
  const mapStore = useMapStore();

  // Create a specific popup instance for clusters
  const clusterPopup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false,
    anchor: 'top',
    maxWidth: '300px',
    offset: 15 // Offset to avoid covering the cluster
  });

  const r_scale = d3.scalePow().exponent(1 / 3)
    .domain([2,300])
    .range([15,32]);

  const font_scale = d3.scalePow().exponent(1 / 3)
    .domain([2,300])
    .range([12,16]);

  function createDonutChart(props, extractivism_type_props) {
    // console.log("Creating donut chart for cluster:", props);
    // Prepare data

    const et_props = extractivism_type_props;
    let counts = et_props.ids.map(et_id => props[`sum_${et_id}`] || 0);

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

    const donutDiv = document.createElement('div');
    // Add a class for easier CSS targeting if needed
    donutDiv.className = 'cluster-marker';

    const svg = d3.select(donutDiv)
      .append('svg')
      .attr('width', w)
      .attr('height', w)
      .attr('viewBox', `-1 -1 ${w + 2} ${w + 2}`)
      .attr('text-anchor', 'middle')
      .style('font', `${fontSize}px sans-serif`)
      .style('display', 'block');

    const pie = d3.pie()
      .sort(null)
      .value(d => d);

    const g = svg.append('g')
      .attr('transform', `translate(${r}, ${r})`);

    if (!only_one) {
      const arc = d3.arc()
        .innerRadius(r0)
        .outerRadius(r);

      g.selectAll('path')
        .data(pie(counts))
        .enter()
        .append('path')
        .attr('d', arc)
        .attr('fill', (d, i) => et_props.colors[i])
        // Optional: internal hover effect on segments
        .on('mouseenter', function(event, d) {
            d3.select(this).attr('opacity', 0.7);
        })
        .on('mouseleave', function(event, d) {
            d3.select(this).attr('opacity', 1);
        });
    }

    g.append('circle')
      .attr('r', r0)
      .attr('fill', only_one && unique_et_full ? unique_et_full.color : '#ffffff');

    g.append('text')
      .attr('dominant-baseline', 'central')
      .text(props.point_count)
      .attr('fill', only_one && unique_et_full ? '#ffffff' : '#000000')
      .attr('style', only_one && unique_et_full ? 'text-shadow: 1px 1px 3px #000000;' : '');

    return donutDiv;
  }

  function setupClusterMarkers() {
    const markers = {};
    let markersOnScreen = {};

    // ID del cluster actualmente bajo el cursor. Sirve como "token de
    // validez" para descartar resultados asíncronos obsoletos y para
    // saber si el marcador que se va a destruir es el que tiene popup.
    const hoveredClusterId = ref(null);

    function closeClusterPopup() {
      hoveredClusterId.value = null;
      clusterPopup.remove();
    }

    // Punto 5 (defensivo): cualquier movimiento/zoom del mapa cierra el
    // popup, por si algún caso límite se escapa de los handlers del DOM.
    map.value.on('movestart', closeClusterPopup);
    map.value.on('zoomstart', closeClusterPopup);

    map.value.on('render', () => {
      if (!map.value.isSourceLoaded('proyectos'))
        return;
      updateMarkers();
    });

    function updateMarkers() {
      const newMarkers = {};
      const features = map.value.querySourceFeatures('proyectos');

      for (const feature of features) {
        const coords = feature.geometry.coordinates;
        const props = feature.properties;
        if (!props.cluster) continue;
        const id = props.cluster_id;

        let marker = markers[id];
        if (!marker) {
          const el = createDonutChart(props, mapStore.extractivismTypeProps);

          // ---------------------------------------------------------
          // 1. INTERACTION: CLICK TO ZOOM
          // ---------------------------------------------------------
          el.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent clicking through to the map

            const source = map.value.getSource('proyectos');

            source.getClusterExpansionZoom(id, (err, zoom) => {
              if (err) return;
              // console.log("Zooming to cluster:", id, "at zoom level:", zoom);
              const final_zoom = Math.max(zoom + 1, 8);

              clusterPopup.remove();
              map.value.easeTo({
                center: coords,
                // zoom: zoom,
                zoom: final_zoom,
                duration: 500 // Smooth animation
              });
            });
          });

          // ---------------------------------------------------------
          // 2. INTERACTION: HOVER POPUP
          // ---------------------------------------------------------
          el.addEventListener('mouseenter', () => {
             el.style.cursor = 'pointer';
             hoveredClusterId.value = id;

             // Fetch the "leaves" (individual points) inside this cluster
             // We limit to 10 items to keep the popup manageable
             const source = map.value.getSource('proyectos');

             source.getClusterLeaves(id, 10, 0, (err, leaves) => {
               if (err) return;

               // Guard: si el mouse ya salió (o entró a otro cluster)
               // antes de que resolviera esta llamada asíncrona, no
               // mostramos un popup obsoleto.
               if (hoveredClusterId.value !== id) return;

               // Build HTML for the list of projects
               let description = `
                 <div class="font-weight-bold mb-2 border-b pb-1">
                   ${props.point_count} Proyectos:
                 </div>
                 <div style="max-height: 200px; overflow-y: auto;">
               `;

               leaves.forEach(leaf => {
                 // Parse JSON just like in useMapInteractions
                 const projectData = typeof leaf.properties.project === 'string'
                    ? JSON.parse(leaf.properties.project)
                    : leaf.properties.project;

                 description += `
                   <div class="mb-1 text-body-small d-flex align-center">
                     <span class="mr-1">•</span>
                     <span>${projectData.name}</span>
                   </div>
                 `;
               });

               if (props.point_count > 10) {
                 description += `
                   <div class="text-body-small text-grey mt-2 font-italic">
                     ... y ${props.point_count - 10} más.
                   </div>
                   <div class="text-body-small text-blue font-weight-bold mt-1">
                     (Haz clic para acercar)
                   </div>
                 `;
               } else {
                 description += `</div>`;
               }

               // Show the popup
               clusterPopup
                 .setLngLat(coords)
                 .setHTML(description)
                 .addTo(map.value);
             });
          });

          el.addEventListener('mouseleave', () => {
            el.style.cursor = '';
            closeClusterPopup();
          });

          // Create the marker with the element
          marker = markers[id] = new mapboxgl.Marker({
              element: el
          }).setLngLat(coords);
        }
        newMarkers[id] = marker;

        if (!markersOnScreen[id])
          marker.addTo(map.value);
      }

      for (const id in markersOnScreen) {
        if (!newMarkers[id]) {
          // Si el marcador que se destruye es el que está en hover,
          // quitar el nodo del DOM no dispara su 'mouseleave', así que
          // cerramos el popup manualmente para que no quede colgado.
          // (id de markersOnScreen es string; cluster_id es número)
          if (hoveredClusterId.value !== null &&
              String(hoveredClusterId.value) === id)
            closeClusterPopup();
          markersOnScreen[id].remove();
        }
      }
      markersOnScreen = newMarkers;
    }
  }

  return {
    setupClusterMarkers
  }
}