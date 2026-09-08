<script setup>
import { useDisplay } from 'vuetify'
import { SHEET_REST_PX } from '~/store/map.js'

// Botón flotante que alterna entre el estilo "mapa" y "satélite".
defineProps({
  is_satellite: { type: Boolean, default: false },
  is_switching: { type: Boolean, default: false }
});
const emit = defineEmits(['toggle']);
const { smAndDown } = useDisplay()

// Teléfono: abajo-derecha, sobre el sheet en reposo y sobre la atribución
// de Mapbox (que también se levanta el alto del reposo en pages/mapa.vue).
const phoneBottom = `${Number.parseInt(SHEET_REST_PX, 10) + 36}px`
</script>

<template>
  <v-btn
    class="map-layer-switch"
    :class="smAndDown ? 'map-layer-switch--phone' : 'map-layer-switch--desktop'"
    icon
    variant="elevated"
    size="small"
    :loading="is_switching"
    :disabled="is_switching"
    :aria-label="is_satellite ? 'Ver mapa' : 'Ver satélite'"
    @click="emit('toggle')"
  >
    <v-icon>{{ is_satellite ? 'map' : 'satellite_alt' }}</v-icon>
    <v-tooltip v-if="!smAndDown" activator="parent" location="end">
      {{ is_satellite ? 'Ver mapa' : 'Ver satélite' }}
    </v-tooltip>
  </v-btn>
</template>

<style scoped>
.map-layer-switch {
  position: absolute;
  z-index: 3;
}

.map-layer-switch--desktop {
  bottom: 170px; /* por encima del NavigationControl (abajo-izquierda) */
  left: 10px;
}

.map-layer-switch--phone {
  bottom: v-bind(phoneBottom);
  right: 10px;
}
</style>
