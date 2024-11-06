<script setup>

import SelectGroup from "~/components/dashboard/common/SelectGroup.vue";
const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})
</script>


<template>
  <v-card-text class="pa-0 d-flex">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="project_types"
      category_group_value="project_type"
    />
  </v-card-text>
</template>

<style scoped>

</style>