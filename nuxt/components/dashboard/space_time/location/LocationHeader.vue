<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
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
  const available_collections = ['event', 'project', 'impact']
  const current_collection = available_collections.find(
    collection => props.main[collection]
  )
  return collections_summary.value[current_collection] || {}
})

const final_state = computed(() => {
  return cats.value.state.find(
    state => state.id === props.main.state)
})

</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #icon v-if="false">
      <SelectGroup
        :main_object="main"
        filter_group_name="impact_types"
        main_collection_name="impact"
        field="impact_type"
        forced_level="subtype"
        is_display
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
      <div class="d-flex flex-column ml-3" v-if="final_state">
        <div class="text-caption">Estado:</div>
        <div class="text-subtitle-1">{{final_state.name}}</div>
      </div>
      <span v-else class="ml-3">Estado no definido</span>
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>