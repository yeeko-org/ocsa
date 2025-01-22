<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})

const mentions = computed(() => {
  return props.main.projects.map(project => {
    return {project_full: project}
  })
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
        :count="main.projects.length"
        collection_name="project"
        class="ml-2"
        horizontal
      />
      <ProjectMiniList
        :mentions="mentions"
      />
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>