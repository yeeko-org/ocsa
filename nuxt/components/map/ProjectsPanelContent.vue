<script setup>

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
import {useMapStore} from "~/store/map.js";
import ProjectMiniCard from "~/components/map/ProjectMiniCard.vue";
import ProjectDetailMap from "~/components/map/ProjectDetailMap.vue";

// `embedded` = el contenido vive dentro del bottom-sheet (móvil). En ese
// modo el sheet (vaul) gobierna mostrar/ocultar vía snap points, así que
// el cuerpo nunca se colapsa a "pill" ni muestra el botón de expandir.
const props = defineProps({
  embedded: Boolean,
})

const mainStore = useMainStore()
const { getSimple, exportData } = mainStore
const mapStore = useMapStore()
const {
  uniqueProjects,
  targetProjectId,
  projectLocations,
  readyGets,
} = storeToRefs(mapStore)

// Altura fija de cada fila
const ITEM_HEIGHT = 76

const expanded = ref(false)

// Cuatro refs que modelan la pila de navegación:
//  - selectedParentProject / parentProject: el frame "primario"
//    (proyecto suelto, agrupador o padre alcanzado desde un hijo).
//  - selectedChildProject / childProject: el frame del hijo (push).
const selectedParentProject = ref(null)
const parentProject = ref(null)
const selectedChildProject = ref(null)
const childProject = ref(null)

const loadingExport = ref(false)

// --- Lista / contador ---
const filteredProjects = computed(() => {
  const selected = mapStore.filters.extractivism
  if (!selected.length)
    return uniqueProjects.value
  return uniqueProjects.value.filter(p =>
    selected.some(set => p.extractivism_type_ids.includes(set))
  )
})

const total = computed(() => uniqueProjects.value.length)
const hasFilter = computed(() => mapStore.filters.extractivism.length > 0)

const countLabel = computed(() => {
  const n = filteredProjects.value.length
  if (!hasFilter.value)
    return `${total.value} proyecto${total.value === 1 ? '' : 's'}`
  return `${n} de ${total.value} proyectos`
})

const dataLoading = computed(() => readyGets.value < 2)

// --- Vista derivada (pila de navegación) ---
// Hay frame de hijo si está seleccionado o ya cargado; hay detalle si
// hay cualquier frame primario o hijo en juego.
const view = computed(() => {
  const inChild = !!(childProject.value || selectedChildProject.value)
  // En el sheet móvil nunca colapsamos a pill: el recorte lo hace el snap.
  if (!expanded.value && !props.embedded) return 'pill'
  if (inChild) return 'child'
  if (selectedParentProject.value) return 'detail'
  return 'list'
})

const listHeight = computed(() =>
  props.embedded ? 'calc(92vh - 128px)' : '70vh')

// Filtra menciones/eventos/impactos del proyecto hijo dentro del payload
// completo del agrupador (que los trae todos mezclados).
function separateCollections(all_project_data, current_project) {
  const mentions = all_project_data.mentions.filter(
    mention => mention.project === current_project.id)
  const mention_ids = mentions.map(mention => mention.id)
  const events = all_project_data.events.filter(
    event => mention_ids.includes(event.mention))
  const impacts = all_project_data.impacts.filter(
    impact => mention_ids.includes(impact.mention))
  return { ...current_project, mentions, events, impacts }
}

// Dado el `properties` de un feature, arma la pila: primero un estado
// optimista (padre o hijo según parent_project), luego completa con el
// fetch de project_map.
function buildFullProjectData(properties) {
  const projectData = typeof properties.project === 'string'
    ? JSON.parse(properties.project)
    : properties.project
  parentProject.value = null
  childProject.value = null
  selectedChildProject.value = null
  selectedParentProject.value = null
  if (projectData.parent_project)
    selectedChildProject.value = { ...properties, project: projectData }
  else
    selectedParentProject.value = { ...properties, project: projectData }
  getSimple(['project_map', projectData.id]).then(res => {
    if (res.parent_project_full) {
      selectedParentProject.value = {
        color: '',
        project: res.parent_project_full,
      }
      parentProject.value = {
        ...res.parent_project_full,
        mentions: res.mentions,
        events: res.events,
        impacts: res.impacts,
      }
      const new_project = separateCollections(
        res, selectedChildProject.value.project)
      childProject.value = { color: '', project: new_project }
    }
    else
      parentProject.value = res
  })
}

// Abre un hijo desde la lista de vinculados del agrupador (push).
function openChildProject(project) {
  selectedChildProject.value = { color: '', project }
  const new_project = separateCollections(parentProject.value, project)
  childProject.value = { color: '', project: new_project }
}

// --- Navegación ---
function selectProject(project) {
  // Dispara el watch de targetProjectId (vuela el mapa) y, abajo, el
  // watch local que arma el detalle.
  targetProjectId.value = project.id
}

