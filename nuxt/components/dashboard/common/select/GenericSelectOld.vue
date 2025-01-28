<script setup>
import {defineComponent, ref, computed} from 'vue'
import { useMainStore } from '~/store/index.js'
import { storeToRefs } from 'pinia'
const mainStore = useMainStore()

const props = defineProps({
  final_filters: Object,
  collection: String,
  filter_group_name: String,
  collection_group: String,
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

const { status, cats, all_nodes } = storeToRefs(mainStore)

// const is_status = computed(() => props.collection_group === "status")

const root_node = computed(() => {
  return all_nodes.value[props.filter_group_name]
})

const item_value = computed(() => {
  return props.item_id || 'id'
})

const items_built = computed(() => {
  return cats.value[props.collection]
  // if (props.collection_group === "impact")
  //   return cats.value["impact_types"].filter(
  //     impact_type => impact_type.impact_group === props.collection)
  //   // return impact_groups.value[props.collection]
  // else{
  //   // console.log("cats", cats.value)
  //   return cats.value[`${props.collection}s`]
  // }
})

</script>

<template>
  <v-autocomplete
    v-if="is_autocomplete"
    v-model="final_filters[field]"
    :items="items_built"
    item-title="name"
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
    item-title="name"
    :item-value="item_value"
    :density="density"
    variant="outlined"
    :clearable="clearable"
    _change="changeStatus"
  ></v-select>

</template>

<style scoped>

</style>