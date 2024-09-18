<script setup>
import { ref, computed, defineProps } from 'vue'
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";

const mainStore = useMainStore()
const { getSimple } = mainStore

const props = defineProps({
  main: Object,
  group: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  sel: Object,
})
// const {  } = storeToRefs(mainStore)
const full_main = ref({})


const openMain = () => {
  getSimple([props.group.key, props.main.id]).then((res) => {
    full_main.value = res
  })
}

</script>

<template>
  <v-expansion-panel class="d-flex">
    <v-sheet
      :color="`${props.group.color}-lighten-5`"
      class="d-flex align-start flex-shrink-0"
    >
      <v-checkbox
        v-model="sel.selected_elems"
        :value="main.id"
        _density="comfortable"
        hide-details
        class="pt-1 pl-1"
      />
    </v-sheet>
    <div class="flex-grow-1">
      <slot name="header" :main="main" :openMain="openMain">
        <v-expansion-panel-title>
          Título genérico
        </v-expansion-panel-title>
      </slot>
      <slot name="sheet" v-if="full_main" :full_main="full_main">
        <v-expansion-panel-text>
          Contenido genérico
        </v-expansion-panel-text>
      </slot>
    </div>
  </v-expansion-panel>
</template>

<style scoped>

</style>