<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
})
const full_main = defineModel({type: Object, required: true})

</script>

<template>
  <SelectGroup
    filter_group_name="sectors"
    v-model="full_main"
    main_collection_name="sector"
    :width="360"
    forced_level="subtype"
  />
</template>

<style scoped>

</style>