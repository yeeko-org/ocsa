<script setup>
// Layout de pantalla completa para el mapa: sin barra ni chrome.
// La UI (marca, búsqueda, filtros, panel) flota sobre el lienzo dentro
// de la propia página `pages/mapa.vue`. Sigue la convención del repo:
// el layout renderiza su propio <v-app> + <NuxtPage/> (no usa <slot/>).

// Bloquea el scroll del documento SOLO mientras el mapa está montado.
// Antes esto vivía como `html { overflow: hidden }` en un <style> global
// (sin scoped) de mapa.vue, que se filtraba a toda la app y mataba el
// scroll del dashboard. useHead añade la clase al <html> mientras este
// layout está activo y Nuxt la retira solo al desmontarlo. La regla
// `html.map-no-scroll` vive en el CSS global (vuetify-overrides.css) y
// solo aplica cuando esta clase existe.
useHead({ htmlAttrs: { class: 'map-no-scroll' } })
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
