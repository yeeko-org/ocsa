// components/map/useMapStyle.js
// Estilos Mapbox custom de OCSA y la mecánica para alternar entre ellos.
// Centraliza las dos URLs (antes duplicadas en mapa.vue y LocationMapDialog)
// y el patrón setStyle → reconstruir capas en 'style.load'.

// Estilo "mapa": base custom con el sprite de pines (*-pin) de extractivismo.
export const MAP_STYLE =
  'mapbox://styles/rickrebel/cm6ls9un800kr01qqdu1g48nq';
// Estilo "satélite": imágenes + calles; debe traer el mismo sprite de pines
// (añadido en Studio) para que los proyectos se vean igual que en el mapa.
export const SATELLITE_STYLE =
  'mapbox://styles/rickrebel/cm83y5cbp004301s5861t18gi';

/**
 * Alterna el estilo del mapa entre `MAP_STYLE` y `SATELLITE_STYLE`.
 * `setStyle` descarta las sources/layers custom, así que tras el cambio se
 * dispara `onStyleReload` para que el llamador las reconstruya.
 *
 * @param {import('vue').Ref} map  ref a la instancia mapboxgl.Map
 * @param {{ onStyleReload?: () => void }} [options]
 * @returns {{ isSatelliteView: import('vue').Ref<boolean>,
 *             toggleMapStyle: () => void }}
 */
export function useMapStyle(map, { onStyleReload } = {}) {
  // Arranca en "mapa"; el satélite es opt-in.
  const isSatelliteView = ref(false);
  // Bloquea reentradas mientras el nuevo estilo termina de cargar.
  const isSwitching = ref(false);

  function toggleMapStyle() {
    if (!map.value || isSwitching.value) return;
    isSwitching.value = true;
    isSatelliteView.value = !isSatelliteView.value;
    const newStyle = isSatelliteView.value ? SATELLITE_STYLE : MAP_STYLE;

    map.value.setStyle(newStyle);
    map.value.once('style.load', () => {
      if (onStyleReload) onStyleReload();
      isSwitching.value = false;
    });
  }

  return { isSatelliteView, isSwitching, toggleMapStyle };
}