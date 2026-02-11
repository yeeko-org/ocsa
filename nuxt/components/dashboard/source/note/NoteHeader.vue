<script setup>

import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import ImpactChip from "~/components/dashboard/impact/ImpactChip.vue";
import HeaderCommon from "~/components/dashboard/common/generic/HeaderCommon.vue";

import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";

import NoteTitle from "~/components/dashboard/source/note/NoteTitle.vue";
import EventGroupsChip from "~/components/dashboard/event/EventGroupsChip.vue";

const props = defineProps({
  main: Object,
  mentions: Array,
  collection_data: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
  parent: String,
  is_simple: Boolean,
})

const note = computed(() => props.main)
// const emits = defineEmits(['open-panel'])

const final_mentions = computed(() => {
  let mentions =  props.mentions || props.main.mentions
  return mentions.filter(mention => mention.project)
})

const events_count = computed(() => {
  let hide_events = false
  const final_count = final_mentions.value.reduce((acc, mention) => {
    if (!mention.events || hide_events) {
      hide_events = true
      return acc
    }
    return acc + mention.events.length
  }, 0)
  if (hide_events)
    return null
  return final_count
})

</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
    :height="74"
  >
    <template #title>
      <NoteTitle
        :main="main"
      />
    </template>
    <template #details>
      <ProjectMiniList
        v-if="main && (!parent || parent !== 'project')"
        :mentions="final_mentions"
      />
      <EventGroupsChip
        v-if="!is_simple"
        :mentions="final_mentions"
      />
      <v-divider
        vertical
        inset
        class="mx-0"
      />
      <ImpactChip
        v-if="!is_simple"
        :main_array="final_mentions"
        filter_group_name="impact_types"
        child_field="impacts"
      />
      <v-divider
        vertical
        class="mx-1"
      />

      <ActorsChip
        :main="note"
        :mentions="final_mentions"
        :is_simple="is_simple"
      />
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>