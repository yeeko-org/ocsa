<script setup>
import StatusChip from '~/components/dashboard/status/StatusChip.vue'
import HeaderChip from '~/components/dashboard/common/HeaderChip.vue'

import { computed } from 'vue'
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
const megaproject_type = computed(() => {
  return props.main
})


</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #icon>
      <ExtractivismIcons
        :megaproject_type="main"
      />
    </template>
    <template #details>
      <HeaderChip
        :count="megaproject_type.count"
        icon="factory"
        label="proyecto"
        label_plural="proyectos"
        color="purple"
        class="mx-1"
        horizontal
      />
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>