<script setup>

import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import CriteriaChip from "~/components/dashboard/source/CriteriaChip.vue";

const props = defineProps({
  mentions: Array,
  show_full: Boolean,
  show_checkboxes: Boolean,
  selected_projects: {
    type: Array,
    default: () => [],
  }
})


const emit = defineEmits(['update:selected_projects'])

const localSelectedProjects = computed({
  get: () => props.selected_projects,
  set: (value) => emit('update:selected_projects', value)
})
const show_criteria = computed(() => {
  return props.mentions.some(mention => mention.project_full.second_criteria)
})


</script>

<template>
  <div
    class="text-body-2 mr-6"
    style="overflow: hidden;"
    :style="{ 'max-width': show_criteria ? '410px' : '260px',
            'max-height': show_full ? 'none' : '80px'}"
  >
<!--    <v-code v-if="show_criteria && show_full">-->
<!--      {{selected_projects}}-->
<!--    </v-code>-->
    <div
      v-for="mention in mentions"
      class="ml-2 text-grey-darken-2 d-flex"
      style="max-height: 16px; overflow: hidden;"
      :style="{ 'width': show_criteria ? '400px' : '250px' }"
    >
      <v-checkbox-btn
        v-if="show_criteria && show_full"
        v-model="localSelectedProjects"
        :value="mention.project_full.id"
        density="compact"
        hide-details
      />
      <ExtractivismIcons
        :project="mention.project_full"
        is_small
      />
      <v-card
        class="ml-1"
        variant="flat"
        color="transparent"
        style="width: 220px"
        :class="{
          'text-decoration-underline': mention.is_mentioned,
          'text-decoration-line-through': mention.project_full.degrees < 100
        }"

      >
        {{ mention.project_full.name }}
        <v-tooltip
          activator="parent"
          location="bottom"
          :max-width="400"
        >
          {{ mention.project_full.name }}
          <template v-if="mention.project_full.tooltip_complement">
            <br/>
            Párrafos:
            {{ mention.project_full.tooltip_complement }}
          </template>
        </v-tooltip>
      </v-card>
      <CriteriaChip
        v-if="show_criteria"
        :main="mention.project_full.second_criteria"
        show_negatives
        is_simple
        class="mr-2"
      />
    </div>
  </div>

</template>

<style scoped>

</style>