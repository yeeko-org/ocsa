<script setup>

import {useMainStore} from "~/store/index.js";
import CriteriaChip from "~/components/dashboard/source/CriteriaChip.vue";
import ParagraphsContent from "~/components/dashboard/source/ParagraphsContent.vue";
import PanelList from "~/components/dashboard/common/PanelList.vue";
import { storeToRefs } from "pinia";
import ProjectsCriteria from "~/components/dashboard/source/article/ProjectsCriteria.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";

const mainStore = useMainStore()
const { saveSelected, valid_options } = mainStore
const { schemas, other_discarded_reason } = storeToRefs(mainStore)

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

const note_collection = computed(() => {
  return schemas.value.collections_dict['note']
})

const rules = ref({
  required: value => !!value || "Campo requerido",
  defined: value => value !== undefined || "Debes seleccionar una opción",
})


const pre_valid = computed(() => {
  return props.full_main.certainty_degree > 100
})

const pre_valid_value = computed(() => {
  const degree = props.full_main.certainty_degree
  if (degree === undefined || degree === null)
    return null
  if (degree <= 100)
    return 1
  else
    return 2
})

const note_full = ref(null)

async function changeSelected(){
  errors.value = null
  // const { valid } = await linkForm.value.validate()
  // if (!valid) return
  const is_selected = props.full_main.is_selected
  const discarded_reason = props.full_main.discarded_reason
  const other_reason = props.full_main.other_discarded_reason
  // console.log("other_reason", other_reason)
  // if (is_selected === false && !other_reason && pre_valid.value) {
  //   errors.value = ["Debes escribir una razón de descarte."]
  //   return
  // }
  // const has_reason =
  if (!discarded_reason && is_selected === false) {
    errors.value = ["Debes seleccionar una razón de descarte."]
    return
  }
  if (need_manual_discard.value && !other_reason) {
    errors.value = ["Debes escribir una razón de descarte."]
    return
  }

  const params = {is_selected, discarded_reason, "other_discarded_reason": other_reason}
  sending_link.value = true
  // console.log("params", params)
  saveSelected([props.full_main.id, params]).then(response => {
    // console.log("response", response)
    if (response.errors)
      errors.value = response.errors

    if (response.note_full)
      note_full.value = response.note_full

    emits('item-saved', {'res': response, is_new: false})
    // props.full_main = {...props.full_main, ...response}
    sending_link.value = false
    // note_content.value = response
  })
}

const need_manual_discard = computed(() => {
  // full_main.discarded_reason && full_main.discarded_reason === other_discarded_reason.id
  if (props.full_main.is_selected !== false)
    return false
  if (!pre_valid.value)
    return false
  if (!other_discarded_reason.value)
    return true
  if (!props.full_main.discarded_reason)
    return false
  return props.full_main.discarded_reason === other_discarded_reason.value.id
})

const label_other_reason = computed(() => {
  return need_manual_discard.value
    ? "Explica por qué se descartó"
    : "Si gustas, explica la razón"
})

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
      label="Subtítulo de la pre-nota"
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
      <SelectGroup
        v-if="full_main.is_selected === false && pre_valid"
        :main_object="full_main"
        filter_group_name="discarded_reasons"
        main_collection_name="article"
        :width="220"
      />
    </div>
    <v-card
      v-if="full_main.is_selected === false && pre_valid"
      variant="flat"
      class="ml-4 pt-2"
      style="max-width: 400px; min-width: 240px;"
    >
      <v-textarea
        v-model="full_main.other_discarded_reason"
        :label="label_other_reason"
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
  <v-col v-if="full_main.note_full || note_full" cols="12" class="px-0">
    <span class="text-subtitle-1 font-weight-bold">
      Nota en la que se menciona:
    </span>
    <PanelList
      :results="[full_main.note_full || note_full]"
      :collection_data="note_collection"
      :show_details="true"
    />
  </v-col>

  <v-col
    v-if="full_main.qualifications && full_main.qualifications.length"
    cols="12"
    class="px-0"
  >
    Alternativas:
    <v-card
      v-for="qualy in full_main.qualifications"
      :key="qualy.id"
      class="pa-2 mb-2"
      variant="outlined"
    >
      <div class="d-flex align-center mb-2">

        <CriteriaChip
          :main="qualy"
          show_negatives
        />
        <ProjectsCriteria
          :criteria="qualy.criteria"
        />
        <div class="ml-4">
          ({{qualy.qualify_schema}})
          {{qualy.change_value}}
          {{qualy.certainty_degree}}
        </div>
      </div>

    </v-card>
  </v-col>

  <v-col cols="12" class="px-0">
    <ParagraphsContent
      :full_main="full_main"
      :sending_link="sending_link"
    />
  </v-col>
</template>