
<script setup>

import {storeToRefs} from "pinia";
import {useDisplay} from "vuetify";

import {useMainStore} from "~/store/index.js";
import {useMapStore} from "~/store/map.js";
const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)
const mapStore = useMapStore()
const { smAndDown } = useDisplay()

const extractivism_types_list = computed(() => {
  if (!cats.value) return [];
  return cats.value.extractivism_type || [];
});

</script>

<template>
  <v-sheet
    color="#FFFFFF60"
    :class="[
      'sheet-filters pl-3 pt-1 pb-1 d-flex align-center',
      smAndDown ? 'legend-mobile' : 'legend-desktop',
    ]"
  >
    <div class="text-subtitle-2 pr-3 font-weight-medium flex-shrink-0">
      Tipos de extractivismo:
    </div>
    <v-chip-group
      v-model="mapStore.filters.extractivism"
      show-arrows
      multiple
      class="flex-grow-1"
      style="min-width: 0;"
    >
      <v-chip
        v-for="e_type in extractivism_types_list"
        :key="e_type.id"
        :value="e_type.id"
        :color="e_type.color"
        :base-color="`${e_type.color}C9`"
        class="mt-0 mb-0"
        variant="flat"
        size="small"
        filter
      >
        {{ e_type.short_name || e_type.name }}
        <template v-slot:prepend>
          <v-icon color="white" class="mr-1">{{ e_type.icon }}</v-icon>
        </template>
        <v-tooltip
          activator="parent"
          location="bottom"
          max-width="300"
        >
          <v-card
            :color="e_type.color"
            class="mx-n4 my-n2 px-4 py-2"
            flat
          >
            {{ e_type.name }}
          </v-card>
        </v-tooltip>
      </v-chip>
    </v-chip-group>
  </v-sheet>
</template>
<style>

/* Leyenda de extractivismo (decisions §5): sheet semitransparente flotante,
   siempre visible (es la clave de color del mapa). El encaje fino se afina
   en la Sesión 5. */
.sheet-filters {
  position: absolute !important;
  z-index: 1;
}

/* md+: a la derecha de la isla superior (logo + buscador), NO dentro. */
.legend-desktop {
  top: 12px;
  left: 410px;
  right: 12px;
  max-width: 1130px;
}

/* sm/xs: franja bajo la isla, sobre el rail horizontal (top: 112px). */
.legend-mobile {
  top: 64px;
  left: 8px;
  right: 8px;
}


</style>