<script setup>

import {computed, defineProps} from "vue";
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import ImpactChip from "~/components/dashboard/common/ImpactChip.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";

const props = defineProps({
  note: Object,
  mentions: Array,
  show_details: {
    type: Boolean,
    default: false,
  },
  parent: String,
})
const emit = defineEmits(['open-panel'])

const final_mentions = computed(() => {
  return props.mentions || props.note.mentions
})

</script>

<template>
  <v-expansion-panel-title
    class="pl-0 py-0"
    color="deep-purple-lighten-5"
    style="min-height: 60px;"
    @click="emit('open-panel')"
  >
    <v-icon>newspaper</v-icon>
    <v-toolbar-title
      class="text-subtitle-1 mr-6"
      style="max-width: 360px;"
    >
      <div
        class="ml-2"
        style="text-wrap: pretty; width: 350px; max-height: 54px; overflow: hidden;"
        v-tooltip:bottom="note.title"
      >{{ note.title }}</div>
    </v-toolbar-title>
    <div
      v-if="!parent || parent !== 'project'"
      class="text-body-2 mr-6"
      style="max-width: 260px;"
    >
      <div
        v-for="mention in final_mentions"
        class="ml-2 text-grey-darken-2 d-flex"
        style="width: 250px; max-height: 16px; overflow: hidden;"
        v-tooltip:bottom="mention.project.official_name"
      >
        <ExtractivismIcons
          :project="mention.project"
          is_small
        />
        <span class="ml-1">
          {{ mention.project.official_name }}
        </span>
      </div>
    </div>
    <template v-if="show_details">
      <ImpactChip
        :mentions="final_mentions"
      />
      <ActorsChip
        :main="note"
        :mentions="final_mentions"
      />
    </template>
    <v-btn
      v-else
      color="blue"
      variant="plain"
    >
      cargando detalles...
    </v-btn>

  </v-expansion-panel-title>

</template>

<style scoped>

</style>