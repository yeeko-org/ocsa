<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import ProjectMiniCard from "~/components/map/ProjectMiniCard.vue";

import ConflictCard from "~/components/dashboard/project/conflict/ConflictCard.vue";
import CollectionListMap from "~/components/map/CollectionListMap.vue";
import ChildProjectsListMap from "~/components/map/ChildProjectsListMap.vue";
import NotesListMap from "~/components/map/NotesListMap.vue";
const mainStore = useMainStore()
const { megaproject_types_dict } = storeToRefs(mainStore)

const props = defineProps({
  selectedProject: {
    type: Object,
    default: null,
  },
  childProject: {
    type: Object,
    default: null,
  },
  full_main: {
    type: Object,
    default: null,
  },
  is_child: Boolean,
});

const emits = defineEmits([
  'update:selectedProject',
  'open-child-project',
]);

const final_color = computed(() => {
  if (props.selectedProject.color)
    return props.selectedProject.color
  console.log("selectedProject has no color, defaulting to 'primary'",
    props.selectedProject?.project)
  // console.log("megaproject_types_dict", megaproject_types_dict.value)
  const megaproject_type = props.selectedProject.project.megaproject_type
  const megaproject_type_obj = megaproject_types_dict.value[megaproject_type]
  console.log('megaproject_type_obj', megaproject_type_obj)
  if (megaproject_type_obj){
    return megaproject_type_obj.first_extractivism_type.color
  }
  return 'primary'
})

const main_card_class = computed(() => {
  // console.log('props.selectedProject', props.selectedProject)
  // console.log('is_child', props.is_child)
  if (props.selectedProject.project.is_grouper){
    return 'grouper-card'
  }
  else if (props.selectedProject.project.parent_project){
    return 'has-parent-project-card'
  }
  return ''
})

function openChildProjectCard(child_project){
  // console.log('child_project', child_project)
  emits('open-child-project', child_project)
}

</script>

<template>
  <v-card
    width="400"
    height="80vh"
    class="ma-3 project-card"
    :class="main_card_class"
    elevation="6"
    rounded="lg"
  >
    <v-card
      v-if="full_main"
      class="d-flex align-center px-3"
      zcolor="final_color"
      color="deep-purple"
      variant="tonal"
      style="width: 100%;"
    >
      <ProjectMiniCard
        :full_main="full_main"
        title="Detalles del Proyecto"
      />
      <v-btn
        v-if="!childProject"
        size="small"
        icon
        variant="tonal"
        @click="emits('update:selectedProject', null)"
        class="close-btn"
        color="accent"
      >
        <v-icon>close</v-icon>
      </v-btn>
    </v-card>
    <template v-else>
      <v-card-text>
        <h3>{{selectedProject.project.name}}</h3>
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
      <ChildProjectsListMap
        :full_main="full_main"
        :child-project="childProject"
        @open-child-project="openChildProjectCard"
      />
      <template v-if="full_main">
        <CollectionListMap
          v-if="full_main?.impacts?.length > 0"
          :objects="full_main.impacts"
          :mentions="full_main.mentions"
          :current_project_id="selectedProject.project.id"
          node_name="impact_types"
          type_key="impact_type"
          subtype_key="impact_subtype"
        />
        <CollectionListMap
          v-if="full_main?.events?.length > 0"
          :objects="full_main.events"
          :mentions="full_main.mentions"
          :current_project_id="selectedProject.project.id"
          node_name="event_types"
          type_key="event_type"
          subtype_key="event_subtype"
        />

        <NotesListMap
          :full_main="full_main"
          :selected-project="selectedProject"
        />
      </template>

    </v-card-text>
  </v-card>
</template>

<style scoped>

.project-card {
  position: absolute !important;
  z-index: 2 !important;
  overflow-y: auto;
  top: 40px;
  right: 0;
}

.grouper-card {
  right: 54px !important;
}

.has-parent-project-card {
  top: 112px !important;
}

.close-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

</style>