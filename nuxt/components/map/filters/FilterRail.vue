<script setup>
import { computed } from 'vue'
import { useDisplay } from 'vuetify'
import { useMapStore } from '~/store/map.js'
import FilterPicker from '~/components/map/filters/FilterPicker.vue'
import FilterActors from '~/components/map/filters/custom/FilterActors.vue'

// Rail de íconos de filtro (decisions §4, Capa A): columna delgada siempre
// visible — botón menu + 8 íconos (uno por rail-group) + zona inferior de
// acciones. El botón menu expande/colapsa el rail mostrando los nombres
// (Capa C); al expandirse, los chips se desplazan a la derecha.
const { smAndDown } = useDisplay()
const mapStore = useMapStore()

// Grupos resueltos (label/icon heredados) en el orden del registro.
const groups = computed(() =>
  mapStore.FILTER_REGISTRY.map(g => mapStore.resolveGroup(g.id)))

function openPicker(id) {
  mapStore.activePickerKey = id
}

// Click fuera del rail → colapsa la expansión (si estaba abierta).
function collapseRail() {
  if (mapStore.railExpanded) mapStore.railExpanded = false
}
</script>

<template>
  <client-only>
    <v-sheet
      v-click-outside="collapseRail"
      :class="smAndDown ? 'rail-horizontal' : 'rail-vertical'"
      class="map-rail pa-1 d-flex ga-2 align-center"
      color="#FFFFFFA9"
      rounded="lg"
      elevation="4"
    >
      <!-- Botón menu → expande/colapsa el rail (Capa C). -->
      <div class="rail-item d-flex align-center">
        <v-btn
          icon="menu"
          variant="text"
          size="large"
          :active="mapStore.railExpanded"
          @click="mapStore.toggleRailExpanded()"
        />
        <v-tooltip
          activator="parent"
          text="Filtrar proyectos por..."
          location="end"
        />
      </div>

      <!-- Íconos de filtro (Capa A): actores tiene su propio componente. Con el
           rail expandido, cada ícono muestra su nombre al lado. -->
      <div
        v-for="g in groups"
        :key="g.id"
        class="rail-item d-flex align-center"
      >
        <FilterActors v-if="g.id === 'actors'"/>
        <FilterPicker v-else :group="g.id"/>
        <v-expand-x-transition>
          <span
            v-if="mapStore.railExpanded"
            class="rail-label cursor-pointer"
            @click="openPicker(g.id)"
          >
            {{ g.label }}
          </span>
        </v-expand-x-transition>
      </div>

      <!-- Zona de acciones: limpiar + comprimir. Botones `flat` (sólidos) para
           diferenciarlos de los íconos de filtro (text/tonal). -->
      <template v-if="mapStore.hasActiveFilters">
        <v-divider class="my-2 align-self-stretch"/>
        <v-expand-x-transition>
          <div
            v-if="mapStore.railExpanded"
            class="text-label-small text-medium-emphasis px-2 text-no-wrap"
          >
            Acciones
          </div>
        </v-expand-x-transition>

        <div class="rail-item d-flex align-center">
          <v-btn
            icon="filter_alt_off"
            variant="outlined"
            color="error"
            @click="mapStore.clearAllFilters()"
          />
          <v-expand-x-transition>
            <span
              v-if="mapStore.railExpanded"
              class="rail-label cursor-pointer"
              @click="mapStore.clearAllFilters()"
            >
              Limpiar filtros
            </span>
          </v-expand-x-transition>
          <v-tooltip
            v-if="!mapStore.railExpanded"
            activator="parent"
            text="Limpiar filtros"
            location="end"
          />
        </div>

        <div
          v-if="mapStore.anyAdjacentChips"
          class="rail-item d-flex align-center"
        >
          <v-btn
            :icon="mapStore.chipsCompact ? 'unfold_more' : 'unfold_less'"
            variant="flat"
            color="blue-grey"
            size="large"
            :active="mapStore.chipsCompact"
            @click="mapStore.toggleChipsCompact()"
          />
          <v-expand-x-transition>
            <span
              v-if="mapStore.railExpanded"
              class="rail-label cursor-pointer"
              @click="mapStore.toggleChipsCompact()"
            >
              {{ mapStore.chipsCompact ? 'Expandir etiquetas' : 'Comprimir etiquetas' }}
            </span>
          </v-expand-x-transition>
          <v-tooltip
            v-if="!mapStore.railExpanded"
            activator="parent"
            :text="mapStore.chipsCompact ? 'Expandir etiquetas' : 'Comprimir etiquetas'"
            location="end"
          />
        </div>
      </template>
    </v-sheet>
  </client-only>
</template>

<style scoped>
.map-rail {
  position: absolute;
  z-index: 2;
  /* Glassmorphism: fondo blanco ~85 % + desenfoque del mapa detrás. */
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

/* Escritorio: columna vertical en el borde izquierdo, bajo la barra superior.
   El ancho crece solo (las labels usan v-expand-x-transition). */
.rail-vertical {
  left: 8px;
  top: 76px;
  flex-direction: column;
  align-items: flex-start;
}

/* Etiqueta del rail expandido: separada del ícono, legible. */
.rail-label {
  margin-inline-start: 6px;
  padding-inline-end: 12px;
  font-size: 0.95rem;
  font-weight: 500;
  white-space: nowrap;
  color: rgba(0, 0, 0, 0.82);
}

/* En vertical, cada fila ícono+label ocupa el ancho (íconos alineados a la
   izquierda). En horizontal (móvil) se mantienen al tamaño del ícono. */
.rail-vertical .rail-item {
  width: 100%;
}

/* Móvil: tira horizontal arriba. */
.rail-horizontal {
  left: 8px;
  right: 8px;
  top: 112px;
  flex-direction: row;
  align-items: center;
  gap: 4px;
  overflow-x: auto;
}
</style>
