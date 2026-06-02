<script setup>
// Botón flotante que alterna entre el estilo "mapa" y "satélite".
defineProps({
  is_satellite: { type: Boolean, default: false },
  is_switching: { type: Boolean, default: false }
});
const emit = defineEmits(['toggle']);
</script>

<template>
  <v-btn
    class="map-layer-switch"
    icon
    variant="elevated"
    size="small"
    :loading="is_switching"
    :disabled="is_switching"
    @click="emit('toggle')"
  >
    <v-icon>{{ is_satellite ? 'map' : 'satellite_alt' }}</v-icon>
    <v-tooltip activator="parent" location="end">
      {{ is_satellite ? 'Ver mapa' : 'Ver satélite' }}
    </v-tooltip>
  </v-btn>
</template>

<style scoped>
.map-layer-switch {
  position: absolute;
  bottom: 170px; /* por encima del NavigationControl (abajo-izquierda) */
  left: 10px;
  z-index: 3;
}
</style>
