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
  show_full: Boolean,
  selected_projects: {
    type: Array,
    default: () => [],
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
  return projects.map((project, idx) => {
    const name_types = project.types
    let project_full = {
      id: project.id || idx,
      name: project.name,
      tooltip_complement: project.paragraphs,
      extractivism_types: [],
      degrees: project.degrees,
      is_selected: project.degrees >= 100,
    }
    if (project.degrees){
      project_full.second_criteria = {"criteria": project}
    }
    if (!name_types) {
      console.warn("Problem: ", props.criteria, project)
    }
    else{
      name_types.forEach(type => {
        const et = ai_extractivism_types[type]
        if (et)
          project_full.extractivism_types.push(et)
      })
    }
    return {project_full}
  })
})

</script>

<template>
  <v-alert
    v-if="final_mentions.length === 0"
    type="warning"
    max-width="200"
    variant="outlined"
    density="compact"
  >
    Sin proyectos
  </v-alert>
  <ProjectMiniList
    v-else
    :mentions="final_mentions"
    :show_full="show_full"
    :selected_projects="selected_projects"
    show_checkboxes
    @update:selected_projects="$emit('update:selected_projects', $event)"
  />

</template>

<style scoped>

</style>