<script setup>

import CriteriaChip from "~/components/dashboard/source/CriteriaChip.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import { useMainStore } from "~/store/index.js";
import ProjectsCriteria from "~/components/dashboard/source/article/ProjectsCriteria.vue";

const mainStore = useMainStore()
const { criteria, ai_extractivism_types } = mainStore

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  sending_link: {
    type: Boolean,
    default: false,
  },
  show_init: {
    type: Boolean,
    default: true,
  }
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

function showAll(value){
  show_all.value = value
  if (value)
    selected_fields.value = []
}

onMounted(() => {
  selected_projects.value = props.full_main.second_criteria?.projects
    .filter(p => p.degrees >= 100)
    .map((p, idx) => p.id || idx) || []
})


const hydrated_data = computed(() => {
  let paragraphs = props.full_main.paragraphs.map((p, idx) => {
    return {
      "idx": idx + 1,
      "text": p,
      "criteria": [],
      "criteria_set": new Set(),
      "projects": [],
    }
  })
  let full_criteria = {}
  criteria_fields.forEach((field) => {
    full_criteria[field] = new Set()
  })
  let image_idx = paragraphs.length + 1
  const images = props.full_main.images || []
  images.forEach((image, idx) => {
    if (image.caption) {
      paragraphs.push({
        "image": image.src,
        "show_image": false,
        "idx": image_idx + idx,
        "text": `${image.caption} (pie de foto)`,
        "criteria": [],
        "criteria_set": new Set(),
        "projects": [],
      })
    }
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

</script>

<template>
  <v-card variant="flat">
    <v-card-title
      class="text-subtitle-1 mt-4 d-flex align-center px-2 flex-wrap"
    >
      <span class="font-weight-bold">
        Párrafos de la pre-nota:
      </span>
      <CriteriaChip
        v-if="full_main.second_criteria"
        :indirect_criteria="hydrated_data.full_criteria"
        :selected_fields="selected_fields"
        is_filter
        @reset-filters="showAll(false)"
        class="ml-3"
      />
      <ProjectsCriteria
        v-if="full_main.second_criteria"
        :criteria="full_main.second_criteria"
        show_full
        :selected_projects="selected_projects"
        @update:selected_projects="selected_projects = $event"
      />
      <v-spacer></v-spacer>

      <v-btn
        v-if="!show_init"
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
      v-if="show_init || forced_show"
    >
      <template
        v-for="paragraph in hydrated_data.full_paragraphs"
      >
        <v-card
          v-if="show_all || (selected_fields.length
            ? paragraph.criteria.some(c => selected_fields.includes(c.name))
            : (paragraph.projects.length) )"
          :key="paragraph.idx"
          variant="outlined"
          class="mb-1"
          color="grey-lighten-1"
          :loading="sending_link"
          style="width: 100%;"
        >
          <v-card-text class="pb-1 pt-2 text-black">
            <div class="d-flex" v-for="project in paragraph.projects">
              <ProjectMiniList
                :mentions="[project]"
                show_full
              />
              <CriteriaChip
                is_simple
                :direct_criteria="project.criteria"
              />
            </div>
            <template v-if="paragraph.image">

              <v-btn
                variant="text"
                size="small"
                @click="paragraph.show_image = !paragraph.show_image"
              >
                [IMAGEN]
              </v-btn>
              <v-img
                v-if="paragraph.show_image"
                :src="paragraph.image"
                class="my-2"
                max-height="400"
                contain
              >
              </v-img>
            </template>
            <span v-html="paragraph.text" class="text-body-1">
            </span>
          </v-card-text>
        </v-card>
        <v-btn
          v-else
          :key="paragraph.idx"
          class="mb-1"
          variant="text"
          color="accent"
          icon
          @click="showAll(true)"
        >
          <v-icon>subject</v-icon>
          <v-tooltip
            activator="parent"
            location="bottom"
            :max-width="400"
          >
            <v-card
              class="mx-n4 my-n2"
            >
              <v-card-title class="text-subtitle-1">
                {{ paragraph.idx }}. Click para ver todos los párrafos
              </v-card-title>
              <v-card-text>
                {{ paragraph.text }}
              </v-card-text>
            </v-card>
          </v-tooltip>
        </v-btn>
      </template>
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
