<script setup >

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

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
  <v-col cols="12" class="d-flex pa-0">
    <SelectGroup
      filter_group_name="participant_types"
      :main_object="full_main"
      forced_level="subtype"
    />
    <v-switch
      v-model="full_main.required_interests"
      label="Requerir Intereses"
      append-icon="category"
      hide-details
      color="primary"
    />
  </v-col>
</template>

<style scoped>

</style>