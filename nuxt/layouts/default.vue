<script setup>
import { storeToRefs } from 'pinia'
import {useMainStore} from '~/store/index'
import {useMapStore} from '~/store/map.js'
const mainStore = useMainStore()
const mapStore = useMapStore()

const { exportData } = mainStore
const { target_project_id } = storeToRefs(mainStore)
const { searchableProjects } = storeToRefs(mapStore)
const q_value = ref('')
const loading_export = ref(false)

function downloadProjects(all_records = true) {
  loading_export.value = true
  const collection_name = 'project'
  let params = {}
  // if (!all_records) {
  //   params = {
  //     ...final_filters.value,
  //     q: q_value.value,
  //     ...props.init_filters,
  //   }
  // }
  exportData([collection_name, params]).then(res => {
    loading_export.value = false
    if (res.cancelled) {
      return
    }
    // console.log("exported data", res)
  })
}

</script>

<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
      flat
      clipped-left
      height="52"
    >
      <v-app-bar-nav-icon
        v-if="true"
        xclick.stop="menu_drawer = !menu_drawer"
        color="white"
        class="mt-1"
      ></v-app-bar-nav-icon>
      <client-only>
        <v-toolbar-title class="d-flex align-center mt-0">
          <div class="d-flex align-center">
            <v-card
              variant="flat"
              color="transparent"
              class="cursor-pointer mt-1"
              href="https://ocsa.ibero.mx"
              min-width="100"
            >
              <span
                class="text-white text-h4 font-weight-bold"
              >
                OCSA
              </span>
              <v-tooltip
                activator="parent"
                location="bottom"
              >
                Ir al Inicio de la página del OCSA
              </v-tooltip>
            </v-card>
            <v-autocomplete
              v-model="target_project_id"
              :items="searchableProjects"
              item-title="label"
              item-value="id"
              label="Buscar proyectos"
              density="compact"
              base-color="white"
              color="white"
              variant="outlined"
              hide-details
              menu-icon=""
              append-inner-icon="search"
              max-width="300"
              min-width="300"
              class="ml-4 my-1"
              clearable
            ></v-autocomplete>
          </div>
        </v-toolbar-title>
      </client-only>
      <v-spacer></v-spacer>
      <v-btn
        color="accent"
        append-icon="download"
        variant="elevated"
        size="small"
        :loading="loading_export"
        @click="downloadProjects()"
      >
        Descargar proyectos
      </v-btn>
      <template v-slot:append>
        <v-menu location="bottom">
          <template v-slot:activator="{props}">
            <v-btn icon="more_vert" v-bind="props">

            </v-btn>
          </template>
          <v-list>
            <v-list-item href="https://ocsa.ibero.mx/quienes-somos">
              <v-list-item-title>Quiénes somos</v-list-item-title>
            </v-list-item>
            <v-list-item href="https://ocsa.ibero.mx/materiales-y-publicaciones">
              <v-list-item-title>Materiales y publicaciones</v-list-item-title>
            </v-list-item>
            <v-list-item href="https://ocsa.ibero.mx/contacto">
            <v-list-item-title>Contacto</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-app-bar>
    <v-main>
      <v-container fluid class="pa-0">
        <v-layout
          align-center justify-center fill-height
        >
          <client-only>
            <NuxtPage/>
          </client-only>
        </v-layout>
      </v-container>
    </v-main>
  </v-app>
</template>
