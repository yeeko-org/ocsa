<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
})
</script>


<template>
  <v-col cols="12" class="pa-0 d-flex">
    <v-text-field
      v-model="full_main.alternative_name"
      label="Nombres alternativos"
      variant="outlined"
      class="mr-2"
      style="max-width: 460px;"
    />
    <v-card variant="outlined" class="mr-2 px-2 mb-5">
      <v-switch
        v-model="full_main.is_grouper"
        label="Es agrupador"
        append-icon="group_work"
        hide-details
        color="primary"
      />
    </v-card>

    <SelectGroup
      :main_object="full_main"
      filter_group_name="project_types"
    />
  </v-col>
</template>

<style scoped>

</style>