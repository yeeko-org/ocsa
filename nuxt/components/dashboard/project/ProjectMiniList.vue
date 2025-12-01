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
    >
      <ExtractivismIcons
        :project="mention.project_full"
        is_small
      />
      <v-card
        class="ml-1"
        variant="flat"
        color="transparent"
      >
        {{ mention.project_full.name }}
        <v-tooltip
          activator="parent"
          location="bottom"
          :max-width="400"
        >
          {{ mention.project_full.name }}
          <br/>
          <template v-if="mention.project_full.tooltip_complement">
            Párrafos:
            {{ mention.project_full.tooltip_complement }}
          </template>
        </v-tooltip>
      </v-card>

    </div>
  </div>

</template>

<style scoped>

</style>