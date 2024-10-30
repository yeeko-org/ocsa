<script setup>
import {ref, computed, nextTick} from 'vue'
import {useMainStore} from "~/store/index.js";
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";

const mainStore = useMainStore()
const { getSimple, saveSimple, editSimple } = mainStore

const props = defineProps({
  main: Object,
  collection_data: Object,
  name_field: {
    type: String,
    default: 'name',
  },
  sel: Object,
})

const full_main = ref({})

const emit = defineEmits(['finish-open'])

const final_snake_name = computed(() => {
  let snake_name = props.collection_data.snake_name
  const level = props.collection_data.level
  if (level.includes('category'))
    snake_name = `catalogs/${snake_name}`
  return snake_name
})


const openMain = () => {
  // const group = props.group
  // const real_group = group.parent ? `catalogs/${group.key}` : group.key
  const level = props.collection_data.level
  console.log('level', level)
  if (level === 'category_group'){
    emit('finish-open')
    return
  }
  getSimple([final_snake_name.value, props.main.id]).then((res) => {
    full_main.value = res
    emit('finish-open')
  })
}

const background_color = computed(() => {
  const coll = props.collection_data
  if (!coll)
    return 'secondary-lighten-5'
  const base_color = coll.color ||
    (coll.parent ? (coll.parent.color || 'blue-grey') : 'blue-grey')
  return `${base_color}-lighten-5`
})

function saveRecord() {
  const snake_name = final_snake_name.value
  saveSimple([snake_name, full_main.value]).then((res) => {
    console.log('res', res)
  })

}

</script>

<template>
  <v-expansion-panel class="d-flex">
    <v-sheet
      :color="background_color"
      class="d-flex align-start flex-shrink-0"
    >
      <v-checkbox
        v-if="sel"
        v-model="sel.selected_elems"
        :value="main.id"
        _density="comfortable"
        hide-details
        class="pt-1 pl-1"
      />
      <div v-else style="width: 40px;">

      </div>
    </v-sheet>
    <div class="flex-grow-1">
      <slot name="header" :main="main" :openMain="openMain">
        <v-expansion-panel-title>
          Cargando detalles...
        </v-expansion-panel-title>
      </slot>
      <v-expansion-panel-text
        v-if="full_main"
        class="ml-n16 mr-n6"
        :color="`${background_color}-lighten-5`"
      >
        <v-sheet
          :color="`${background_color}-lighten-5`"
          class="mt-n2 mb-n4 pa-3"
        >
          <v-card class="mb-3 pa-3" elevation="8">
            <v-card-text
              class="d-flex flex-wrap"
            >

              <div class="d-flex" style="width: 100%;">
                <v-text-field
                  v-model="full_main.name"
                  label="Nombre"
                  class="mr-2"
                  style="width: 300px;"
                />
                <v-spacer></v-spacer>
                <template v-if="collection_data.status_groups">
                  <StatusDetail
                    v-for="status_group in collection_data.status_groups"
                    :final_filters="full_main"
                    :collection="status_group"
                    style="max-width: 300px;"
                    density="default"
                  />
                </template>

              </div>

              <slot name="edit" :full_main="full_main">
                EDICIÓN (REVISAR PORQUE NO ES NORMAL)
              </slot>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="accent"
                variant="elevated"
                @click="saveRecord"
              >
                Guardar
              </v-btn>
            </v-card-actions>
          </v-card>
          <slot name="sheet" :full_main="full_main">
            Contenido genérico 3
          </slot>
        </v-sheet>
      </v-expansion-panel-text>
    </div>
  </v-expansion-panel>
</template>

<style scoped>

</style>