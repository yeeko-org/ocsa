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
  <v-col cols="12" class="d-flex px-0" :order="col_order">
    <SelectGroup
      v-model="full_main"
      filter_group_name="interest_types"
      forced_level="type"
      main_collection_name="interest_type"
      subtype_class="ml-6"
    />
  </v-col>


</template>

<style scoped>

</style>