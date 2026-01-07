<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import CriteriaChip from "~/components/dashboard/source/CriteriaChip.vue";
import {computed} from "vue";
import dayjs from "dayjs";

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import ProjectsCriteria from "~/components/dashboard/source/article/ProjectsCriteria.vue";
const mainStore = useMainStore()
const { ai_extractivism_types, cats, valid_options } =storeToRefs(mainStore)

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
  return cats.value.source.find(src => src.id === props.main.source) || {
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

const pre_valid_value = computed(() => {
  const degree = props.main.certainty_degree
  if (degree === undefined || degree === null)
    return valid_undefined
  if (degree < 100)
    return valid_options.value[0]
  else
    return valid_options.value[1]
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
  return valid_options.value.find(
      option => option.value === props.main.is_selected)
})

const discarded_reason = computed(() => {
  if (props.main.is_selected === false)
    return cats.value.discarded_reason.find(
      reason => reason.id === props.main.discarded_reason
    ) || {
      id: null,
      name: '',
      // description: props.main.other_discarded_reason || 'No especificada',
      description: '',
    }
  return null
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
            max-width="400"
          >
            <v-card
              color="red-lighten-4"
              class="mx-n4 my-n2"
            >
              <v-card-title
                class="text-subtitle-1 text-uppercase"
              >
                Motivo de descarte:
              </v-card-title>
              <v-card-text>
                <div
                  v-if="discarded_reason.name"
                  class="mb-2"
                >
                  <span class="font-weight-bold">
                    {{ discarded_reason.name }}:
                  </span>
                  <span
                    v-if="discarded_reason.description"
                    class="text-grey-darken-3 mb-2"
                  >
                    {{ discarded_reason.description }}
                  </span>
                </div>
                <div
                  v-if="main.other_discarded_reason"
                  class="text-subtitle-1"
                >
                  {{ main.other_discarded_reason }}
                </div>
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
      <div
        v-if="main.qualifications && main.qualifications.length"
      >
        <span
          v-for="qualification in main.qualifications"
          :key="qualification.id"
          class="text-caption mr-1 text-grey-darken-1"
        >
          {{ qualification.certainty_degree }}
        </span>


      </div>
      <CriteriaChip
        v-if="main.criteria"
        :main="main"
        show_negatives
      />
      <ProjectsCriteria
        :criteria="main.criteria"
      />
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>