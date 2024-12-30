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
  return cats.value.sources.find(src => src.id === note.value.source)
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
      <span class="ml-2 mr-2 text-grey">
        {{main.nota_id_ref}}
      </span>
      <ProjectMiniList
        v-if="!parent || parent !== 'project'"
        :mentions="final_mentions"
      />
      <StatusChip
        v-if="note.status_register && false"
        :main="note"
        collection="register"
        small
        class="mb-1"
      />
      <ImpactChip
        :main_array="final_mentions"
        filter_group_name="impact_types"
        child_field="impacts"
      />
      <HeaderChip
        :count="2"
        icon="notifications_active"
        label="evento"
        label_plural="eventos"
        color="blue"
        class="mr-2"
      />
      <ActorsChip
        :main="note"
        :mentions="final_mentions"
      />
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>