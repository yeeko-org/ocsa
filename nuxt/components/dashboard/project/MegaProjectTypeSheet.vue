<script setup>

import NoteHeader from "~/components/dashboard/note/NoteHeader.vue";
import MentionDetails from "~/components/dashboard/note/MentionDetails.vue";
import ProjectHeader from "~/components/dashboard/project/ProjectHeader.vue";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
import PanelCommon from "~/components/dashboard/common/PanelCommon.vue";
import {computed, nextTick, ref} from "vue";

import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
import ProjectSheet from "~/components/dashboard/project/ProjectSheet.vue";
import GenericSelect from "~/components/dashboard/common/GenericSelect.vue";
import MegaProjectEdit from "~/components/dashboard/project/MegaProjectTypeEdit.vue";
const mainStore = useMainStore()
const { groups } = storeToRefs(mainStore)

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
})

const sel = ref({"selected_elems": []})
const main_show_details = ref(false)

const openProject = () => {
  console.log("open project")
}


const project_group = computed(() => {
  return props.group || groups.value.find(gr => gr.key === 'project')
})

function changeShowDetails() {
  console.log("changeShowDetails")
  nextTick(() => {
    setTimeout(() => {
      main_show_details.value = true
    }, 10)
  })
}


</script>

<template>
  <v-expansion-panel-text
    class="ml-n16 mr-n6"
    color="grey-lighten-5"
  >
    <v-sheet
      v-if="full_main"
      color="grey-lighten-5"
      class="mt-n2 mb-n4 pa-3"
    >
      <MegaProjectEdit
        :full_main="full_main"
      />
      <v-card v-if="full_main.projects">
        <v-card-title class="text-deep-purple">
          {{ full_main.projects.length }} Proyectos
        </v-card-title>
        <v-card-text>
          <v-expansion-panels multiple>
            <PanelCommon
              v-for="project in full_main.projects"
              :key="project.id"
              :group="project_group"
              :main="project"
              :sel="sel"
              @finish-open="changeShowDetails"
            >
              <template #header="{openMain}">
                <ProjectHeader
                  :main="project"
                  :show_details="true"
                  @open-panel="openMain"
                  parent="catalog"
                />
              </template>
              <template #sheet="{full_main}">
                <ProjectSheet
                  :full_main="full_main"
                  :show_details="true"
                />
              </template>
            </PanelCommon>
          </v-expansion-panels>

        </v-card-text>

      </v-card>

    </v-sheet>
  </v-expansion-panel-text>
</template>

<style scoped>

</style>