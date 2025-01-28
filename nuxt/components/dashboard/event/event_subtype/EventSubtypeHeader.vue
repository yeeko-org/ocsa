<script setup >

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import {nextTick} from "vue";
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

const mainStore = useMainStore()
const { all_nodes, cats } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})

const main_node = computed(() => {
  return all_nodes.value.event_types.find(
    node => node.id === `subtype_${props.main.id}`)
})

// nextTick(() => {
//   setTimeout(() => {
//     if (props.main.id){
//       // console.log("main_node", main_node.value)
//       props.main.event_group = main_node.value.parent.parent.data.id
//     }
//   }, 10)
// })

const event_group = computed(() => {
  return cats.value.event_group.find(
    group => group.id === props.main.event_group)
})


</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #icon v-if="false">
      <v-icon
        v-if="event_group && false"
        :color="event_group.color"
        v-tooltip="event_group.name"
      >
        {{ event_group.icon }}
      </v-icon>
    </template>
    <template #title v-if="false">
      <v-card
        variant="outlined"
        color="grey-lighten-2"
        class="py-1 px-2 ml-3"
      >
        <span class="text-black text-subtitle-1">
          {{ main.name }}
        </span>
      </v-card>
    </template>
    <template #details>
      <HeaderChip
        :count="main.count"
        icon="notifications_active"
        label="evento"
        label_plural="eventos"
        color="lime-darken-2"
        class="mx-1"
      />
      <v-card
        variant="tonal"
        color="accent"
        class="d-flex justify-center align-center ml-3 py-1"
      >
        <SelectGroup
          :main_object="main"
          filter_group_name="event_types"
          :main_collection="collection_data"
          field="event_types"
          forced_level="subtype"
          :width="160"
          is_display
        />
      </v-card>

    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>