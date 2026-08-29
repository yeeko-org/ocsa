const API_URL = 'space_time'

async function handleRequest(requestFunc) {
  try {
    return await requestFunc();
  } catch (error) {
    console.error('Error in geoService:', error);
    return {
      success: false,
      error: error.message || 'An error occurred'
    };
  }
}

async function getMunicipalities(state_id) {
  const { $api } = useNuxtApp()
  return await handleRequest(() => $api.get(
    `${API_URL}/state/${state_id}/`));
}

async function getLocalities(municipality_id) {
  const { $api } = useNuxtApp()
  return await handleRequest(() => $api.get(
    `${API_URL}/municipality/${municipality_id}/`)
  );
}

// Único endpoint fuera de `API_URL`: cuelga del router de Location
async function geolocate(lat, lon, state_id = null) {
  const { $api } = useNuxtApp()
  const params = state_id ? { lat, lon, state: state_id } : { lat, lon }
  return await handleRequest(() => $api.get(
    '/location/geolocate/', { params })
  );
}

// Las líneas y polígonos no caben en la query string: mismo endpoint que
// `geolocate`, pero con la geometría en el cuerpo.
async function geolocateGeometry(feature, state_id = null) {
  const { $api } = useNuxtApp()
  return await handleRequest(() => $api.post(
    '/location/geolocate/', { geojson: feature, state: state_id })
  );
}

export const geoService = {
  getMunicipalities,
  getLocalities,
  geolocate,
  geolocateGeometry,
}
