// components/map/useMapClusters.js
import mapboxgl from 'mapbox-gl';
import * as d3 from 'd3';
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";

export function useMapClusters(map) {
  const mainStore = useMainStore();
  const { cats } = storeToRefs(mainStore);
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
    const donutDiv = document.createElement('div');

    // Create SVG using D3
    const svg = d3.select(donutDiv)
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

    return donutDiv;
  }

  function setupClusterMarkers(selectedExtractivismTypes, extractivism_type_props) {
    const markers = {};
    let markersOnScreen = {};

    map.value.on('render', () => {
      if (!map.value.isSourceLoaded('proyectos'))
        return;
      updateMarkers();
      // const select_all = selectedExtractivismTypes.value.length === 0;
      // if (select_all)
      // else{
      //   console.log("no hay markers por filtro");
      // }
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
          const el = createDonutChart(props, extractivism_type_props.value);
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

  return {
    setupClusterMarkers
  }
}