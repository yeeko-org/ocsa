<script setup>

import {useMainStore} from "~/store/index.js";
import CriteriaChip from "~/components/dashboard/source/CriteriaChip.vue";
import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";

const mainStore = useMainStore()
const { criteria, ai_extractivism_types, saveSelected, valid_options } = mainStore

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  is_massive_edit: Boolean,
  is_edit: Boolean,
})

const emits = defineEmits(['item-saved'])
const errors = ref(null)
const sending_link = ref(false)
const selected_fields = ref([])

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


const show_all = ref(false)

const pre_valid = computed(() => {
  return props.full_main.certainty_degree > 10
})

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

function showAll(value){
  show_all.value = value
  if (value)
    selected_fields.value = []
}

async function changeSelected(){
  errors.value = null
  // const { valid } = await linkForm.value.validate()
  // if (!valid) return
  const is_selected = props.full_main.is_selected
  const other_reason = props.full_main.other_discarded_reason
  // console.log("other_reason", other_reason)
  if (is_selected === false && !other_reason && pre_valid.value) {
    errors.value = ["Debes escribir una razón de descarte."]
    return
  }

  const params = {is_selected, "other_discarded_reason": other_reason}
  sending_link.value = true
  // console.log("params", params)
  saveSelected([props.full_main.id, params]).then(response => {
    // console.log("response", response)
    if (response.errors)
      errors.value = response.errors

    emits('item-saved', {'res': response, is_new: false})
    sending_link.value = false
    // note_content.value = response
  })
}

</script>

<template>
  <v-col
    class="px-0 grow"
  >
    <v-textarea
      v-model="full_main.url"
      label="Enlace a la nota"
      variant="outlined"
      class="mr-2"
      rows="1"
      auto-grow
      max-rows="3"
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
    </v-textarea>
    <v-textarea
      v-model="full_main.subtitle"
      label="Subtítulo del artículo"
      variant="outlined"
      class="mr-2"
      rows="2"
      max-rows="3"
      auto-grow
      max-width="500px"
      hide-details
    >
    </v-textarea>

  </v-col>
  <v-col
    class="d-flex px-0"
    style="min-width: 500px;"
  >

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
        v-model="full_main.is_selected"
        label="Válido"
        type="text"
        :rules="[rules.defined]"
        :error-messages="errors"
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
    <v-card
      v-if="full_main.is_selected === false && pre_valid"
      variant="flat"
      class="ml-4 pt-2"
      style="max-width: 400px; min-width: 240px;"
    >
      <v-textarea
        v-model="full_main.other_discarded_reason"
        label="Razón de descarte"
        variant="solo-filled"
        color="red-darken-1"
        bg-color="red-lighten-4"
        rows="2"
        auto-grow
      >
      </v-textarea>
      <v-btn
        v-if="!full_main.is_selected"
        color="accent"
        variant="outlined"
        @click="changeSelected"
        :loading="sending_link"
      >
        Guardar
      </v-btn>
    </v-card>
  </v-col>
  <v-col cols="12" class="px-0">

    <v-card-title
      class="text-subtitle-1 mt-4 d-flex align-center"
    >
      Párrafos del artículo:
      <CriteriaChip
        v-if="full_main.criteria"
        :main="full_main"
        :selected_fields="selected_fields"
        is_filter
        @reset-filters="showAll(false)"
        class="ml-3"
      />
    </v-card-title>
    <v-card-text
      class="px-0 d-flex flex-wrap"
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
  </v-col>
</template>

<style scoped>

</style>