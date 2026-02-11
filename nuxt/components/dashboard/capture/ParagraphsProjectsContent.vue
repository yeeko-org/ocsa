<script setup>

import CriteriaChip from "~/components/dashboard/capture/CriteriaChip.vue";
import { useMainStore } from "~/store/index.js";
import ProjectsCriteria from "~/components/dashboard/source/article/ProjectsCriteria.vue";
import {storeToRefs} from "pinia";
import {watch} from "vue";
import Paragraph from "~/components/dashboard/capture/Paragraph.vue";

const mainStore = useMainStore()
const { criteria, ai_extractivism_types } = mainStore
const { content_paragraphs } = storeToRefs(mainStore)

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  note_id: Number,
  sending_link: {
    type: Boolean,
    default: false,
  },
  show_init: {
    type: Boolean,
    default: true,
  },
  two_columns: Boolean,
})

const criteria_fields = [
  'opponents',
  'social_impacts',
  'ecological_impacts',
  'acts_of_violence',
  'collective_actions',
]

const show_all = ref(false)
const selected_fields = ref([])
const selected_projects = ref([])
const forced_show = ref(false)
const external_paragraphs = ref([])

function buildParagraph(idx, text="", image=null){
  let paragraph = {
    "idx": idx,
    "criteria": [],
    "criteria_set": new Set(),
    "projects": [],
  }
  if (image){
    paragraph.image = image.src
    paragraph.show_image = false
    paragraph.text = `${image.caption} (pie de foto)`
  }
  else
    paragraph.text = text
  return paragraph
}

const hydrated_data = computed(() => {
  let paragraphs = props.full_main.paragraphs.map((pg, idx) => {
    return buildParagraph(idx + 1, pg)
  })
  let full_criteria = {}
  criteria_fields.forEach((field) => {
    full_criteria[field] = new Set()
  })
  let image_idx = paragraphs.length + 1
  const images = props.full_main.images || []
  images.forEach((image, idx) => {
    if (image.caption)
      paragraphs.push(buildParagraph(image_idx + idx, null, image))
  })
  const projects = props.full_main.second_criteria?.projects || []
  projects.forEach((project, idx) => {
    if (selected_projects.value.length
      && !selected_projects.value.includes(project.id || idx))
      return
    const name_types = project.types
    let extractivism_types = name_types.map(type => {
      return ai_extractivism_types[type]
    })
    const project_data = {
      name: project.name,
      id: project.id || idx,
      degrees: project.degrees,
      extractivism_types: extractivism_types,
    }
    const final_project = {...project_data, project_full: project_data}

    let current_paragraphs = {}
    project.paragraphs.forEach((p_idx) => {
      if (!current_paragraphs[p_idx])
        current_paragraphs[p_idx] = {"criteria": []}
      current_paragraphs[p_idx]["is_mentioned"] = true
    })

    criteria_fields.forEach((field) => {
      const values = project[field] || []
      if (!values.length)
        return
      const criteria_obj = criteria[field]

      values.forEach((p_idx) => {
        if (!current_paragraphs[p_idx])
          current_paragraphs[p_idx] = {"criteria": []}
        paragraphs[p_idx - 1].criteria_set.add(field)
        current_paragraphs[p_idx].criteria.push({
          ...criteria_obj,
          "count": 1,
        })
      })
    })

    Object.entries(current_paragraphs).forEach(([p_idx, para_data]) => {
      paragraphs[p_idx - 1].projects.push({
        ...final_project, ...para_data,
      })
    })
  })
  paragraphs.forEach((paragraph) => {
    paragraph.criteria = Array.from(paragraph.criteria_set).map((c_name) => {
      full_criteria[c_name].add(paragraph.idx)
      return {...criteria[c_name], "count": 1}
    })
    delete paragraph.criteria_set
  })
  const final_criteria = {}
  Object.entries(full_criteria).forEach(([c_name, p_set]) => {
    final_criteria[c_name] = Array.from(p_set)
  })

  return {full_paragraphs: paragraphs, full_criteria: final_criteria}
})

function showAll(value){
  // external_paragraphs.value = []
  content_paragraphs.value.is_active = false
  show_all.value = value
  if (value)
    selected_fields.value = []
}

