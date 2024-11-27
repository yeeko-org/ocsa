<script setup>
import { computed } from "vue";
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'

const mainStore = useMainStore()
const { all_nodes } = storeToRefs(mainStore)
const props = defineProps({
  project: Object,
  megaproject_type: Object,
  is_small: Boolean,
  show_name: {
    type: Boolean,
    default: false,
  },
})

const megaproject_type_node = computed(() => {
  const mp_type_id = props.megaproject_type ?
    props.megaproject_type.id : props.project.megaproject_type
  return all_nodes.value.project_types.find(
    pt => pt.id === `subtype_${mp_type_id}`)
})

const original_types = computed(() => {
  if (!megaproject_type_node.value)
    return []
  const extractivism_type = megaproject_type_node.value.parent.data
  if (extractivism_type.original_types)
    return extractivism_type.original_types
  return [extractivism_type]
})

</script>

<template>
  <div class="d-flex" v-if="true">
    <v-chip
      v-if="show_name && megaproject_type_node"
      class="mr-1"
      :color="megaproject_type_node.parent.data.color"
      size="small"
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
    <div
      v-for="text_type in original_types"
      :key="text_type.id"
    >
      <v-icon
        :color="text_type.color"
        :class="is_small ? '' : 'mr-1'"
        :size="is_small ? '16' : 'default'"
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
  </div>

</template>

<style scoped>

</style>