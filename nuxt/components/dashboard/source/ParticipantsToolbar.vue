<script setup>

import ToolbarCommon from "~/components/dashboard/capture/ToolbarCommon.vue";
import CardCommon from "~/components/dashboard/common/generic/CardCommon.vue";

const props = defineProps({
  parent_id: Number,
  note_id: Number,
})
// const mention = defineModel({type: Object, required: true})
const participants = defineModel({type: Array, required: true})

const mainToolbarRef = ref(null)
const secondToolbarRef = ref(null)

const emits = defineEmits([
  'selected-item', 'search-item', 'edited-item', 'discard-participant'])
defineExpose({ resetInitialData })

function resetInitialData(){
  if (mainToolbarRef.value)
    mainToolbarRef.value.resetInitialData()
  if (secondToolbarRef.value)
    secondToolbarRef.value.resetInitialData()
}

</script>

<template>
  <ToolbarCommon
    ref="mainToolbarRef"
    v-model="participants"
    :parent_id="parent_id"
    :note_id="note_id"
    filter_group_name="participant_types"
    child_relation_name="participant"
    two_columns
    :additional_fields="{'interests': []}"
    color="blue"
    special_multiple
    emit_add
    required_full_category
    vertical_actions
    hide_pre_buttons
    @add-item="emits('search-item', $event)"
    required
  >
    <template #rows_init="{ item, index }">
      <CardCommon
        :full_main="item.actor_full"
        @edited-item="emits('edited-item', [item, $event])"
        indirect_get
        :init_filters="!item.id ? item.init_filters : {}"
        :note_id="note_id"
        :disabled_discard_buttons="!parent_id"
        collection_name="actor"
        @selected-item="emits('selected-item', [item, index, $event])"
        @discard-item="emits('discard-participant', [item, index])"
      />
    </template>
    <template #second-column="{ item, second_index }">
      <ToolbarCommon
        ref="secondToolbarRef"
        v-model="participants[second_index].interests"
        main_collection_name="participant"
        filter_group_name="interest_types"
        child_relation_name="interest"
        required_full_category
        :note_id="note_id"
        :parent_id="item.id"
        second_level
        color="cyan"
      >
        <template #rows="{ item }">
          <v-textarea
            v-model="item.text"
            label="Descripción del interés"
            variant="outlined"
            class="mr-8"
            density="compact"
            rows="1"
            auto-grow
          ></v-textarea>
        </template>
      </ToolbarCommon>
    </template>
  </ToolbarCommon>
</template>

<style scoped>

</style>