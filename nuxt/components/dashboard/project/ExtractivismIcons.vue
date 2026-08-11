<script setup>
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'

const mainStore = useMainStore()
const { all_nodes } = storeToRefs(mainStore)
const props = defineProps({
  project: Object,
  megaproject_type: Object,
  small_icons: Boolean,
  show_name: {
    type: Boolean,
    default: false,
  },
  chip_variant: {
    type: String,
    default: 'flat',
    options: ['flat', 'elevated', 'tonal', 'outlined', 'text'],
  },
  chip_size: {
    type: [String, Number],
    default: 'small',
  },
})

const megaproject_type_node = computed(() => {
  const mp_type_id = props.megaproject_type ?
    props.megaproject_type.id : props.project.megaproject_type
  return all_nodes.value?.project_types?.find(
    pt => pt.id === `subtype_${mp_type_id}`)
})

const original_types = computed(() => {
  if (props.project?.extractivism_types)
    return props.project.extractivism_types
  if (!megaproject_type_node.value)
    return []
  const extractivism_type = megaproject_type_node.value.parent.data
  if (extractivism_type.original_types)
    return extractivism_type.original_types
  return [extractivism_type]
})

</script>

<template>
  <div class="d-flex align-center">
    <div
      v-for="text_type in original_types"
      :key="text_type.id"
    >
      <v-icon
        :color="text_type.color"
        :class="small_icons ? '' : 'mr-1'"
        :size="small_icons ? '18' : 'default'"
      >
        {{ text_type.icon }}
      </v-icon>
      <v-tooltip
        activator="parent"
        location="bottom"
      >
        {{ text_type.name }}
      </v-tooltip>
    </div>
    <v-chip
      v-if="show_name && megaproject_type_node"
      class="ml-1"
      :color="megaproject_type_node.parent.data.color"
      :size="chip_size"
      :variant="chip_variant"
    >
      {{ megaproject_type_node.data.name }}
    </v-chip>
<!--    <v-chip-->
<!--      v-else-->
<!--      class="mr-1"-->
<!--      color="grey"-->
<!--      size="small"-->
<!--    >-->
<!--      ???? {{show_name}}-->
<!--    </v-chip>-->

  </div>

</template>

<style scoped>

</style>