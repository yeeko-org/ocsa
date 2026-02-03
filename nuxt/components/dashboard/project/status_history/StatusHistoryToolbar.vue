  <script setup>

import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import SelectDate from "~/components/dashboard/common/select/SelectDate.vue";

const props = defineProps({
  mention: Object,
})

</script>

<template>
  <ToolbarCommon
    :cols="5"
    :main_object="mention"
    main_collection_name="mention"
    filter_group_name="status_projects"
    child_relation_name="status_history"
    field="status_history"
    color="purple"
    :note_id="mention.id ? mention.note : null"
    :parent_object="{ mention: mention.id }"
  >
    <template #rows_init="{item}">
      <div>
        <v-chip variant="outlined" color="grey" min-width="150" label>
          Status
        </v-chip>
        <div
          v-if="!item.status_project && item.status_project_text && !item.id"
          class="mt-3 ml-n16"
        >
          <b>Pre-registro:</b>
          {{ item.status_project_text }}
        </div>
      </div>
      <v-spacer></v-spacer>
      <SelectDate
        :init_date="item.date"
        @update-date="item.date = $event"
        label="Fecha de cambio"
        class="mb-n6"
        hide_details
      />
    </template>
  </ToolbarCommon>
</template>

<style scoped>

</style>