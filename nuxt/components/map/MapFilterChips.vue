<script setup>
import { computed } from 'vue'
import { useDisplay } from 'vuetify'
import { useMapStore } from '~/store/map.js'
import { RAIL_GEOMETRY } from '~/components/map/filterRegistry.js'
import ExtractivismIcons from '~/components/dashboard/project/ExtractivismIcons.vue'

// Filas de chips de filtros activos (decisions §4.3, Capa B): a la derecha del
// rail, una banda por rail-group alineada a su ícono. Cada grupo expone
// `blocks` (uno normalmente; dos en Actores). Cada bloque se dibuja como una
// cuadrícula adaptativa de 2 columnas (regla gradual en `gridRows`) limitada a
// `maxCells`. En modo comprimido cada grupo colapsa a un chip "{n} filtros".
const { smAndDown } = useDisplay()
const mapStore = useMapStore()

const rows = computed(() => mapStore.capsulesByGroup)
const chipCount = group => group.blocks.reduce((n, b) => n + b.length, 0)

// Desplazamiento: los chips se corren a la derecha cuando el rail se expande.
const chipsLeft = computed(() =>
  RAIL_GEOMETRY.chipsLeft +
  (mapStore.railExpanded ? RAIL_GEOMETRY.expandedExtra : 4) + 'px')

// Cuadrícula adaptativa de un bloque → array de filas (cada fila = 1-2 celdas).
// Celda = chip normal o celda de overflow ({ overflow, hidden }).
function gridRows(block, maxCells) {
  const n = block.length
  if (n === 0) return []
  if (n === 1) return [[block[0]]]
  if (n === 2) return [[block[0]], [block[1]]]
  let cells
  if (n <= maxCells) {
    cells = block.slice()
  } else {
    cells = block.slice(0, maxCells - 1)
    cells.push({ overflow: n - (maxCells - 1), hidden: block.slice(maxCells - 1) })
  }
  const result = []
  for (let i = 0; i < cells.length; i += 2) result.push(cells.slice(i, i + 2))
  return result
}

function openPicker(id) {
  mapStore.activePickerKey = id
}
</script>

<template>
  <client-only>
    <!-- En móvil el layout cambia (Sesión 5); por ahora solo escritorio. -->
    <div
      v-if="!smAndDown"
      class="map-chips d-flex flex-column"
      :style="{ left: chipsLeft }"
    >
      <div
        v-for="group in rows"
        :key="group.id"
        class="chip-group d-flex flex-column justify-center"
      >
        <!-- Modo comprimido: un solo chip "{n} filtros" por grupo (solo si hay
             más de uno; los de 1 chip se muestran tal cual abajo). -->
        <template v-if="mapStore.chipsCompact && chipCount(group) > 1">
          <v-chip
            size="small"
            variant="tonal"
            :color="group.color"
            class="cursor-pointer align-self-start"
            @click="openPicker(group.id)"
          >
            <v-icon
              v-if="group.icon"
              :icon="group.icon"
              size="small"
              class="mr-1"
            />
            {{ chipCount(group) }} filtros
          </v-chip>
        </template>

        <!-- Modo normal: bloques → cuadrícula adaptativa. -->
        <template v-else>
          <div v-for="(block, bi) in group.blocks" :key="bi" class="chip-block">
            <div
              v-for="(line, li) in gridRows(block, group.maxCells)"
              :key="li"
              class="chip-line d-flex"
            >
              <template v-for="(cell, ci) in line" :key="ci">
                <!-- Chip normal -->
                <v-chip
                  v-if="!cell.overflow"
                  :key="`${cell.stateKey}-${cell.value}`"
                  size="small"
                  variant="tonal"
                  base-color="white"
                  :color="cell.color"
                  close-icon="clear"
                  closable
                  class="cursor-pointer special-chip"
                  @click="openPicker(group.id)"
                  @click:close="mapStore.removeCapsule(cell)"
                >
                  <ExtractivismIcons
                    v-if="cell.kind === 'megaproject'"
                    :megaproject_type="{ id: cell.value }"
                    small_icons
                    class="mr-1"
                  />
                  <v-icon
                    v-else-if="cell.icon"
                    :icon="cell.icon"
                    size="small"
                    class="mr-1"
                  />
                  {{ cell.label }}
                  <v-tooltip activator="parent" location="top" :max-width="320">
                    <div class="font-weight-bold">{{ cell.full }}</div>
                    <div v-if="cell.description">{{ cell.description }}</div>
                  </v-tooltip>
                </v-chip>

                <!-- Celda de overflow "+N" con el resto en el tooltip. -->
                <v-chip
                  v-else
                  size="small"
                  variant="tonal"
                  :color="group.color"
                  class="cursor-pointer"
                  @click="openPicker(group.id)"
                >
                  +{{ cell.overflow }}
                  <v-tooltip activator="parent" location="top" :max-width="320">
                    <div
                      v-for="c in cell.hidden"
                      :key="`${c.stateKey}-${c.value}`"
                      class="font-weight-medium"
                    >
                      {{ c.full }}
                    </div>
                  </v-tooltip>
                </v-chip>
              </template>
            </div>
          </div>
        </template>
      </div>
    </div>
  </client-only>
</template>

<style scoped>
/* Capa B: columna de bandas alineadas a los íconos del rail. `pointer-events`
   en none para no bloquear el mapa; los chips lo reactivan. `left` se anima
   junto con la expansión del rail. */
.map-chips {
  position: absolute;
  z-index: 2;
  top: v-bind('RAIL_GEOMETRY.chipsTop + "px"');
  pointer-events: none;
  transition: left 0.25s ease;
  row-gap: 8px;
}

.map-chips :deep(.v-chip) {
  pointer-events: auto;
}

/* Cada grupo ocupa al menos la banda de un ícono (pitch del rail) y centra su
   contenido; crece si el bloque tiene más filas (estados 2×4, actores 2 bloques).
   El encaje fino chips↔íconos lo afina Ricardo en otra sesión. */
.chip-group {
  min-height: v-bind('RAIL_GEOMETRY.rowH + "px"');
}

.chip-line {
  gap: 4px;
  margin-bottom: 4px;
}

.chip-line:last-child {
  margin-bottom: 0;
}

.special-chip .v-chip__underlay {
  opacity: 0.6 !important;
  backdrop-filter: blur(2px);
   -webkit-backdrop-filter: blur(2px);
  background-color: rgba(0, 150, 136, 0.2);
}
</style>
