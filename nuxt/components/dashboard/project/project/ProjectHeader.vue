<script setup>
import HeaderChip from '~/components/dashboard/common/utils/HeaderChip.vue'
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import ImpactChip from "~/components/dashboard/impact/ImpactChip.vue";


import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import HeaderCommon from "~/components/dashboard/common/generic/HeaderCommon.vue";
import LocationsChip from "~/components/dashboard/project/LocationsChip.vue";
import TitleCommon from "~/components/dashboard/common/utils/TitleCommon.vue";
import EventGroupsChip from "~/components/dashboard/event/EventGroupsChip.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  is_simple: Boolean,
})
const project = computed(() => {
  return props.main
})

const mention_counts = computed(() => {
  return project.value.mentions.length
})

</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
    :height="70"
    min_width_status="210"
  >
    <template #icon>
      <div
        v-if="!is_simple"
        style="width: 30px;"
      >
        <v-icon
          v-if="main.conflict"
          color="pink"
          v-tooltip="main.conflict_full.name"
        >
          local_fire_department
        </v-icon>
      </div>
      <ExtractivismIcons
        :project="main"
      />
<!--      <v-icon-->
<!--        v-if="main.is_grouper"-->
<!--        class="ml-3"-->
<!--        color="deep-purple"-->
<!--        v-tooltip="'Es un agrupador de proyectos.'"-->
<!--      >-->
<!--        group_work-->
<!--      </v-icon>-->
    </template>
    <template #title>
      <div class="d-flex flex-column align-start justify-start">
        <div class="ml-2 text-body-small" v-if="main.parent_project_full">
          <v-icon
            size="small"
            color="deep-purple"
          >hub</v-icon>
          <span class="text-grey-darken-1">
            Agrupador:
          </span>
          <span class="text-blue-darken-1 ml-1">
            {{main.parent_project_full.name}}
          </span>
        </div>
        <div v-else-if="main.is_grouper" class="ml-2 text-body-small">
          <v-icon
            class="mr-1"
            color="deep-purple"
            v-tooltip="'Este proyecto es un agrupador de otros proyectos.'"
          >
            hub
          </v-icon>
          <span class="text-grey-darken-1">
            Proyecto agrupador
          </span>
        </div>
        <TitleCommon
          :title_text="main.name"
          :title_width="300"
          card_class="ml-2 text-body-large"
        />
      </div>
    </template>

    <template #details>
      <HeaderChip
        v-if="main.is_grouper && main.children_projects"
        :count="main.children_projects.length"
        icon="hub"
        label="proyecto hijo"
        label_plural="proyectos hijos"
        collection_name="actor"
      />
      <HeaderChip
        :count="mention_counts"
        icon="newsmode"
        label="nota"
        label_plural="notas"
        color="deep-purple"
        :is_simple="is_simple"
      />
      <template v-if="!is_simple">
        <LocationsChip
          :project="main"
        />
        <v-divider
          vertical
          class="mx-1"
        />
        <EventGroupsChip
          :mentions="main.mentions"
        />
        <v-divider
          v-if="false"
          vertical
          inset
        />
        <ImpactChip
          :main_array="main.mentions"
          filter_group_name="impact_types"
          child_field="impacts"
        />
      </template>
      <v-divider
        vertical
        class="mx-1"
      />
      <ActorsChip
        :main="main"
        :is_simple="is_simple"
      />
      <HeaderChip
        v-if="main.others_parents && main.others_parents.length"
        :count="main.others_parents.length"
        icon="hub"
        label="otros proyectos agrupadores"
        color="warning"
        label_plural="otros actores padres"
        class="ml-2"
      />
      <div class="ml-1 d-flex flex-column align-center">
        <div class="text-grey text-body-small">
          {{main.proyecto_id_ref}}
        </div>
        <div class="text-grey-lighten-1 text-body-small">
          {{main.id}}
        </div>
      </div>
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>