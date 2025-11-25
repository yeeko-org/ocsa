<script setup>

import {computed} from "vue";

import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import ImpactChip from "~/components/dashboard/impact/ImpactChip.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

import NoteTitle from "~/components/dashboard/source/note/NoteTitle.vue";

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
  is_map_viz: {
    type: Boolean,
    default: false,
  },
})

const note = computed(() => props.main)
// const emits = defineEmits(['open-panel'])

const final_mentions = computed(() => {
  return props.mentions || props.main.mentions
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
    :is_map_viz="is_map_viz"
  >
    <template #title>
      <NoteTitle
        :main="main"
      />
    </template>
    <template #details>
      <ProjectMiniList
        v-if="!is_map_viz && main && (!parent || parent !== 'project')"
        :mentions="final_mentions"
      />
      <ImpactChip
        v-if="!is_simple"
        :main_array="final_mentions"
        filter_group_name="impact_types"
        child_field="impacts"
      />
      <HeaderChip
        v-if="!is_simple && events_count !== null"
        :count="events_count"
        collection_name="event"
        icon="notifications_active"
        label="evento"
        label_plural="eventos"
        color="lime-darken-2"
        class="mr-2 ml-1"
      />
      <ActorsChip
        :main="note"
        :mentions="final_mentions"
        :is_simple="is_simple"
      />
      <div
        v-if="!is_simple && !is_map_viz"
        class="ml-1 d-flex flex-column align-center"
      >
        <div class="text-grey text-caption">
          {{main.nota_id_ref}}
        </div>
        <div class="text-grey-lighten-1 text-caption">
          {{main.id}}
        </div>
      </div>
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>