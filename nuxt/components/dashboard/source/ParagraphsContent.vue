<script setup>

import {defineComponent} from "vue";
import CriteriaChip from "~/components/dashboard/source/CriteriaChip.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import {useMainStore} from "~/store/index.js";

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

const fields = [
  'opponents',
  'social_impacts',
  'ecological_impacts',
  'acts_of_violence',
  'collective_actions',
]

const show_all = ref(false)
const selected_fields = ref([])
const forced_show = ref(false)

function showAll(value){
  show_all.value = value
  if (value)
    selected_fields.value = []
}

const full_paragraphs = computed(() => {
  const criteria_values = props.full_main.criteria || []
  let paragraphs = props.full_main.paragraphs.map((p, idx) => {
    return {
      "idx": idx + 1,
      "text": p,
      "criteria": [],
      "projects": [],
    }
  })
  let image_idx = paragraphs.length + 1
  const images = props.full_main.images || []
  images.forEach((image, idx) => {
    if (image.caption) {
      paragraphs.push({
        "image": image.src,
        "idx": image_idx + idx,
        "text": image.caption,
        "criteria": [],
        "projects": [],
      })
    }
  })
  fields.forEach((field) => {
    const criteria_obj = criteria[field]
    const values = criteria_values[field] || []
    values.forEach((p_idx) => {
      paragraphs[p_idx - 1].criteria.push({
        ...criteria_obj,
        "count": 1,
      })
    })
  })
  criteria_values.projects.forEach((project) => {
    const name_types = project.types
    let extractivism_types = name_types.map(type => {
      return ai_extractivism_types[type]
    })
    const project_data = {
      name: project.name,
      extractivism_types: extractivism_types,
    }
    project.paragraphs.forEach((p_idx) => {
      paragraphs[p_idx - 1].projects.push({
        ...project_data,
        "project_full": project_data,
      })
    })

  })

  return paragraphs
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
        v-if="full_main.criteria"
        :main="full_main"
        :selected_fields="selected_fields"
        is_filter
        @reset-filters="showAll(false)"
        class="ml-3"
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
        v-for="paragraph in full_paragraphs"
      >
        <v-card
          v-if="show_all || (selected_fields.length
            ? paragraph.criteria.some(c => selected_fields.includes(c.name))
            : (paragraph.criteria.length || paragraph.projects.length) )"
          :key="paragraph.idx"
          variant="outlined"
          class="mb-1"
          color="grey-lighten-1"
          :loading="sending_link"
          style="width: 100%;"
        >
          <v-card-text class="pb-1 pt-2 text-black">
            <div class="d-flex">
              <CriteriaChip
                is_simple
                :direct_criteria="paragraph.criteria"
              />
              <ProjectMiniList
                :mentions="paragraph.projects"
              />
            </div>
            <b v-if="paragraph.image">[IMAGEN]</b>
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
