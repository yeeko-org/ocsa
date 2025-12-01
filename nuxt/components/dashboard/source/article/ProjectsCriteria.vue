<script setup>
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const { ai_extractivism_types } = mainStore

import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
const props = defineProps({
  criteria: {
    type: Object,
    required: true,
  },
})


const final_mentions = computed(() => {
  if (!props.criteria) {
    console.warn("No main or criteria found", props.criteria)
    return []
  }
  const projects = props.criteria.projects
  if (!projects){
    console.warn("No projects found in main criteria", props.criteria)
    return []
  }
  return projects.map(project => {
    const name_types = project.types
    if (!name_types) {
      console.warn("Problem: ", props.criteria, project)
      return {
        project_full: {
          name: project.name,
          tooltip_complement: project.paragraphs,
          extractivism_types: [],
        }
      }
    }
    let extractivism_types = []
    name_types.forEach(type => {
      const et = ai_extractivism_types[type]
      if (et)
        extractivism_types.push(et)
    })
    return {
      project_full: {
        name: project.name,
        tooltip_complement: project.paragraphs,
        extractivism_types: extractivism_types,
      }
    }
  })
})

</script>

<template>
  <ProjectMiniList
    :mentions="final_mentions"
  />
  <v-alert
    v-if="final_mentions.length === 0"
    type="warning"
    max-width="200"
    variant="outlined"
    density="compact"
    class="ml-0"
  >
    Sin proyectos
  </v-alert>

</template>

<style scoped>

</style>