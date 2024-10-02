<script setup>

import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";

import { computed } from 'vue'

const props = defineProps({
  mentions: Array,
})

</script>

<template>
  <div
    class="text-body-2 mr-6"
    style="max-width: 260px;"
  >
    <div
      v-for="mention in mentions"
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

</template>

<style scoped>

</style>