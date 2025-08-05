<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import {useMainStore} from "~/store/index.js";
import CriteriaChip from "~/components/dashboard/source/CriteriaChip.vue";
import {computed} from "vue";
import dayjs from "dayjs";

const mainStore = useMainStore()
const { ai_extractivism_types } = mainStore

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})

const pretty_date = computed(() => {
  return dayjs(props.main.published_date).format("DD/MM/YYYY")
})

const final_mentions = computed(() => {
  if (!props.main || !props.main.criteria) {
    console.warn("No main or criteria found", props.main)
    return []
  }
  const projects = props.main.criteria.projects
  if (!projects){
    console.warn("No projects found in main criteria", props.main)
    return []
  }
  return projects.map(project => {
    const name_types = project.types
    if (!name_types) {
      console.warn("Problem: ", props.main)
      return {
        project_full: {
          name: project.name,
          extractivism_types: [],
        }
      }
    }
    let extractivism_types = name_types.map(type => {
      return ai_extractivism_types[type]
    })
    return {
      project_full: {
        name: project.name,
        extractivism_types: extractivism_types,
      }
    }
  })
})

</script>

<template>

  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #title>
      <div class="d-flex flex-column align-start justify-start">
        <div class="ml-2 text-caption">
          <span class="text-grey-darken-1">
            {{pretty_date}}
          </span>
<!--          <span class="text-purple-darken-1 ml-3">-->
<!--            {{main.title}}-->
<!--          </span>-->
        </div>
        <v-card
          class="ml-2 text-body-1"
          variant="flat"
          color="transparent"
          style="text-wrap: pretty; max-height: 54px; overflow: hidden;"
        >
          {{ main.title }}
          <v-tooltip
            activator="parent"
            location="bottom"
            :max-width="400"
          >
            {{ main.title }}
          </v-tooltip>

        </v-card>
      </div>
    </template>
    <template #details>
<!--      {{main.criteria.projects.length}}-->
      <CriteriaChip
        v-if="main.criteria"
        :main="main"
      />

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
  </HeaderCommon>
</template>

<style scoped>

</style>