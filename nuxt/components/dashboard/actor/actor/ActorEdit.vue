<script setup>

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
    <v-text-field
      v-model="full_main.alternative_names"
      label="Nombres alternativos"
      variant="outlined"
      class="mb-2"
    />
  </v-col>
  <v-col cols="12" class="d-flex pa-0">
    <v-text-field
      v-model="full_main.official_name"
      label="Nombre oficial del actor"
      variant="outlined"
      class="mb-2 mr-3"
    />
    <SelectGroup
      :main_object="full_main"
      filter_group_name="sectors"
      main_collection_name="actor"
    />
  </v-col>
  <v-col cols="12" class="d-flex pa-0">
    <SelectGroup
      :main_object="full_main"
      filter_group_name="belongs"
      main_collection_name="actor"
      field="belongs"
      :width="400"
      subtype_class="mr-2"
    />
    <SelectGroup
      :main_object="full_main"
      filter_group_name="indigenous_groups"
      main_collection_name="actor"
      field="indigenous_group"
      subtype_class="mr-2"
    />
    <SelectGroup
      :main_object="full_main"
      filter_group_name="countries"
      main_collection_name="actor"
      field="countries"
    />
  </v-col>
</template>

<style scoped>

</style>