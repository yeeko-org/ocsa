<script setup>

const q_value = ref('')

</script>

<template>
<!--  <v-responsive>-->
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
          xclick.stop="menu_drawer = !menu_drawer"
          color="white"
          class="mt-1"
        ></v-app-bar-nav-icon>
        <client-only>
          <v-toolbar-title class="d-flex align-center mt-1">
            <div class="d-flex align-center">

              <span class="text-white text-h6 font-weight-bold">
                Mapa OCSA
              </span>
              <v-text-field
                v-model="q_value"
                label="Buscar proyectos"
                outlined
                density="compact"
                clearable
                base-color="white"
                color="white"
                variant="outlined"
                hide-details
                max-width="300"
                min-width="300"
                append-inner-icon="search"
                class="ml-4 my-1"
              ></v-text-field>
            </div>
          </v-toolbar-title>
        </client-only>
        <v-spacer></v-spacer>
        <v-btn
          color="accent"
          append-icon="download"
          variant="elevated"
          size="small"
        >
          Descargar proyectos
        </v-btn>
      </v-app-bar>
      <v-main>
        <v-container fluid class="px-0 pb-0">
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
<!--  </v-responsive>-->
</template>
