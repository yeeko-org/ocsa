<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import ProjectMiniCard from "~/components/map/panel/ProjectMiniCard.vue";

import ConflictCard from "~/components/dashboard/project/conflict/ConflictCard.vue";
import CollectionList from "~/components/map/mentions/CollectionList.vue";
import ChildProjectsList from "~/components/map/panel/ChildProjectsList.vue";
import NotesList from "~/components/map/mentions/NotesList.vue";

const mainStore = useMainStore()
const { megaproject_types_dict } = storeToRefs(mainStore)

// Vista del detalle de un proyecto.
const props = defineProps({
  // Cabecera optimista: { color, project } (llega antes que full_main).
  selectedProject: {
    type: Object,
    default: null,
  },
  // Hijo abierto, para resaltarlo en la lista de vinculados (vista padre).
  childProject: {
    type: Object,
    default: null,
  },
  // Proyecto completo con mentions/events/impacts (llega tras el fetch).
  full_main: {
    type: Object,
    default: null,
  },
  is_child: Boolean,
});

const emits = defineEmits([
  'open-child-project',
]);

// Color de respaldo para la barra de carga mientras llega full_main.
const final_color = computed(() => {
  if (props.selectedProject?.color)
    return props.selectedProject.color
  const megaproject_type = props.selectedProject?.project?.megaproject_type
  const megaproject_type_obj = megaproject_types_dict.value[megaproject_type]
  if (megaproject_type_obj)
    return megaproject_type_obj.first_extractivism_type.color
  return 'primary'
})

function openChildProjectCard(child_project){
  emits('open-child-project', child_project)
}

</script>

<template>
  <div class="project-detail">
    <!-- Cabecera del proyecto (mini-card) o barra de carga -->
    <v-card
      v-if="full_main"
      class="d-flex align-center px-3"
      color="deep-purple"
      variant="tonal"
      style="width: 100%;"
    >
      <ProjectMiniCard
        :full_main="full_main"
        title="Detalles del Proyecto"
      />
    </v-card>
    <template v-else-if="selectedProject">
      <v-card-text>
        <h3>{{ selectedProject.project?.name || 'Nombre desconocido' }}</h3>
      </v-card-text>
      <v-progress-linear
        height="40"
        indeterminate
        :color="final_color || 'primary'"
      ></v-progress-linear>
    </template>

    <v-card-text
      v-if="full_main"
      class="px-1 py-2"
    >
      <span class="text-grey-darken-1 ml-1">
        Conflicto socioambiental:
      </span>

      <v-card
        v-if="full_main.conflict_name"
        class="d-flex align-center px-3 py-2 mb-3"
        color="red"
        variant="tonal"
        style="width: 100%;"
      >
        <ConflictCard
          :full_main="{name: full_main.conflict_name}"
          in_map
        />
      </v-card>

      <ChildProjectsList
        :full_main="full_main"
        :child-project="childProject"
        @open-child-project="openChildProjectCard"
      />

      <CollectionList
        v-if="full_main?.impacts?.length > 0"
        :objects="full_main.impacts"
        :mentions="full_main.mentions"
        :current_project_id="selectedProject.project.id"
        node_name="impact_types"
        type_key="impact_type"
        subtype_key="impact_subtype"
      />
      <CollectionList
        v-if="full_main?.events?.length > 0"
        :objects="full_main.events"
        :mentions="full_main.mentions"
        :current_project_id="selectedProject.project.id"
        node_name="event_types"
        type_key="event_type"
        subtype_key="event_subtype"
      />

      <NotesList
        :full_main="full_main"
        :selected-project="selectedProject"
      />
    </v-card-text>
  </div>
</template>

<style scoped>

.project-detail {
  width: 100%;
}

</style>