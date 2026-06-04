<script setup>
import { computed, watch } from 'vue'
import { useDisplay } from 'vuetify'
import { VMenu, VBottomSheet } from 'vuetify/components'
import { useMapStore } from '~/store/map.js'
import ActorSearch from '~/components/map/filters/custom/ActorSearch.vue'
import HelpTooltip from '~/components/map/common/HelpTooltip.vue'

const { smAndDown } = useDisplay()
const mapStore = useMapStore()

const rg = computed(() => mapStore.resolveGroup('actors') || {})
const count = computed(() => mapStore.countFor('actors'))
const hasSelection = computed(() => count.value > 0)

const isOpen = computed({
  get: () => mapStore.activePickerKey === 'actors',
  set: v => { mapStore.activePickerKey = v ? 'actors' : null },
})

// Al abrir el picker, carga lazy el payload de actores (idempotente con el
// @focus del buscador: solo se descarga una vez).
watch(isOpen, open => { if (open) mapStore.ensureActors() })
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
      <div class="d-flex align-center">
        <v-badge
          :model-value="hasSelection"
          :content="count"
          :color="rg.color"
          location="bottom end"
          offset-x="2"
          offset-y="2"
        >
          <v-btn
            :icon="rg.icon"
            :color="rg.color"
            :variant="hasSelection ? 'tonal' : 'text'"
            :active="isOpen"
            size="large"
            v-bind="actProps"
          />
        </v-badge>
        <v-tooltip activator="parent" :text="rg.label" location="end"/>
      </div>
    </template>

    <v-card min-width="340" max-width="460" class="pa-2">
      <div class="text-title-medium font-weight-bold px-2 pt-1 pb-2 d-flex
        align-center">
        <v-icon :color="rg.color" :icon="rg.icon" class="mr-2"/>
        {{ rg.label }}
        <HelpTooltip
          :title="rg.label"
          :description="rg.description"
          :color="rg.color"
        />
      </div>

      <div class="px-2 mb-3">
        <ActorSearch/>
      </div>

      <div class="text-title-small font-weight-medium px-2">Posiciones</div>
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
          :color="grp.color"
          :prepend-icon="grp.icon"
          :variant="mapStore.filters.positions.includes(grp.id)
            ? 'flat' : 'outlined'"
          size="small"
        >
          {{ grp.name }}
        </v-chip>
      </v-chip-group>

      <!-- Sub-posiciones: solo de las posiciones activas. -->
      <template
        v-for="grp in mapStore.positionGroups"
        :key="`sub-${grp.id}`"
      >
        <div
          v-if="mapStore.filters.positions.includes(grp.id)"
          class="mt-1"
        >
          <div class="text-body-small text-medium-emphasis px-2">
            {{ grp.name }}
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
              :title="pt.name"
              class="ms-item"
            >
              <template #prepend="{ isSelected }">
                <v-checkbox-btn
                  :model-value="isSelected"
                  density="compact"
                  class="ms-check"
                />
                <v-icon
                  v-if="pt.icon"
                  :color="pt.color || 'grey-darken-2'"
                  :icon="pt.icon"
                  class="mr-2"
                />
              </template>
            </v-list-item>
          </v-list>
        </div>
      </template>
    </v-card>
  </component>
</template>

<style scoped>
/* Checkbox de sub-posiciones pegado a la izquierda sin empujar el texto. */
.ms-item :deep(.v-list-item__spacer) {
  width: 8px;
}
.ms-item {
  padding-inline-start: 8px !important;
}
.ms-check {
  margin-inline-end: 0;
}
</style>
