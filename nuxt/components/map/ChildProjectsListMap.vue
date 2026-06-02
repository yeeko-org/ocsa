<script setup>

import ProjectMiniCard from "~/components/map/ProjectMiniCard.vue";

const props = defineProps({
  full_main: {
    type: Object,
    default: null,
  },
  childProject: {
    type: Object,
    default: null,
  },
});

const emits = defineEmits([
  'open-child-project',
]);

function openChildProjectCard(child_project) {
  emits('open-child-project', child_project)
}

</script>

<template>
  <template v-if="full_main.children_projects_full?.length > 0">
    <div class="d-flex align-center mb-1">
      <v-icon color="grey" class="mr-2">
        hub
      </v-icon>
      <span class="text-title-medium text-grey">
        {{ full_main.children_projects_full.length }} proyectos vinculados:
      </span>
    </div>
    <div>
      <v-card
        v-for="child_project in full_main.children_projects_full"
        :key="child_project.id"
        variant="elevated"
        :color="child_project.id === childProject?.id ? 'light-blue' : 'white'"
        elevation="3"
        v-ripple
        class="mb-2 px-3 d-flex align-center"
        @click="openChildProjectCard(child_project)"
      >
        <v-icon
          class="mr-2"
          :color="child_project.id === childProject?.id ? 'white' : 'light-blue'"
        >
          graph_4
<!--              subdirectory_arrow_right-->
        </v-icon>
        <ProjectMiniCard
          :full_main="child_project"
          title="Detalles del Proyecto"
          from_parent_project
        />
        <v-tooltip
          activator="parent"
          location="left"
        >
          <div style="max-width: 200px;">
            <div class="font-weight-bold">
              {{ child_project.name }}
            </div>
            <div class="text-body-small mt-2">
              (Haz clic para ver más detalles)
            </div>
          </div>
        </v-tooltip>
      </v-card>
    </div>
  </template>
</template>