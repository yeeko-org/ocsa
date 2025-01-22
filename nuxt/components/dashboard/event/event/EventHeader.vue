<script setup>

import {computed} from "vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

const props = defineProps({
  main: Object,
  mentions: Array,
  collection_data: Object,
  is_small: Boolean,
  show_details: {
    type: Boolean,
    default: false,
  },
  parent: String,
})

const involvement_count = computed(() => {
  if (!props.main.involvements)
    return 0
  return props.main.involvements.length
})

const event_subtype = computed(() => {
  return null
  // return event_subtypes.value.find(
  //   subtype => props.main.event_subtype === subtype.id)
})

// const main_collection = computed(() => {
//   return schemas.value.collections_dict['event']
// })

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
    :collection_data="collection_data"
  >
    <template #icon v-if="final_event_types.length">
      <v-icon
        :icon="final_event_types[0].event_group.icon"
      ></v-icon>
    </template>
    <template #title>
      <v-card
        color="lime"
        rounded="lg"
        variant="outlined"
        class="mx-2 d-flex flex-column"
      >
        <SelectGroup
          :main_object="main"
          filter_group_name="event_types"
          main_collection_name="event"
          :width="160"
          is_display
        />
      </v-card>
    </template>
    <template #details>
      <ProjectMiniList
        :mentions="[main.mention_full]"
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