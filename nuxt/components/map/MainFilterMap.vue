
<script setup>

import {storeToRefs} from "pinia";

import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  selectedExtractivismTypes: {
    type: Array,
    default: () => [],
  },
})

const extractivism_types_list = computed(() => {
  if (!cats.value) return [];
  return cats.value.extractivism_type || [];
});

</script>

<template>
  <v-sheet
    color="#FFFFFF60"
    class="sheet-filters px-3 pt-2"
  >
    <div v-if="false" class="text-h6 pt-2">
      Filtros
    </div>

    <v-chip-group
      :model-value="selectedExtractivismTypes"
      column
      multiple
      @update:model-value="$emit('update:selectedExtractivismTypes', $event)"
    >
      <div class="text-subtitle-1 pt-1 pr-3 font-weight-medium">
        Tipos de extractivismo:
      </div>
      <v-chip
        v-for="e_type in extractivism_types_list"
        :key="e_type.id"
        :value="e_type.id"
        :color="e_type.color"
        :base-color="`${e_type.color}C9`"
        class="mt-0 mb-2"
        variant="flat"
        filter
      >
        {{ e_type.short_name || e_type.name }}
        <template v-slot:prepend>
          <v-icon color="white" class="mr-1">{{ e_type.icon }}</v-icon>
        </template>
      </v-chip>

    </v-chip-group>
  </v-sheet>
</template>
<style>

.sheet-filters {
  position: absolute !important;
  top: 0;
  left: 0;
  z-index: 1;
  margin-right: 40px;
}


</style>