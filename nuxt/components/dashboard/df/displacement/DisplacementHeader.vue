<script setup>

import HeaderCommon from "~/components/dashboard/common/generic/HeaderCommon.vue";

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import DisplayGroup from "~/components/dashboard/common/select/DisplayGroup.vue";
const mainStore = useMainStore()
const { collections_summary, cats } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    required: false,
    default: true,
  }
})

const dest_collection = computed(() => {
  const available_collections = ['event', 'impact']
  const current_collection = available_collections.find(
    collection => props.main[collection]
  )
  return collections_summary.value[current_collection] || {}
})

</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #icon v-if="false">
      <DisplayGroup
        :main_object="main"
        filter_group_name="impact_types"
        main_collection_name="impact"
        field="impact_type"
        forced_level="subtype"
      />
    </template>
    <template #title>
      <v-icon
        v-if="dest_collection.icon"
        :icon="dest_collection.icon"
        :color="dest_collection.color"
        class="mr-2"
      ></v-icon>
      <span class="font-weight-bold">
        {{dest_collection.name}}
      </span>

      <div
        v-if="false"
        class="ml-2 font-weight-bold"
        style="text-wrap: pretty; max-height: 54px; overflow: hidden;"
        v-tooltip:bottom="main.description"
      >{{ main.description }}</div>
    </template>
    <template #details>
      <DisplayGroup
        :main_object="main"
        filter_group_name="dimensions"
        main_collection_name="impact"
        field="dimension"

      />
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>