function setSelectedProjects(){
  selected_projects.value = props.full_main.second_criteria?.projects
    .filter(p => p.degrees >= 100)
    .map((p, idx) => p.id || idx) || []
}

onMounted(() => {
  setSelectedProjects()
})

function addField(field) {
  if (selected_fields.value.includes(field)){
    const index = selected_fields.value.indexOf(field)
    selected_fields.value.splice(index, 1)
  }
  else
    selected_fields.value.push(field)
  showAll(false)
}

function closeExternalParagraphs(is_reset=false){
  setSelectedProjects()
  content_paragraphs.value.is_active = false
  if (is_reset)
    external_paragraphs.value = []
}

function openExternalParagraphs(){
  content_paragraphs.value.is_active = true
  selected_fields.value = []
  selected_projects.value = []
}

function changeActiveFilter(){
  if (content_paragraphs.value.is_active)
    closeExternalParagraphs()
  else{
    openExternalParagraphs()
  }
}

watch(content_paragraphs, (new_content) => {
  // console.log("Watching content_paragraphs", new_content)
  if (new_content.is_reset){
    closeExternalParagraphs(true)
    return
  }
  if (!new_content.paragraphs || !new_content.note_id)
    return
  if (!props.note_id)
    return
  if (new_content.note_id !== props.note_id)
    return
  if (new_content.is_active === false)
    return
  console.log("Applying external paragraphs filter", new_content)
  external_paragraphs.value = new_content.paragraphs
  openExternalParagraphs()
  // selected_fields.value = []
  // selected_projects.value = []
  // forced_show.value = true
});

</script>

<template>
  <v-card variant="flat">
    <v-card-title
      class="text-subtitle-1 mt-4 d-flex align-center px-2 flex-wrap ga-2"
    >
      <span class="font-weight-bold">
        Párrafos de la pre-nota:
      </span>
      <CriteriaChip
        v-if="full_main.second_criteria"
        :indirect_criteria="hydrated_data.full_criteria"
        :selected_fields="selected_fields"
        is_filter
        @add-field="addField"
        class="ml-3"
      />
      <ProjectsCriteria
        v-if="full_main.second_criteria"
        :criteria="full_main.second_criteria"
        show_full
        :selected_projects="selected_projects"
        @update:selected_projects="selected_projects = $event"
      />
      <v-btn
        v-if="external_paragraphs.length"
        :variant="content_paragraphs.is_active ? 'elevated' : 'outlined'"
        color="accent"
        @click="changeActiveFilter"
        icon
        size="x-small"
      >
        <v-icon
          size="large"
        >filter_list</v-icon>
        <v-tooltip
          activator="parent"
          position="left"
        >
          <span v-if="!content_paragraphs.is_active">
            Activar filtro de elemento específico
          </span>
          <span v-else>
            Filtro de elemento:
            <br> {{ content_paragraphs.path }}
            <br> (Haz clic para desactivar)
          </span>
        </v-tooltip>
      </v-btn>
      <v-spacer></v-spacer>

      <v-btn
        v-if="!show_init && !external_paragraphs.length && !two_columns"
        variant="outlined"
        color="accent"
        @click="forced_show = !forced_show"
        :append-icon="forced_show ? 'expand_less' : 'expand_more'"
      >
        {{ forced_show ? 'Ocultar' : 'Mostrar' }}
        párrafos
      </v-btn>
    </v-card-title>

    <v-card-text
      class="px-0 d-flex flex-wrap"
      v-if="show_init || forced_show || two_columns"
    >
      <Paragraph
        v-for="paragraph in hydrated_data.full_paragraphs"
        :key="paragraph.idx"
        :paragraph="paragraph"
        :selected_fields="selected_fields"
        :external_paragraphs="external_paragraphs"
        :active_external="content_paragraphs.is_active"
        :loading="sending_link"
        @show-all="showAll(true)"
      >
      </Paragraph>
      <v-btn
        v-if="show_all"
        variant="outlined"
        color="accent"
        @click="showAll(false)"
      >
        Ocultar párrafos
      </v-btn>
    </v-card-text>
  </v-card>
</template>
