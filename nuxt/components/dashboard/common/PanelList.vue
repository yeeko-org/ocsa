<script setup>

import PanelCommon from "~/components/dashboard/common/PanelCommon.vue";

import {ref, computed, shallowRef, nextTick} from 'vue'

const props = defineProps({
  results: Array,
  collection_data: Object,
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

const route_key = computed(() => props.collection_data.app_label)
const snake_name = computed(() => props.collection_data.snake_name)
const header_name = computed(() => `${props.collection_data.model_name}Header`)
const sheet_name = computed(() => `${props.collection_data.model_name}Sheet`)
const edit_name = computed(() => `${props.collection_data.model_name}Edit`)

import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${header_name.value}.vue`)
  .then(module => {
    header_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/generic/HeaderGeneric.vue`).then(module => {
      header_component.value = module.default
    })
  })

import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${sheet_name.value}.vue`)
  .then(module => {
    sheet_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/generic/SheetCommon.vue`).then(module => {
      sheet_component.value = module.default
    })
  })

import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${edit_name.value}.vue`)
  .then(module => {
    edit_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/generic/EditGeneric.vue`).then(module => {
      edit_component.value = module.default
    })
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
      :collection_data="collection_data"
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
          :group="collection_data"
          :show_details="show_details"
          @open-panel="openMain"
        />
      </template>
      <template
        #edit="{full_main}"
      >
        <component
          :is="edit_component"
          :full_main="full_main"
          is_edit
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
          :collection_data="collection_data"
        />
      </template>
    </PanelCommon>
  </v-expansion-panels>
</template>

<style scoped>

</style>