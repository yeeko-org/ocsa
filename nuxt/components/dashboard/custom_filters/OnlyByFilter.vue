<script setup>
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
const mainStore = useMainStore()
const { collections_summary } = storeToRefs(mainStore)

const props = defineProps({
  final_filters: Object,
  field: String,
  label: {
    type: String,
    default: "Usuario",
  },
  filter_box: Object,
})

const items = computed(() => {
  if (!props.filter_box)
    return []
  // console.log("collections_summary", collections_summary.value)
  const options = props.filter_box.options || []
  return options.map((opt) => {
    return collections_summary.value[opt]
  })
})

</script>

<template>
  <v-select
    v-model="final_filters[field]"
    :items="items"
    :label="label"
    item-title="plural_name"
    item-value="value"
    clearable
    variant="underlined"
    density="compact"
    hide-details
    min-width="140"
    max-width="220"
  >
  </v-select>
</template>

<style scoped>

</style>