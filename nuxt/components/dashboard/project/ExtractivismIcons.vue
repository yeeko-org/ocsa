<script setup>
import { computed } from "vue";
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'

const mainStore = useMainStore()
const { cats, positions } = storeToRefs(mainStore)
const props = defineProps({
  project: Object,
  megaproject_type: Object,
  is_small: Boolean,
  show_name: {
    type: Boolean,
    default: false,
  },
})

const final_megaproject_type = computed(() => {
  if (props.megaproject_type)
    return props.megaproject_type
  return cats.value.megaproject_types.find(
    mp_type => props.project.megaproject_type === mp_type.id)
})

const original_types = computed(() => {
  if (!final_megaproject_type.value)
    return []
  const extractivism_obj = final_megaproject_type.value.extractivism_obj
  if (extractivism_obj.original_types)
    return extractivism_obj.original_types
  return [extractivism_obj]
})

</script>

<template>
  <div class="d-flex">
    <v-chip
      v-if="show_name"
      class="mr-1"
      :color="final_megaproject_type.extractivism_obj.color"
      size="small"
    >
      {{ final_megaproject_type.name }}
    </v-chip>
    <div
      v-for="ext_type in original_types"
      :key="ext_type.id"
    >
      <v-icon
        :color="ext_type.color"
        :class="is_small ? '' : 'mr-1'"
      >
        {{ ext_type.icon }}
      </v-icon>
      <v-tooltip
        activator="parent"
        location="bottom"
      >
        {{ ext_type.name }}
      </v-tooltip>
    </div>
  </div>

</template>

<style scoped>

</style>