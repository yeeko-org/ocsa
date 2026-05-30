<script setup>
// Stub (Sesión 1): reserva el espacio del cambio de capa satélite/mapa.
// La implementación real (map.setStyle) llega en la Sesión 5.
function notImplementedYet() {
  // Placeholder: aún sin lógica de cambio de estilo.
}
</script>

<template>
  <v-btn
    class="map-layer-switch"
    icon="layers"
    variant="elevated"
    size="small"
    @click="notImplementedYet"
  >
    <v-icon>layers</v-icon>
    <v-tooltip activator="parent" location="start">
      Cambiar vista satélite / mapa (próximamente)
    </v-tooltip>
  </v-btn>
</template>

<style scoped>
.map-layer-switch {
  position: absolute;
  bottom: 170px; /* por encima del NavigationControl (abajo-derecha) */
  right: 10px;
  z-index: 3;
}
</style>
