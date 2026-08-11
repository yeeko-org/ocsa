<script setup>

import {storeToRefs} from "pinia";
import {useDisplay} from "vuetify";
import {useMapStore} from "~/store/map.js";
import { DrawerRoot, DrawerPortal, DrawerContent, DrawerHandle } from "vaul-vue";
import ProjectsPanelContent from "~/components/map/panel/ProjectsPanelContent.vue";

const { smAndDown } = useDisplay()
const mapStore = useMapStore()
const { targetProjectId } = storeToRefs(mapStore)

// Fracción visible del sheet en "peek" (solo la barra del contador).
const PEEK = 0.12
const drawerOpen = ref(true)     // el sheet vive siempre montado en móvil
const activeSnap = ref(PEEK)

// Abrir un detalle (desde cualquier fuente: buscador, marcador o lista)
// sube el sheet a pantalla casi completa. Al cerrar no lo bajamos: el
// usuario queda en la lista y baja el sheet manualmente si quiere.
watch(targetProjectId, (id) => {
  if (id) activeSnap.value = 1
})

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

    <!-- Móvil: bottom-sheet (vaul-vue, headless) -->
    <DrawerRoot
      v-else
      v-model:open="drawerOpen"
      v-model:activeSnapPoint="activeSnap"
      :snap-points="[PEEK, 1]"
      :modal="false"
      :dismissible="false"
      handle-only
    >
      <DrawerPortal>
        <DrawerContent class="panel-drawer">
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
   tamaño y aspecto. */
.panel-drawer {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  height: 92vh;
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
}

</style>