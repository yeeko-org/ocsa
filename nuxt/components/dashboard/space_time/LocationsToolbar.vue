<script setup>

import Comments from "~/components/dashboard/utils/Comments.vue";
import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";

import LocationEdit from "~/components/dashboard/space_time/location/LocationEdit.vue";

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  main_collection_name: String,
  second_level: Boolean,
})

</script>

<template>
  <ToolbarCommon
    :main_object="full_main"
    :cols="12"
    filter_group_name="states"
    :main_collection_name="main_collection_name"
    child_relation_name="location"
    field="locations"
    color="blue-grey"
    forced_level="group"
    :second_level="second_level"
    :additional_fields="{'status_location': 'empty', 'type_location': 'point'}"
  >
    <template #rows_init="{item}">
      <div
        v-if="!second_level"
        class="d-flex align-start align-self-start"
      >
        <v-chip variant="outlined" color="grey" min-width="150" label>
          Ubicación
        </v-chip>
      </div>
      <v-spacer></v-spacer>
      <div
        class="d-flex justify-end"
      >
        <StatusDetail
          :final_filters="item"
          collection="location"
          :style="`max-width: ${second_level ? 250 : 280}px; min-width: 200px;`"
          hide_details
        />
        <Comments
          :main="item"
          collection_name="location"
          :width="second_level ? 200 : 280"
        />
      </div>
    </template>
    <template #rows="{item}">
      <LocationEdit
        :full_main="item"
      />
    </template>
  </ToolbarCommon>

</template>

<style scoped>

</style>