<script setup>

import CardCommon from "~/components/dashboard/common/generic/CardCommon.vue";

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
  <div
    class="my-2"
  >
    <CardCommon
      v-for="result in results"
      :key="result[elem_id]"
      :collection_data="collection_data"
      class="my-2"
      :full_main="result"
      is_select
      @selected-item="selectItem"
    />
  </div>
</template>

<style scoped>

</style>