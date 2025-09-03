<script setup>

import CardCommon from "~/components/dashboard/common/CardCommon.vue";

const props = defineProps({
  results: Array,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
const emits = defineEmits(['select-item'])

function selectItem(result) {
  // console.log("item selected", result)
  emits('select-item', result)
}

const elem_id = computed(() => {
  return props.collection_data.pk
})

</script>

<template>
  <v-card
    v-for="result in results"
    :key="result[elem_id]"
    class="my-2 d-flex align-center px-3"
    :color="collection_data.color"
    variant="tonal"
  >
    <CardCommon
      :collection_data="collection_data"
      :full_main="result"
      is_select
      @selected-item="selectItem"
    />
  </v-card>
</template>

<style scoped>

</style>