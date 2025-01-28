<script setup>

import {computed} from "vue";
import dayjs from "dayjs";
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import ImpactChip from "~/components/dashboard/impact/ImpactChip.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import StatusChip from "~/components/dashboard/status/StatusChip.vue";

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

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
  return props.mentions || props.main.mentions
})

const pretty_date = computed(() => {
  return dayjs(note.value.date).format("DD/MM/YYYY")
})
const source = computed(() => {
  return cats.value.source.find(src => src.id === note.value.source)
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
    :height="72"
  >
    <template #title>
      <div class="d-flex flex-column align-start justify-start">
        <div class="ml-2 text-caption">
          <span class="text-grey-darken-1">
            {{pretty_date}}
          </span>
          <span class="text-purple-darken-1 ml-3">
            {{source.name}}
          </span>
        </div>
        <div
          class="ml-2 text-body-1"
          style="text-wrap: pretty; max-height: 54px; overflow: hidden;"
          v-tooltip:bottom="main.title"
        >
          {{ main.title }}
        </div>
      </div>
    </template>
    <template #details>
      <ProjectMiniList
        v-if="main && (!parent || parent !== 'project')"
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
        icon="notifications_active"
        label="evento"
        label_plural="eventos"
        color="blue"
        class="mr-2 ml-1"
      />
      <ActorsChip
        :main="note"
        :mentions="final_mentions"
        :is_simple="is_simple"
      />
      <div class="ml-1 d-flex flex-column align-center">
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