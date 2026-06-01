<script setup>
import { computed } from 'vue'
import { useDisplay } from 'vuetify'
import { VMenu, VBottomSheet } from 'vuetify/components'
import { useMapStore } from '~/store/map.js'

// Grupo de actores del rail (decisions §10): dos controles en un popover.
//  1. Autocomplete por nombre de actor → en STUB esta sesión (los actores
//     viven en la colección /actor/, no en cats; el fetch real es Sesión 4).
//  2. Posiciones (ParticipantGroup) como chips toggle; al activar una
//     posición despliega sus sub-posiciones (ParticipantType del grupo).
 const { smAndDown } = useDisplay()
const mapStore = useMapStore()

const isOpen = computed({
  get: () => mapStore.activePickerKey === 'actors',
  set: v => { mapStore.activePickerKey = v ? 'actors' : null },
})

// Badge ● si hay cualquier criterio de actor activo.
const hasSelection = computed(() =>
  mapStore.filters.actors.length > 0 ||
  mapStore.filters.positions.length > 0 ||
  Object.values(mapStore.filters.positionTypes).some(ids => ids?.length))

const titleOf = o => o.short_name || o.name
</script>

<template>
  <component
    :is="smAndDown ? VBottomSheet : VMenu"
    v-model="isOpen"
    :close-on-content-click="false"
    location="end"
    :offset="8"
  >
    <template #activator="{ props: actProps }">
      <div class="rail-btn">
        <v-badge
          :model-value="hasSelection"
          dot
          color="primary"
          offset-x="6"
          offset-y="6"
        >
          <v-btn
            icon="groups"
            :color="isOpen ? 'primary' : undefined"
            variant="text"
            density="comfortable"
            v-bind="actProps"
          />
        </v-badge>
        <v-tooltip activator="parent" text="Actores y posiciones" location="end"/>
      </div>
    </template>

    <v-card min-width="300" max-width="380" class="pa-2">
      <div class="text-subtitle-2 font-weight-medium px-2 pt-1 pb-2">
        Actores y posiciones
      </div>

      <!-- 1. Autocomplete de actor por nombre (stub hasta Sesión 4). -->
      <v-autocomplete
        :items="[]"
        label="Buscar actor por nombre"
        density="compact"
        variant="outlined"
        hide-details
        no-filter
        class="mx-2 mb-3"
      >
        <template #no-data>
          <div class="text-caption text-medium-emphasis pa-3">
            La búsqueda de actores se conecta al backend en una próxima fase.
          </div>
        </template>
      </v-autocomplete>

      <!-- 2. Posiciones: chips toggle (siempre seleccionables). -->
      <div class="text-overline px-2">Posiciones</div>
      <v-chip-group
        v-model="mapStore.filters.positions"
        multiple
        column
        class="px-2"
      >
        <v-chip
          v-for="grp in mapStore.positionGroups"
          :key="grp.id"
          :value="grp.id"
          size="small"
          filter
          variant="outlined"
        >
          {{ titleOf(grp) }}
        </v-chip>
      </v-chip-group>

      <!-- Sub-posiciones: solo de las posiciones activas (decisions §10). -->
      <template
        v-for="grp in mapStore.positionGroups"
        :key="`sub-${grp.id}`"
      >
        <div
          v-if="mapStore.filters.positions.includes(grp.id)"
          class="mt-1"
        >
          <div class="text-caption text-medium-emphasis px-2">
            {{ titleOf(grp) }}
          </div>
          <v-list
            v-model:selected="mapStore.filters.positionTypes[grp.id]"
            select-strategy="leaf"
            density="compact"
            max-height="180"
            class="py-0"
          >
            <v-list-item
              v-for="pt in mapStore.positionTypeOptions(grp.id)"
              :key="pt.id"
              :value="pt.id"
              :title="titleOf(pt)"
            >
              <template #prepend="{ isSelected }">
                <v-checkbox-btn :model-value="isSelected" density="compact"/>
              </template>
            </v-list-item>
          </v-list>
        </div>
      </template>
    </v-card>
  </component>
</template>

<style scoped>
.rail-btn {
  display: flex;
  align-items: center;
}
</style>
