<script setup>
import { useDisplay } from 'vuetify'
import { useMapStore } from '~/store/map.js'

// Franja de cápsulas de filtros activos (decisions §4.3). Vive separada de
// los controles, sobre el mapa. Cerrar una cápsula quita ese valor; hacer
// clic en su cuerpo reabre el picker que la originó (§4.4). Al final,
// "limpiar todo" vacía todos los filtros de golpe (§4).
// El extractivismo NO aparece aquí: tiene su propia tira de chips (§5).
const { mobile } = useDisplay()
const mapStore = useMapStore()

// Qué picker reabrir desde una cápsula. Posiciones, sub-posiciones y
// actores cuelgan del grupo de actores; el purpose, del picker legal.
function pickerKeyFor(cap) {
  if (['actors', 'positions', 'positionTypes'].includes(cap.filterKey))
    return 'actors'
  if (cap.filterKey === 'legalPurpose') return 'legal'
  return cap.filterKey
}
</script>

<template>
  <client-only>
    <v-sheet
      v-if="mapStore.activeCapsules.length"
      :class="['map-capsules', mobile ? 'capsules-mobile' : 'capsules-desktop']"
      color="#FFFFFFE6"
      rounded="lg"
      elevation="4"
    >
      <v-chip
        v-for="cap in mapStore.activeCapsules"
        :key="`${cap.filterKey}-${cap.groupId ?? ''}-${cap.value}`"
        size="small"
        closable
        class="ma-1"
        @click="mapStore.activePickerKey = pickerKeyFor(cap)"
        @click:close="mapStore.removeCapsule(cap)"
      >
        {{ cap.label }}
      </v-chip>

      <v-btn
        variant="text"
        size="small"
        color="error"
        class="ma-1 flex-shrink-0"
        prepend-icon="filter_alt_off"
        @click="mapStore.clearAllFilters()"
      >
        Limpiar todo
      </v-btn>
    </v-sheet>
  </client-only>
</template>

<style scoped>
.map-capsules {
  position: absolute;
  z-index: 2;
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  overflow-x: auto;
  padding: 2px 4px;
}

/* Escritorio: banda bajo la leyenda de extractivismo, librando el rail. */
.capsules-desktop {
  top: 112px;
  left: 64px;
  right: 56px;
}

/* Móvil: bajo la tira de íconos. `top` tentativo (encaje fino → Sesión 5). */
.capsules-mobile {
  top: 160px;
  left: 8px;
  right: 8px;
}
</style>
