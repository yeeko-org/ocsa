<script setup>

import ToolbarCommon from "~/components/dashboard/capture/ToolbarCommon.vue";

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import LocationMex from "~/components/dashboard/space_time/location/LocationMex.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {computed} from "vue";
const mainStore = useMainStore()

const {
  internal_displacement, displacement_event_types, displacement_impact_types
} = storeToRefs(mainStore)

const props = defineProps({
  main_collection_name: String,
  second_level: Boolean,
  is_event: Boolean,
  parent_id: Number,
  event_type: Number,
  impact_type: Number,
  note_id: Number,
})
const displacements = defineModel({type: Array, required: true})


const show_displacement = computed(() => {
  return props.is_event
    ? displacement_event_types.value.includes(props.event_type)
    : displacement_impact_types.value.includes(props.impact_type)
})

</script>

<template>
  <ToolbarCommon
    v-if="show_displacement"
    v-model="displacements"
    :parent_id="parent_id"
    :note_id="note_id"
    :main_collection_name="main_collection_name"
    filter_group_name="dimensions"
    child_relation_name="displacement"
    :second_level="second_level"
    color="orange"
    required
  >
    <template #rows="{ item, index }">
      <SelectGroup
        v-model="displacements[index]"
        filter_group_name="population_sizes"
        main_collection_name="displacement"
        :width="400"
        forced_clearable
      />
      <div class="d-flex">
        <SelectGroup
          v-model="displacements[index]"
          filter_group_name="temporalities"
          main_collection_name="displacement"
          subtype_class="ml-2"
          forced_clearable
        />
        <v-select
          v-model="displacements[index].rhythm"
          :items="['Paulatino', 'Repentino']"
          label="Ritmo"
          variant="outlined"
          class="ml-2"
          style="max-width: 300px; min-width: 200px;"
          clearable
        >
        </v-select>
      </div>
      <div class="mt-2 text-subtitle-1">
        Origen del desplazamiento:
      </div>
      <div class="d-flex flex-wrap">
        <LocationMex
          v-model="displacements[index]"
          state_field="origin_state"
          municipality_field="origin_municipality"
          locality_field="origin_locality"
        />
      </div>
      <div
        v-if="item.dimension"
        class="mt-2 text-subtitle-1"
      >
        Destino del desplazamiento:
      </div>
      <div class="d-flex flex-wrap">
        <LocationMex
          v-if="item.dimension === internal_displacement.id"
          v-model="displacements[index]"
          state_field="destination_state"
          municipality_field="destination_municipality"
          locality_field="destination_locality"
        />
        <SelectGroup
          v-else-if="item.dimension"
          v-model="displacements[index]"
          filter_group_name="countries"
          main_collection_name="displacement"
          forced_clearable
        />
      </div>
    </template>
  </ToolbarCommon>

</template>

<style scoped>

</style>