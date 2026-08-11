<script setup>

import ToolbarCommon from "~/components/dashboard/capture/ToolbarCommon.vue";

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import LocationMex from "~/components/dashboard/space_time/location/LocationMex.vue";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
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
  direct_displacement: Boolean,
})
const displacements = defineModel({type: Array, required: true})


const show_displacement = computed(() => {
  if (props.direct_displacement)
    return true
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
          v-model="displacements[index].rithm"
          :items="['Paulatino', 'Repentino']"
          label="Ritmo"
          variant="outlined"
          class="ml-2"
          style="max-width: 300px; min-width: 200px;"
          clearable
        >
        </v-select>
      </div>
      <div class="mt-2 text-title-medium">
        Origen del desplazamiento:
      </div>
      <div class="d-flex flex-wrap">
        <LocationMex
          v-model:state="displacements[index].origin_state"
          v-model:municipality="displacements[index].origin_municipality"
          v-model:locality="displacements[index].origin_locality"
          clearable
        />
      </div>
      <div
        v-if="item.dimension"
        class="mt-2 text-title-medium"
      >
        Destino del desplazamiento:
      </div>
      <div class="d-flex flex-wrap">
        <LocationMex
          v-if="item.dimension === internal_displacement.id"
          v-model:state="displacements[index].destination_state"
          v-model:municipality="displacements[index].destination_municipality"
          v-model:locality="displacements[index].destination_locality"
          clearable
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