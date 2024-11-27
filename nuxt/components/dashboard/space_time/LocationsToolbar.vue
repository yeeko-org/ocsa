<script setup>

import Comments from "~/components/dashboard/common/Comments.vue";
import SelectGroup from "~/components/dashboard/common/SelectGroup.vue";
import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import LocationEdit from "~/components/dashboard/space_time/location/LocationEdit.vue";
const mainStore = useMainStore()
const { full_geo } = storeToRefs(mainStore)

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
    :additional_fields="{'status_location': 'empty'}"
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
<!--      <div class="d-flex align-center flex-wrap">-->
<!--        <SelectGroup-->
<!--          :main_object="item"-->
<!--          filter_group_name="states"-->
<!--          :width="200"-->
<!--        />-->
<!--        <v-autocomplete-->
<!--          v-model="item.municipality"-->
<!--          :items="full_geo.state[item.state] || []"-->
<!--          item-title="name"-->
<!--          item-value="id"-->
<!--          label="Municipio"-->
<!--          variant="outlined"-->
<!--          class="ml-2"-->
<!--          max-width="300"-->
<!--          min-width="260"-->
<!--        >-->
<!--        </v-autocomplete>-->
<!--        <v-autocomplete-->
<!--          v-model="item.locality"-->
<!--          :items="full_geo.municipality[item.municipality] || []"-->
<!--          item-title="name"-->
<!--          item-value="id"-->
<!--          label="Localidad"-->
<!--          variant="outlined"-->
<!--          class="ml-2"-->
<!--          max-width="320"-->
<!--          min-width="260"-->
<!--        >-->
<!--        </v-autocomplete>-->
<!--        <v-text-field-->
<!--          v-model="item.latitude"-->
<!--          label="Latitud"-->
<!--          variant="outlined"-->
<!--          class="mx-1"-->
<!--          style="max-width: 180px;"-->
<!--        >-->
<!--        </v-text-field>-->
<!--        <v-text-field-->
<!--          v-model="item.longitude"-->
<!--          label="Longitud"-->
<!--          variant="outlined"-->
<!--          style="max-width: 180px;"-->
<!--        >-->
<!--        </v-text-field>-->
<!--      </div>-->
<!--      <v-textarea-->
<!--        v-model="item.details"-->
<!--        label="Detalles adicionales"-->
<!--        variant="outlined"-->
<!--        class="mb-2"-->
<!--        density="compact"-->
<!--        hide-details-->
<!--        rows="1"-->
<!--        auto-grow-->
<!--      >-->
<!--      </v-textarea>-->
    </template>
  </ToolbarCommon>

</template>

<style scoped>

</style>