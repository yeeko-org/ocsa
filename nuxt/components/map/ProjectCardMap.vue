<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import ProjectMiniCard from "~/components/map/ProjectMiniCard.vue";

import ConflictCard from "~/components/dashboard/project/conflict/ConflictCard.vue";
import NoteTitle from "~/components/dashboard/source/note/NoteTitle.vue";
import CollectionListMap from "~/components/map/CollectionListMap.vue";
const mainStore = useMainStore()
const { megaproject_types_dict, all_nodes, schemas } = storeToRefs(mainStore)

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

const showing = ref(10)

const emits = defineEmits([
  'update:selectedProject',
  'open-child-project',
]);

const related_notes = computed(() => {
  let note_ids = new Set()
  let direct_notes = []
  let indirect_notes = []
  if (!props.full_main || !props.full_main.mentions)
    return {direct: direct_notes, indirect: indirect_notes, count: 0}
  const is_grouper = props.selectedProject?.project?.is_grouper || false
  props.full_main.mentions.forEach(mention => {
    if (!note_ids.has(mention.note)){
      // direct_notes.push(mention.note_full)
      if (is_grouper){
        if (mention.project === props.selectedProject.project.id){
          direct_notes.push(mention.note_full)
        }
        else {
          indirect_notes.push(mention.note_full)
        }
      }
      else
        direct_notes.push(mention.note_full)

    }
    note_ids.add(mention.note)
  })
  return {direct: direct_notes, indirect: indirect_notes, count: note_ids.size}
})

const filtered_notes = computed(() => {
  return related_notes.value.direct.slice(0, showing.value)
})

const plural_comp = computed(() => {
  return related_notes.value.direct.length !== 1 ? 's' : ''
})

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
      <span class="text-grey-darken-1 mr-2">
        Conflicto:
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
      <template v-if="full_main.children_projects_full?.length > 0">
        <div class="d-flex align-center mb-1">
          <v-icon color="grey" class="mr-2">
            hub
          </v-icon>
          <span class="text-subtitle-1 text-grey">
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
              device_hub
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
                <div class="text-caption mt-2">
                  (Haz clic para ver más detalles)
                </div>
              </div>
            </v-tooltip>
          </v-card>
        </div>
      </template>
      <template v-if="full_main">
        <CollectionListMap
          v-if="full_main?.impacts?.length > 0"
          :objects="full_main.impacts"
          node_name="impact_types"
          type_key="impact_type"
          subtype_key="impact_subtype"
        />
        <CollectionListMap
          v-if="full_main?.events?.length > 0"
          :objects="full_main.events"
          node_name="event_types"
          type_key="event_type"
          subtype_key="event_subtype"
        />


        <span class="text-subtitle-1 text-deep-purple mt-2">
          Mencionado directamente en {{related_notes.direct.length}}
          Nota{{plural_comp}}:
        </span>
        <v-card
          :key="note_id.id"
          v-for="note_id in filtered_notes"
          class="mb-2 py-1 px-1"
          variant="tonal"
          color="purple"
        >
          <NoteTitle
            :main="note_id"
            forced_title
          />
        </v-card>
        <v-card-actions class="py-0">
          <v-spacer></v-spacer>
          <v-btn
            v-if="related_notes.direct.length > showing"
            variant="outlined"
            color="purple"
            @click="showing += 15"
            append-icon="expand_more"
          >
            Mostrar más
          </v-btn>
          <v-btn
            v-if="showing > 10"
            variant="text"
            color="red"
            @click="showing = 10"
            append-icon="expand_less"
          >
            Mostrar menos
          </v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
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