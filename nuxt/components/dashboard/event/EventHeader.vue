<script setup>

import {computed} from "vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

import {useMainStore} from '~/store/index'
import {storeToRefs} from 'pinia'
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
const mainStore = useMainStore()
const { groups, event_types, event_subtypes } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  mentions: Array,
  group: Object,
  is_small: Boolean,
  show_details: {
    type: Boolean,
    default: false,
  },
  parent: String,
})

const final_group = computed(() => {
  return props.group || groups.value.find(gr => gr.key === 'event')
})

const involvement_count = computed(() => {
  return props.main.involvements.length
})

const event_subtype = computed(() => {
  return event_subtypes.value.find(
    subtype => props.main.event_subtype === subtype.id)
})

const final_event_types = computed(() => {
  if (!event_subtype.value)
    return []
  const event_type_obj = event_subtype.value.event_type_obj
  // console.log("event_type_obj", event_type_obj)
  if (event_type_obj.original_types)
    return event_type_obj.original_types
  return [event_type_obj]
})

</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :group="final_group"
    name_field="title"
  >
    <template #icon v-if="final_event_types.length">
      <v-icon
        :icon="final_event_types[0].event_group.icon"
      ></v-icon>
    </template>
    <template #title>
      <div class="pl-3">

        <div class="d-flex">
          <v-chip
            v-for="event_type in final_event_types"
            :key="event_type.id"
            size="small"
            :variant="main.event_type === event_type.id ? 'outlined' : 'tonal'"
            class="mr-1"
          >
            {{ event_type.name }}
            <v-tooltip
              activator="parent"
              location="bottom"
            >
              {{ event_type.name }}
              <div v-if="main.event_type === event_type.id">
                (Categoria principal)
              </div>
            </v-tooltip>
          </v-chip>
        </div>
        <div>
          {{event_subtype.name}}
        </div>
      </div>
    </template>
    <template #details>
      <ProjectMiniList
        :mentions="[main.mention]"
      />
      <HeaderChip
        :count="involvement_count"
        icon="supervised_user_circle"
        label="involucrado"
        label_plural="involucrados"
        color="teal"
        class="ml-2"
      />
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>