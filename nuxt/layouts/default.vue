<script setup>
// Layout genérico (home y páginas sin layout propio). El mapa usa su
// propio layout 'map' a pantalla completa; aquí no se carga estado del
// mapa para no acoplar la home a esos stores.
const public_links = [
  {
    title: 'Quiénes somos',
    href: 'https://ocsa.ibero.mx/quienes-somos',
  },
  {
    title: 'Mapa',
    href: 'https://ocsa.ibero.mx/mapa',
  },
  {
    title: 'Materiales y publicaciones',
    href: 'https://ocsa.ibero.mx/materiales-y-publicaciones',
  },
  { title: 'Contacto', href: 'https://ocsa.ibero.mx/contacto' },
]
</script>

<template>
  <v-app>
    <v-app-bar app color="primary" dark flat height="52">
      <v-toolbar-title>
        <v-card
          variant="flat"
          color="transparent"
          class="cursor-pointer"
          href="https://ocsa.ibero.mx"
          min-width="100"
        >
          <span class="text-white text-h5 font-weight-bold">OCSA</span>
          <v-tooltip activator="parent" location="bottom">
            Ir al inicio del sitio del OCSA
          </v-tooltip>
        </v-card>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-menu location="bottom">
        <template v-slot:activator="{ props }">
          <v-btn icon="more_vert" v-bind="props"></v-btn>
        </template>
        <v-list>
          <v-list-item
            v-for="link in public_links"
            :key="link.href"
            :href="link.href"
            :title="link.title"
          ></v-list-item>
        </v-list>
      </v-menu>
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
