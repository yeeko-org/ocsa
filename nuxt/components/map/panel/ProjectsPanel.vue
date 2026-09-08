<script setup>

import {storeToRefs} from "pinia";
import {useDisplay} from "vuetify";
import {
  useMapStore, SHEET_REST_PX, SHEET_MID_SNAP,
} from "~/store/map.js";
import { DrawerRoot, DrawerPortal, DrawerContent, DrawerHandle } from "vaul-vue";
import ProjectsPanelContent from "~/components/map/panel/ProjectsPanelContent.vue";

const { smAndDown } = useDisplay()
const mapStore = useMapStore()
const { targetProjectId, sheetSnap, sheetCoveredPx } = storeToRefs(mapStore)

// Alturas preset del sheet: reposo (solo la barra del contador), media
// pantalla y completa. El snap activo vive en el store para que el mapa
// recalcule su padding lógico en cada cambio.
const SNAP_POINTS = [SHEET_REST_PX, SHEET_MID_SNAP, 1]
const drawerOpen = ref(true)     // el sheet vive siempre montado en móvil

// Abrir un detalle (desde cualquier fuente: buscador, marcador o lista)
// sube el sheet al snap medio: el proyecto queda en la parte visible.
// Al cerrar no lo bajamos: el usuario baja el sheet manualmente si quiere.
watch(targetProjectId, (id) => {
  if (id) sheetSnap.value = SHEET_MID_SNAP
})

// Píxeles del mapa que cubre el sheet en su snap actual (vaul mide contra
// window.innerHeight; los px del reposo llegan como string).
function measureCovered() {
  if (typeof window === 'undefined') return
  const snap = sheetSnap.value
  sheetCoveredPx.value = typeof snap === 'string'
    ? Number.parseInt(snap, 10)
    : Math.round((snap || 0) * window.innerHeight)
}
watch(sheetSnap, measureCovered, { immediate: true })
onMounted(() => window.addEventListener('resize', measureCovered))
onUnmounted(() => window.removeEventListener('resize', measureCovered))

// reka-ui cierra un Dialog no modal cuando el foco sale de él (focusin en
// cualquier botón del mapa), y vaul solo veta el pointerdown externo:
// `dismissible=false` no cubre ese camino. Vetamos el focus-outside aquí.
function keepOpen(event) {
  event.preventDefault()
}

</script>

<template>
  <client-only>
    <!-- Escritorio: tarjeta flotante abajo-derecha -->
    <v-card
      v-if="!smAndDown"
      class="projects-panel"
      width="400"
      elevation="5"
    >
      <ProjectsPanelContent/>
    </v-card>

    <!-- Móvil: bottom-sheet (vaul-vue, headless). Toda la superficie
         arrastra; vaul arbitra contra el scroll interno de la lista. -->
    <DrawerRoot
      v-else
      v-model:open="drawerOpen"
      v-model:activeSnapPoint="sheetSnap"
      :snap-points="SNAP_POINTS"
      :modal="false"
      :dismissible="false"
    >
      <DrawerPortal>
        <DrawerContent class="panel-drawer" @focus-outside="keepOpen">
          <DrawerHandle class="panel-drawer__handle"/>
          <ProjectsPanelContent embedded/>
        </DrawerContent>
      </DrawerPortal>
    </DrawerRoot>
  </client-only>
</template>

<style scoped>

.projects-panel {
  position: absolute;
  right: 12px;
  bottom: 0;
  z-index: 2;
}

/* Bottom-sheet móvil: vaul es headless, aportamos el estilo del panel.
   vaul controla el transform/translate según el snap; nosotros damos
   tamaño y aspecto. La altura debe ser la del viewport: vaul traslada el
   sheet desde su borde superior en `innerHeight - snap`, así que con menos
   altura el reposo en px quedaba fuera de pantalla. */
.panel-drawer {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 100dvh;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 16px 16px 0 0;
  box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.18);
  z-index: 1000;
  overflow: hidden;
}

.panel-drawer__handle {
  flex: 0 0 auto;
  margin: 5px auto;
}

</style>
