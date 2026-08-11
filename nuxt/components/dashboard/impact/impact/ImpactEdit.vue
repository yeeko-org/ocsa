<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  col_order: {
    type: Number,
    default: 5,
  }
})
const full_main = defineModel({type: Object, required: true})
</script>

<template>
  <v-col
    cols="12"
    class="d-flex pa-0"
    :order="col_order"
  >
    <SelectGroup
      v-model="full_main"
      filter_group_name="impact_types"
      main_collection_name="impact"
    />
  </v-col>
</template>

<style scoped>

</style>
