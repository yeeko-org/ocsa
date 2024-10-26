<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

const props = defineProps({
  main: Object,
  group: Object,
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
    :group="group"
    name_field="name"
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