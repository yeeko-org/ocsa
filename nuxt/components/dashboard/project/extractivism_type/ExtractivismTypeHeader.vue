<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})

const megaproject_types_count = computed(() => {
  return props.main.megaproject_types?.length
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
        :count="megaproject_types_count"
        icon="category"
        label="proyecto"
        label_plural="tipos de megaproyecto"
        color="purple"
        class="mx-1"
      />
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>