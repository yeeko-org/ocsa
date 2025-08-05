<script setup>

import {useMainStore} from "~/store/index.js";
import CriteriaChip from "~/components/dashboard/source/CriteriaChip.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";

const mainStore = useMainStore()
const { criteria, ai_extractivism_types, saveSelected } = mainStore

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
})

const errors = ref(null)
const sending_link = ref(false)

const rules = ref({
  required: value => !!value || "Campo requerido",
  defined: value => value !== undefined || "Debes seleccionar una opción",
})

const fields = [
  'opponents',
  'social_impacts',
  'ecological_impacts',
  'acts_of_violence',
  'collective_actions',
]

const valid_options = [
  {
    "id": 1,
    "name": "No cumple",
    "order": 1,
    "icon": "close",
    "color": "error",
    "value": false,
  },
  {
    "id": 2,
    "name": "Sí cumple",
    "order": 2,
    "icon": "verified",
    "color": "success",
    "value": true,
  },
]

const show_all = ref(false)

const pre_valid_value = computed(() => {
  const degree = props.full_main.certainty_degree
  if (degree === undefined || degree === null)
    return null
  if (degree <= 10)
    return 1
  else
    return 2
})

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
  props.full_main.images.forEach((image, idx) => {
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


async function changeSelected(){
  errors.value = null
  // const { valid } = await linkForm.value.validate()
  // if (!valid) return
  sending_link.value = true
  console.log("full_main", props.full_main)
  // const elem_id = props.full_main.id ? 'id' : 'key_name'
  // const is_new = !Boolean(props.full_main[elem_id])
  const params = {
    "is_selected": props.full_main.is_selected,
  }
  // console.log("params", params)
  saveSelected([props.full_main.id, params]).then(response => {
    console.log("response", response)
    if (response.errors)
      errors.value = response.errors
    // if (response.note_contents){
    //   // props.full_main.note_contents.concat(response.note_contents)
    //   response.note_contents.forEach(note_content => {
    //     props.full_main.note_contents.push(note_content)
    //   })
    // }

    // emits('item-saved', {'res': response, is_new})
    sending_link.value = false
    // note_content.value = response
  })
}

</script>

<template>
  <v-col cols="12" class="d-flex">
    <v-text-field
      v-model="full_main.url"
      label="Enlace a la nota"
      variant="outlined"
      class="mr-2"
      style="max-width: 600px;"
    >
      <template #append v-if="full_main.url">
        <v-btn
          color="accent"
          variant="outlined"
          icon="open_in_new"
          :href="full_main.url"
          target="_blank"
          v-tooltip:bottom="'Abrir enlace'"
        ></v-btn>
      </template>
    </v-text-field>

    <div class="d-flex flex-column ml-6 justify-center">
      <span class="text-caption text-grey-darken-1">
        ¿Cumple los criterios de selección?
      </span>

      <v-btn-toggle
        v-model="pre_valid_value"
        variant="elevated"
        color="grey-lighten-4"
        style="margin-left: 2px;"
        class="mb-n2"
        density="compact"
      >
        <v-btn
          v-for="option in valid_options"
          :key="option.id"
          :color="option.color"
          class="text-caption"
          :value="option.id"
          :prepend-icon="option.icon"
          disabled
        >
          {{option.name}}
        </v-btn>
      </v-btn-toggle>
      <v-input
        v-if="true"
        v-model="full_main.is_selected"
        label="Válido"
        type="text"
        :rules="[rules.defined]"
      >
        <v-btn-toggle
          v-model="full_main.is_selected"
          :rules="[rules.defined]"
          variant="elevated"
          border
          divided
          color="grey-lighten-3"
          @update:model-value="changeSelected"
        >
          <v-btn
            v-for="option in valid_options"
            :key="option.id"
            :color="option.color"
            :value="option.value"
            :prepend-icon="option.icon"
            class="text-caption"
          >
            {{option.name}}

          </v-btn>

        </v-btn-toggle>
      </v-input>
    </div>
  </v-col>
  <v-card-title
    class="text-subtitle-1 mt-4"
  >
    Párrafos del artículo:
  </v-card-title>
  <div
    v-for="paragraph in full_paragraphs"
    :key="paragraph.idx"
    style="width: 100%;"
  >
    <v-card
      v-if="show_all || paragraph.criteria.length || paragraph.projects.length"
      variant="outlined"
      class="mb-1"
      color="grey-lighten-1"
      :loading="sending_link"
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
      v-if="!show_all && !paragraph.criteria.length"
      class="mb-1"
      variant="text"
      color="accent"
      icon
      @click="show_all = true"
    >
      <v-icon>horizontal_rule</v-icon>
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
  </div>
  <v-btn
    v-if="show_all"
    variant="outlined"
    color="accent"
    @click="show_all = false"
  >
    Ocultar párrafos
  </v-btn>
</template>

<style scoped>

</style>