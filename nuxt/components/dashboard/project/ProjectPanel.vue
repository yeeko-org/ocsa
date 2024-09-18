<script setup>
import { ref, computed, defineProps } from 'vue'
import ProjectHeader from "~/components/dashboard/project/ProjectHeader.vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import ProjectSheet from "~/components/dashboard/project/ProjectSheet.vue";

const mainStore = useMainStore()
const { getProject, getNote } = mainStore

const props = defineProps({
  project: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
const { cats, impact_groups, positions } = storeToRefs(mainStore)
const full_project = ref({})

const openProject = () => {
  console.log("open project", props.project)
  getProject(props.project.id).then((res) => {
    console.log("project fetched", res)
    full_project.value = res
  })
}

</script>

<template>
  <v-expansion-panel class="d-flex">
    <v-sheet
      color="purple-lighten-5"
      class="d-flex align-start flex-shrink-0"
    >
      <v-checkbox
        _v-model="sel.selected_months"
        _value="month"
        _density="comfortable"
        hide-details
        class="pt-1 pl-1"
      />
    </v-sheet>
    <div class="flex-grow-1">
      <ProjectHeader
        :project="project"
        :show_details="show_details"
        @open-project="openProject"
      />
      <v-expansion-panel-text
        class="ml-n16 mr-n6"
        color="purple-lighten-5"
      >
        <ProjectSheet
          :full_project="full_project"
          :show_details="show_details"
        />
      </v-expansion-panel-text>
    </div>
  </v-expansion-panel>
</template>

<style scoped>

</style>