function clearDetail() {
  selectedParentProject.value = null
  parentProject.value = null
  selectedChildProject.value = null
  childProject.value = null
}

function backToParent() {
  selectedChildProject.value = null
  childProject.value = null
}

function backToList() {
  targetProjectId.value = null
}

// Fuente de verdad única: el buscador, el clic en marcador y la lista
// cambian targetProjectId; aquí reaccionamos armando (o cerrando) el
// detalle.
watch(targetProjectId, (id) => {
  if (!id) {
    clearDetail()
    return
  }
  expanded.value = true
  const feature = projectLocations.value.features.find(
    f => f.properties.project.id === id)
  if (feature)
    buildFullProjectData(feature.properties)
})

function exportProjects() {
  loadingExport.value = true
  exportData(['project', {}]).then(() => {
    loadingExport.value = false
  })
}

</script>

<template>
  <div class="panel-content">
    <!-- Cabecera: pill / lista -->
    <div
      v-if="view === 'pill' || view === 'list'"
      class="d-flex align-center px-3 py-2"
      :class="{ 'panel-header': view === 'list' }"
    >
      <span class="text-title-large font-weight-bold">{{ countLabel }}</span>
      <v-spacer/>
      <v-btn
        v-if="view === 'list' || view === 'pill'"
        prepend-icon="download"
        variant="tonal"
        color="green-darken-2"
        size="small"
        class="mr-2"
        :loading="loadingExport"
        v-tooltip:top="'Descargar datos en Excel'"
        @click="exportProjects"
      >
        Excel
      </v-btn>
      <v-btn
        v-if="!embedded"
        :icon="expanded
          ? 'keyboard_double_arrow_down'
          : 'keyboard_double_arrow_up'"
        variant="text"
        density="comfortable"
        v-tooltip:top="expanded ? 'Ocultar lista' : 'Ver lista de proyectos'"
        @click="expanded = !expanded"
      />
    </div>

    <!-- Cabecera: detalle / hijo (breadcrumb) -->
    <div
      v-else
      class="d-flex align-center px-2 py-1 panel-header"
    >
      <v-btn
        icon="chevron_left"
        variant="text"
        density="comfortable"
        v-tooltip="view === 'child' ? 'Volver al agrupador' : 'Volver a la lista'"
        @click="view === 'child' ? backToParent() : backToList()"
      />
      <div class="breadcrumb text-truncate text-body-medium d-flex align-center">
        <template v-if="view === 'child'">
          <v-btn
            variant="text"
            color="primary"
            size="small"
            class="text-none px-1"
            @click="backToParent"
          >
            {{ selectedParentProject?.project?.name || 'Volver' }}
          </v-btn>
          <v-icon size="small" class="mx-1">chevron_right</v-icon>
          <span class="font-weight-bold text-truncate">
            {{ selectedChildProject?.project?.name || '??' }}
          </span>
        </template>
        <span v-else class="font-weight-bold">Detalle del proyecto</span>
      </div>
      <v-btn
        icon="close"
        variant="text"
        density="comfortable"
        v-tooltip="'Cerrar'"
        @click="backToList"
      />
    </div>

    <!-- Cuerpo -->
    <v-expand-transition>
      <div v-if="view !== 'pill'">
        <v-divider/>

        <!-- Lista -->
        <template v-if="view === 'list'">
          <div
            v-if="dataLoading"
            class="pa-8 d-flex flex-column align-center text-grey"
          >
            <v-progress-circular indeterminate color="primary" class="mb-3"/>
            Cargando proyectos…
          </div>
          <div
            v-else-if="filteredProjects.length === 0"
            class="pa-8 d-flex flex-column align-center text-grey text-center"
          >
            <v-icon size="48" class="mb-2">search_off</v-icon>
            <div>No hay proyectos para los filtros actuales.</div>
          </div>
          <v-virtual-scroll
            v-else
            :items="filteredProjects"
            :item-height="ITEM_HEIGHT"
            :height="listHeight"
          >
            <template #default="{ item }">
              <v-card
                class="project-row my-1 cursor-pointer"
                :class="{ 'project-row--active': item.id === targetProjectId }"
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
        </template>

        <!-- Detalle / hijo -->
        <div
          v-else
          class="overflow-y"
          :style="{ maxHeight: embedded ? 'calc(92vh - 64px)' : '78vh' }"
        >
          <ProjectDetailMap
            :selectedProject="view === 'child'
              ? selectedChildProject
              : selectedParentProject"
            :full_main="view === 'child'
              ? childProject?.project
              : parentProject"
            :childProject="childProject?.project"
            :is_child="view === 'child'"
            @open-child-project="openChildProject"
          />
        </div>
      </div>
    </v-expand-transition>
  </div>
</template>

<style scoped>

.panel-header {
  background-color: #f5f5f5;
}

/* Necesario para que text-truncate funcione dentro del flex del header. */
.breadcrumb {
  flex: 1 1 auto;
  min-width: 0;
}

.project-row {
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