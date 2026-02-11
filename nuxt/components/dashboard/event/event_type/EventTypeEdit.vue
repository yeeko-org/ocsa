<script setup>

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
})
const full_main = defineModel({type: Object, required: true})
const emits = defineEmits(['item-saved'])

</script>

<template>
  <SelectGroup
    v-model="full_main"
    filter_group_name="event_types"
    main_collection_name="event_type"
    field="event_group"
    forced_level="type"
    :width="320"
    required
  />
  <v-switch
    v-model="full_main.has_displacement"
    label="Desplegar Desplazamiento Forzado"
    class="ml-4"
    color="accent"
    append-icon="hiking"
  />
</template>

<style scoped>

</style>