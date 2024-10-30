<script setup>
import {computed} from 'vue'
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import StatusChip from "~/components/dashboard/status/StatusChip.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    required: false,
    default: true,
  }
})

const actor = computed(() => props.main)

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
    :collection_data="collection_data"
  >
    <template #details>
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