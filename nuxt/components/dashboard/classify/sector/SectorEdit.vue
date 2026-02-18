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
      filter_group_name="sectors"
      v-model="full_main"
      main_collection_name="sector"
      :width="360"
      forced_level="subtype"
    />
  </v-col>
</template>

<style scoped>

</style>