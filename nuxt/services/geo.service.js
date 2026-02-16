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

export const geoService = {
  getMunicipalities,
  getLocalities,
}
