<script setup>

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {useMapStore} from "~/store/map.js";
import ProjectMiniCard from "~/components/map/ProjectMiniCard.vue";

const mainStore = useMainStore()
const { target_project_id } = storeToRefs(mainStore)
const mapStore = useMapStore()
const { uniqueProjects, selectedExtractivismTypes } = storeToRefs(mapStore)

// Altura fija de cada fila (la comparte v-virtual-scroll y ProjectMiniCard).
const ITEM_HEIGHT = 76

const expanded = ref(false)

// Mismo criterio de filtrado que useMapLayers: el contador siempre
// coincide con lo que se ve en el mapa.
const filteredProjects = computed(() => {
  const selected = selectedExtractivismTypes.value
  if (!selected.length)
    return uniqueProjects.value
  return uniqueProjects.value.filter(p =>
    selected.some(set => p.extractivism_type_ids.includes(set))
  )
})

const projectCount = computed(() => filteredProjects.value.length)

const countLabel = computed(() =>
  `${projectCount.value} ${projectCount.value === 1 ? 'Proyecto' : 'Proyectos'}`
)

function selectProject(project) {
  // Dispara el watch de target_project_id en mapa.vue (vuela + abre card).
  target_project_id.value = project.id
}

</script>

<template>
  <v-card
    class="projects-display"
    :class="{ 'projects-display--collapsed': !expanded }"
    width="400"
    elevation="8"
  >
    <div
      class="d-flex align-center px-3 py-2"
      :class="{ 'panel-header': expanded }"
    >
      <span class="text-h6 font-weight-bold">{{ countLabel }}</span>
      <v-spacer/>
      <v-btn
        v-if="expanded"
        prepend-icon="download"
        variant="tonal"
        color="green-darken-2"
        size="small"
        class="mr-2"
        v-tooltip="'Descargar datos en Excel'"
      >
        Excel
      </v-btn>
      <v-btn
        :icon="expanded
          ? 'keyboard_double_arrow_down'
          : 'keyboard_double_arrow_up'"
        variant="text"
        density="comfortable"
        v-tooltip="expanded ? 'Ocultar lista' : 'Ver lista de proyectos'"
        @click="expanded = !expanded"
      />
    </div>

    <!-- Lista virtualizada: se despliega desde abajo al expandir -->
    <v-expand-transition>
      <div v-if="expanded">
        <v-divider/>
        <v-virtual-scroll
          :items="filteredProjects"
          :item-height="ITEM_HEIGHT"
          height="80vh"
        >
          <template #default="{ item }">
            <v-card
              class="project-row my-1"
              :class="{ 'project-row--active': item.id === target_project_id }"
              variant="tonal"
              :color="item.color"
              rounded="0"
              :height="ITEM_HEIGHT"
              @click="selectProject(item)"
            >
              <ProjectMiniCard
                :full_main="item"
                :fixed_height="ITEM_HEIGHT"
              />
            </v-card>
          </template>
        </v-virtual-scroll>
      </div>
<!--      <div v-else style="height: 80px">
        Muéstrate
      </div>-->
    </v-expand-transition>
  </v-card>
</template>

<style scoped>

.projects-display {
  position: absolute;
  left: 12px;
  bottom: 0;
  z-index: 2;
}

.projects-display--collapsed {
  background-color: #ffffff80 !important;
}

.panel-header {
  background-color: #f5f5f5;
}

.project-row {
  cursor: pointer;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: filter 0.15s ease;
}

.project-row:hover {
  filter: brightness(0.95);
}

.project-row--active {
  border-left: 4px solid currentColor;
  font-weight: 600;
}

</style>
