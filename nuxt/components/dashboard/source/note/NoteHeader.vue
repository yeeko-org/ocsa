<script setup>

import {computed} from "vue";
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import ImpactChip from "~/components/dashboard/impact/ImpactChip.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

import {useMainStore} from '~/store/index.js'
import {storeToRefs} from 'pinia'
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import StatusChip from "~/components/dashboard/status/StatusChip.vue";
const mainStore = useMainStore()
const { groups } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  mentions: Array,
  group: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  parent: String,
})

const final_group = computed(() => {
  return props.group || groups.value.find(gr => gr.key === 'note')
})

const note = computed(() => props.main)
// const emit = defineEmits(['open-panel'])

const final_mentions = computed(() => {
  return props.mentions || note.value.mentions
})

</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :group="final_group"
    name_field="title"
  >
    <template #details>
      <ProjectMiniList
        v-if="!parent || parent !== 'project'"
        :mentions="final_mentions"
      />
      <StatusChip
        v-if="note.status_register"
        :main="note"
        collection="register"
        field="status_register"
        small
        label="Registro:"
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