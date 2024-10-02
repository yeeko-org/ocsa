<script setup>

import PanelCommon from "~/components/dashboard/common/PanelCommon.vue";

import {ref, computed, shallowRef, nextTick} from 'vue'

const props = defineProps({
  results: Array,
  group: Object,
  sel: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})

const open_panels = ref([])
const main_show_details = ref(false)

const header_component = shallowRef('')
const sheet_component = shallowRef('')
const edit_component = shallowRef('')

const route_key = computed(() => props.group.meta_key || props.group.key)
const header_name = computed(() => props.group.header)
const sheet_name = computed(() => props.group.sheet)
const edit_name = computed(() => props.group.edit)
import(`~/components/dashboard/${route_key.value}/${header_name.value}.vue`).then(module => {
  header_component.value = module.default
})
import(`~/components/dashboard/${route_key.value}/${sheet_name.value}.vue`).then(module => {
  sheet_component.value = module.default
})
import(`~/components/dashboard/${route_key.value}/${edit_name.value}.vue`).then(module => {
  edit_component.value = module.default
})

function changeShowDetails() {
  nextTick(() => {
    setTimeout(() => {
      main_show_details.value = true
    }, 10)
  })
}

</script>

<template>
  <v-expansion-panels
    multiple
    v-model="open_panels"
  >
    <PanelCommon
      v-for="elem in results"
      :key="elem.id"
      :group="group"
      :main="elem"
      :sel="sel"
      @finish-open="changeShowDetails"
    >
      <template
        #header="{openMain}"
        v-if="header_component"
      >
        <component
          :is="header_component"
          :main="elem"
          :group="group"
          :show_details="show_details"
          @open-panel="openMain"
        />
      </template>
      <template
        #sheet="{full_main}"
        v-if="sheet_component"
      >
        <component
          :is="sheet_component"
          :full_main="full_main"
          :show_details="main_show_details"
        />
      </template>
    </PanelCommon>
  </v-expansion-panels>

</template>

<style scoped>

</style>