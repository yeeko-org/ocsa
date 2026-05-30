<script setup>
// Layout de pantalla completa para el mapa: sin barra ni chrome.
// La UI (marca, búsqueda, filtros, panel) flota sobre el lienzo dentro
// de la propia página `pages/mapa.vue`. Sigue la convención del repo:
// el layout renderiza su propio <v-app> + <NuxtPage/> (no usa <slot/>).
</script>

<template>
  <v-app>
    <v-main class="pa-0 map-main">
      <client-only>
        <NuxtPage/>
      </client-only>
    </v-main>
  </v-app>
</template>

<style scoped>
.map-main {
  /* Sin offset de app-bar: el mapa ocupa todo el alto del viewport. */
  --v-layout-top: 0px;
}
</style>
