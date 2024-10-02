<script setup>
import {defineComponent, ref, computed} from 'vue'
import { useMainStore } from '~/store/index.js'
import { storeToRefs } from 'pinia'
const mainStore = useMainStore()

const props = defineProps({
  final_filters: Object,
  collection: String,
  collection_type: String,
  field: String,
  item_id: String,
  clearable: {
    type: Boolean,
    default: true,
  },
  density: {
    type: String,
    default: "compact",
  },
  is_autocomplete: {
    type: Boolean,
    default: false,
  },
  // hide_details: {
  //   type: Boolean,
  //   default: false,
  // },
})

const { status, cats, impact_groups } = storeToRefs(mainStore)
const is_status = computed(() => props.collection_type === "status")
const item_title = computed(() => {
  return is_status.value ? "public_name" : "name"
})
const item_value = computed(() => {
  return props.item_id || (is_status.value ? "name" : "id")
})
const items_built = computed(() => {
  if (is_status.value)
    return status.value[props.collection]
  else if (props.collection_type === "impact")
    return impact_groups.value[props.collection]
  else
    return cats.value[props.collection]
})

</script>

<template>
  <v-autocomplete
    v-if="is_autocomplete"
    v-model="final_filters[field]"
    :items="items_built"
    :item-title="item_title"
    :item-value="item_value"
    :density="density"
    variant="outlined"
    :clearable="clearable"
    _change="changeStatus"
  ></v-autocomplete>
  <v-select
    v-else
    v-model="final_filters[field]"
    :items="items_built"
    :item-title="item_title"
    :item-value="item_value"
    :density="density"
    variant="outlined"
    :clearable="clearable"
    _change="changeStatus"
  ></v-select>

</template>

<style scoped>

</style>