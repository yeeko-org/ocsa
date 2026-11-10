<script setup>

import Comments from "~/components/dashboard/common/utils/Comments.vue";
import ToolbarCommon from "~/components/dashboard/capture/ToolbarCommon.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";

import LocationEdit from "~/components/dashboard/space_time/location/LocationEdit.vue";

const props = defineProps({
  main_collection_name: String,
  parent_id: Number,
})
// const full_main = defineModel({type: Object, required: true})
const locations = defineModel({type: Array, required: true})
</script>

<template>
  <ToolbarCommon
    v-model="locations"
    :cols="12"
    filter_group_name="states"
    :main_collection_name="main_collection_name"
    child_relation_name="location"
    color="blue-grey"
    forced_level="group"
    :parent_id="parent_id"
    :additional_fields="{'status_location': 'empty', 'type_location': 'point'}"
  >
    <template #rows_init="{item, index}">
      <div class="d-flex align-start align-self-start">
        <v-chip variant="outlined" color="grey" min-width="150" label>
          Ubicación
        </v-chip>
      </div>
      <v-spacer></v-spacer>
      <div
        class="d-flex justify-end"
      >
        <StatusDetail
          v-model="locations[index]"
          collection="location"
          style="max-width: 280px; min-width: 200px;"
          hide_details
        />
        <Comments
          :main="item"
          collection_name="location"
          :width="280"
        />
      </div>
    </template>
    <template #rows="{item, index}">
      <v-row>
        <LocationEdit v-model="locations[index]" />
      </v-row>
    </template>
  </ToolbarCommon>

</template>

<style scoped>

</style>