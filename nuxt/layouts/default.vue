<script setup>
import {useMainStore} from '~/store/index'
const mainStore = useMainStore()

const { exportData } = mainStore
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
        v-if="false"
        xclick.stop="menu_drawer = !menu_drawer"
        color="white"
        class="mt-1"
      ></v-app-bar-nav-icon>
      <client-only>
        <v-toolbar-title class="d-flex align-center mt-1">
          <div class="d-flex align-center">
            <a href="https://ocsa.ibero.mx" class="text-decoration-none">
              <span
                class="text-white text-h4 font-weight-bold"
              >
                OCSA
              </span>
            </a>
<!--            <v-text-field-->
<!--              v-model="q_value"-->
<!--              label="Buscar proyectos"-->
<!--              outlined-->
<!--              density="compact"-->
<!--              clearable-->
<!--              base-color="white"-->
<!--              color="white"-->
<!--              variant="outlined"-->
<!--              hide-details-->
<!--              max-width="300"-->
<!--              min-width="300"-->
<!--              append-inner-icon="search"-->
<!--              class="ml-4 my-1"-->
<!--            ></v-text-field>-->
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
