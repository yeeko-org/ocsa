<script setup>

import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";

const props = defineProps({
  mentions: Array,
})


</script>

<template>
  <div
    class="text-body-2 mr-6"
    style="max-width: 260px; max-height: 80px; overflow: hidden;"
  >
    <div
      v-for="mention in mentions"
      class="ml-2 text-grey-darken-2 d-flex"
      style="width: 250px; max-height: 16px; overflow: hidden;"
      v-tooltip:bottom="mention.project_full.name"
    >
      <ExtractivismIcons
        :project="mention.project_full"
        is_small
      />
      <span class="ml-1">
        {{ mention.project_full.name }}
      </span>
    </div>
  </div>

</template>

<style scoped>

</style>