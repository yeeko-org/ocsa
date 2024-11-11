<script setup>

import {computed, nextTick, ref} from "vue";

import { storeToRefs } from 'pinia'
import PanelList from "~/components/dashboard/common/PanelList.vue";
import { useMainStore } from '~/store/index.js'
const mainStore = useMainStore()
const { groups, all_nodes, schemas } = storeToRefs(mainStore)

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

const project_collection = computed(() => {
  return schemas.value.collections_dict['project']
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
  <v-card v-if="full_main.projects">
    <v-card-title class="text-deep-purple">
      {{ full_main.projects.length }} Proyectos
    </v-card-title>
    <v-card-text>
      <PanelList
        :results="full_main.projects"
        :collection_data="project_collection"
        :show_details="show_details"
        :sel="sel"
      />

<!--      <v-expansion-panels multiple v-if="false">-->
<!--        <PanelCommon-->
<!--          v-for="project in full_main.projects"-->
<!--          :key="project.id"-->
<!--          :group="project_group"-->
<!--          :main="project"-->
<!--          :sel="sel"-->
<!--          @finish-open="changeShowDetails"-->
<!--        >-->
<!--          <template #header="{openMain}">-->
<!--            <ProjectHeader-->
<!--              :main="project"-->
<!--              :show_details="true"-->
<!--              @open-panel="openMain"-->
<!--              parent="catalog"-->
<!--            />-->
<!--          </template>-->
<!--          <template #sheet="{full_main}">-->
<!--            <ProjectSheet-->
<!--              :full_main="full_main"-->
<!--              :show_details="true"-->
<!--            />-->
<!--          </template>-->
<!--        </PanelCommon>-->
<!--      </v-expansion-panels>-->

    </v-card-text>

  </v-card>
</template>

<style scoped>

</style>