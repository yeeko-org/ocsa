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
// de Mapbox (que también se levanta el alto del reposo en pages/mapa.vue),
// con 10 px de aire sobre su botón «i». En teléfono mide 48 px, el blanco
// táctil mínimo del skill map-mobile-ux.
const phoneBottom = `${Number.parseInt(SHEET_REST_PX, 10) + 44}px`
</script>

<template>
  <v-btn
    class="map-layer-switch"
    :class="smAndDown ? 'map-layer-switch--phone' : 'map-layer-switch--desktop'"
    icon
    variant="elevated"
    :size="smAndDown ? 'default' : 'small'"
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
  /* 10 px (el margen de Mapbox entre controles) sobre el NavigationControl
     de abajo-izquierda, que es solo zoom: logo + atribución + zoom suman
     117 px desde el borde. Si cambia esa pila, hay que recalibrar. */
  bottom: 127px;
  left: 10px;
}

.map-layer-switch--phone {
  bottom: v-bind(phoneBottom);
  right: 10px;
}
</style>
