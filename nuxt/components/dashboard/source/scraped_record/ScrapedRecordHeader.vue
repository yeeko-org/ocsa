<script setup>
import dayjs from 'dayjs'
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

const props = defineProps({
  main: {
    type: Object,
    required: true,
  },
  show_details: Boolean,
  collection_data: Object,
})

const title = computed(() => {
  const format = 'DD/MMM/YY'
  return `${dayjs(props.main.from_date).format(format)} -->
  ${dayjs(props.main.to_date).format(format)}`
})

</script>
<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #title>
      {{ title }}
    </template>
    <template #details>
      <v-chip
        v-if="main.has_errors"
        color="error"
        class="ml-3"
      >
        Tiene errores
      </v-chip>
      <v-chip
        v-else
        color="success"
        class="ml-3"
      >
        Exitoso
      </v-chip>
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>