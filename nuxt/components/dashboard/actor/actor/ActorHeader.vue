<script setup>
// export default defineComponent({
//   name: "ActorHeader"
// })
import {computed} from 'vue'
import { useMainStore } from '~/store/index.js'
import { storeToRefs } from 'pinia'
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import StatusChip from "~/components/dashboard/status/StatusChip.vue";
const mainStore = useMainStore()

const { cats, groups } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  group: Object,
  show_details: {
    type: Boolean,
    required: false,
    default: true,
  }
})

const actor = computed(() => props.main)
const final_group = computed(() => {
  return props.group || groups.value.find(gr => gr.key === 'actor')
})

// const emit = defineEmits(['open-panel'])

const unique_projects = computed(() => {
  let projects = actor.value.participants.map(
    participant => participant.mention.project.official_name)
  return [...new Set(projects)]
})

</script>
<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :group="final_group"
  >
    <template #details>
      <StatusChip
        v-if="actor.status_validation"
        :main="actor"
        collection="validation"
        field="status_validation"
        small
        label="Validación:"
        class="mb-1"
      />
      <HeaderChip
        :count="actor.mentions_count"
        icon="newspaper"
        label="mención"
        label_plural="menciones"
        color="deep-purple"
        class="ml-2"
      />
      <ActorsChip
        :main="actor"
        :participants="actor.participants"
        field="project"
        subfield="official_name"
        class="ml-2"
      />
      <HeaderChip
        :count="unique_projects.length"
        :tooltip_complement="unique_projects.join('<br>')"
        icon="factory"
        label="proyecto"
        label_plural="proyectos"
        color="purple"
        class="ml-2"
      />
      <span v-if="actor.network_seq" class="ml-2">
        <v-icon color="deep-purple">lan</v-icon>
        <span class="text-body-2">Red {{ actor.network_seq }}</span>
      </span>
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>