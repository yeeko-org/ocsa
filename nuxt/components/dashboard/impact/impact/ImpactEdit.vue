<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

const props = defineProps({
  is_edit: Boolean,
  is_massive_edit: Boolean,
})
const full_main = defineModel({type: Object, required: true})
</script>

<template>
  <SelectGroup
    v-model="full_main"
    filter_group_name="impact_types"
    main_collection_name="impact"
  />
</template>

<style scoped>

</style>
