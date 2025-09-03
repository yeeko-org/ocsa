<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import {useMainStore} from "~/store/index.js";
import CriteriaChip from "~/components/dashboard/source/CriteriaChip.vue";
import {computed} from "vue";
import dayjs from "dayjs";

const mainStore = useMainStore()
const { ai_extractivism_types, cats, valid_options } = mainStore

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

const source = computed(() => {
  return cats.source.find(src => src.id === props.main.source) || {
    name: "Desconocida",
    id: 0,
  }
})

const valid_undefined = {
  id: null,
  name: "Desconocido",
  icon: "help_outline",
  color: "grey",
  value: null,
}

const selected_undefined = {
  id: null,
  name: "--",
  icon: "",
  color: "yellow-darken-1",
  value: null,
}

const pre_valid_value = computed(() => {
  const degree = props.main.certainty_degree
  if (degree === undefined || degree === null)
    return valid_undefined
  if (degree < 100)
    return valid_options[0]
  else
    return valid_options[1]
})

const valid_value = computed(() => {
  if (typeof props.main.is_selected !== 'boolean'){
    const need_selection = props.main.certainty_degree > 100
    return {
      id: null,
      icon: need_selection ? "help_outline" : null,
      value: null,
      color: need_selection ?  "orange" : "grey-lighten-1",
      name: need_selection ? "Pendiente" : "Sin selección",
    }
  }
  return valid_options.find(
      option => option.value === props.main.is_selected)
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
          <span class="text-purple-darken-1 ml-3">
            {{source.name}}
          </span>
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
      <div
        class="mr-2 d-flex flex-column align-center justify-center"
        style="width: 140px; height: 46px;"
      >
        <v-btn
          variant="outlined"
          class="text-body-2"
          :color="valid_value.color"
          :prepend-icon="valid_value.icon"
          size="small"
        >
          {{ valid_value.name }}
          <v-tooltip
            v-if="main.is_selected === false"
            activator="parent"
            location="bottom"
          >
            <v-card
              color="red-lighten-3"
              class="mx-n4 my-n2"
            >
              <v-card-title
                class="text-subtitle-1"
              >
                Razón de descarte:
              </v-card-title>
              <v-card-text>
                {{ main.other_discarded_reason || 'No especificada' }}
              </v-card-text>
            </v-card>
          </v-tooltip>

        </v-btn>
        <v-btn
          readonly
          variant="plain"
          class="text-body-2 mt-n1"
          :color="pre_valid_value.color"
          :prepend-icon="pre_valid_value.icon"
          size="small"
        >
          {{ pre_valid_value.name }}
        </v-btn>

      </div>
      <CriteriaChip
        v-if="main.criteria"
        :main="main"
        show_foreign
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