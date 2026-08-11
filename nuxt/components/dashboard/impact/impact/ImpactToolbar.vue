  <script setup>

import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import ToolbarCommon from "~/components/dashboard/capture/ToolbarCommon.vue";

const impacts = defineModel({type: Array, required: true})
const props = defineProps({
  parent_id: Number,
  note_id: Number,
})
const mainRef = ref(null)
defineExpose({ validate })

function validate(){
  if (mainRef.value)
    return mainRef.value.validateAllForms()
  return true
}
</script>

<template>
  <ToolbarCommon
    v-model="impacts"
    ref="mainRef"
    filter_group_name="impact_types"
    child_relation_name="impact"
    two_columns
    required
    partial_save
    required_field="impact_type"
    :parent_id="parent_id"
    :note_id="note_id"
    :additional_fields="{'locations': [], 'displacements': []}"
  >
    <template #rows="{ item, index }">
      <v-switch
        v-model="item.is_potential"
        label="Se trata de una afectación potencial"
        class="ml-4"
        color="accent"
        append-icon="tips_and_updates"
      />
      <v-textarea
        v-model="item.description"
        label="Descripción de la afectación"
        variant="outlined"
        density="compact"
        hide-details
        rows="1"
        auto-grow
        style="max-width: 600px;"
      ></v-textarea>
      <DisplacementToolbar
        v-if="impacts[index].displacements"
        v-model="impacts[index].displacements"
        :impact_type="impacts[index].impact_type"
        :parent_id="item.id"
        main_collection_name="impact"
        second_level
        class="px-0"
      />
    </template>
    <template #second-column="{ second_index, index }">
      <LocationsToolbar
        v-if="impacts[second_index]"
        v-model="impacts[second_index].locations"
        :parent_id="impacts[second_index].id"
        :note_id="parent_id"
        main_collection_name="impact"
        second_level
      />
    </template>
  </ToolbarCommon>
</template>

<style scoped>

</style>