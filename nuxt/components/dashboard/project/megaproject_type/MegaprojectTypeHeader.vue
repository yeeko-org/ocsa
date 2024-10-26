<script setup>
import StatusChip from '~/components/dashboard/status/StatusChip.vue'
import HeaderChip from '~/components/dashboard/common/HeaderChip.vue'

import { computed } from 'vue'
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

const props = defineProps({
  main: Object,
  group: Object,
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
    :group="group"
    name_field="name"
  >
    <template #icon>
      <ExtractivismIcons
        :megaproject_type="main"
      />
    </template>
    <template #details>
      <StatusChip
        v-if="megaproject_type.status_validation"
        :main="megaproject_type"
        collection="validation"
        field="status_validation"
        small
        label="Validación:"
        class="mb-1"
      />
      <HeaderChip
        :count="megaproject_type.count"
        icon="factory"
        label="proyecto"
        label_plural="proyectos"
        color="purple"
        class="mx-1"
      />
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>