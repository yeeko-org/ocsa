<script setup>
import {defineComponent, ref, computed, defineProps} from 'vue'
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
// export default defineComponent({
//   name: "StatusDetail"
// })
const mainStore = useMainStore()
// const final_filters = ref({})
// const collection = ref("status_location")

const props = defineProps({
  final_filters: Object,
  collection: String,
  field: String,
  collection_type: {
    type: String,
    default: "status",
  },
  density: {
    type: String,
    default: "compact",
  },
  // label: {
  //   type: String,
  //   default: "Status",
  // },
  // clearable: {
  //   type: Boolean,
  //   default: false,
  // },
  // hide_details: {
  //   type: Boolean,
  //   default: false,
  // },
})

const { status, cats } = storeToRefs(mainStore)
const items_built = computed(() => {
  const status_collection = props.collection.split('_')[1]
  return props.collection_type === "status"
      ? status.value[props.collection]
      : cats.value[props.collection]
})

</script>

<template>
  <v-select
    v-model="final_filters[field]"
    :items="items_built"
    item-title="public_name"
    item-value="name"
    :density="density"
    variant="outlined"
    clearable
  >
  </v-select>
</template>

<style scoped>

</style>