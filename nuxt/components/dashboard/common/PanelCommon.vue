<script setup>
import {ref, computed, nextTick} from 'vue'
import {useMainStore} from "~/store/index.js";

const mainStore = useMainStore()
const { getSimple } = mainStore

const props = defineProps({
  main: Object,
  group: Object,
  name_field: {
    type: String,
    default: 'name',
  },
  sel: Object,
})
// const {  } = storeToRefs(mainStore)
const full_main = ref({})

const openMain = () => {
  const group = props.group
  const real_group = group.parent ? `catalogs/${group.key}` : group.key
  getSimple([real_group, props.main.id]).then((res) => {
    full_main.value = res
    emit('finish-open')
  })
}

const background_color = computed(() => {
  if (!props.group)
    return 'grey-lighten-5'
  const base_color = props.group.color ||
      (props.group.parent ? props.group.parent.color : 'grey')
  return `${base_color}-lighten-5`
})

const emit = defineEmits(['open-panel'])

</script>

<template>
  <v-expansion-panel class="d-flex">
    <v-sheet
      :color="background_color"
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
          Contenido genérico 3
        </v-expansion-panel-text>
      </slot>
    </div>
  </v-expansion-panel>
</template>

<style scoped>

</style>