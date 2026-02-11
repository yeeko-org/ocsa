  <script setup>

import ToolbarCommon from "~/components/dashboard/capture/ToolbarCommon.vue";
import SelectDate from "~/components/dashboard/common/select/SelectDate.vue";
const props = defineProps({
  parent_id: Number,
  note_id: Number,
})
const status_history = defineModel({type: Array, required: true})

</script>

<template>
  <ToolbarCommon
    :cols="5"
    v-model="status_history"
    filter_group_name="status_projects"
    child_relation_name="status_history"
    required_field="status_project"
    required_full_category
    color="purple"
    :note_id="note_id"
    :parent_id="parent_id"
  >
    <template #rows_init="{item}">
      <div class="d-flex align-center mt-2">
        <v-icon
          variant="outlined"
          color="purple"
          size="x-large"
          class="mb-3 mx-1"
        >
          history_toggle_off
        </v-icon>
        <SelectDate
          :init_date="item.date"
          @update-date="item.date = $event"
          label="Fecha de cambio"
          hide_details
        />
      </div>
    </template>
    <template #rows="{item}">
      <div
        v-if="item.status_project_text && !item.id"
      >
        <b>Pre-registro:</b>
        {{ item.status_project_text }}
      </div>
    </template>
  </ToolbarCommon>
</template>

<style scoped>

</style>