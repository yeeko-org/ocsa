<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import {computed} from "vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
const mainStore = useMainStore()
const { schemas, all_nodes } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  mentions: Array,
  collection_data: Object,
  is_small: Boolean,
  show_details: {
    type: Boolean,
    default: false,
  },
})

const sector_group_node = computed(() => {
  return all_nodes.value.sectors.find(
    pt => pt.id === `type_${props.main.sector_group}`)
})

const sector_group = computed(() => {
  const data = sector_group_node.value.data
  return {
    id: data.id,
    name: data.name,
    icon: data.icon,
  }
})

</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #details>
      <HeaderChip
        :count="main.sectors_count"
        collection_name="sector"
        icon="category"
        class="ml-2"
        horizontal
      />
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>