<script setup>
import HeaderChip from '~/components/dashboard/common/HeaderChip.vue'
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import ImpactChip from "~/components/dashboard/impact/ImpactChip.vue";

import { computed } from 'vue'
import { useMainStore } from '~/store/index.js'
import { storeToRefs } from 'pinia'
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import LocationsChip from "~/components/dashboard/project/LocationsChip.vue";

const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

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

// const emits = defineEmits(['open-panel'])

const mention_counts = computed(() => {
  // console.log('project', project.value)
  return project.value.mentions.length
})
</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
    :height="70"
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
        <div class="ml-2 text-caption" v-if="main.parent_project_full">
          <span class="text-grey-darken-1">
            Grouper:
          </span>
          <span class="text-blue-darken-1 ml-1">
            {{main.parent_project_full.name}}
          </span>
        </div>
        <div
          class="ml-2 text-body-1"
          style="text-wrap: pretty; max-height: 54px; overflow: hidden;"
          v-tooltip:bottom="main.name"
        >
          {{ main.name }}
        </div>
      </div>
    </template>

    <template #details>
      <HeaderChip
        v-if="main.is_grouper"
        :count="main.children_projects.length"
        icon="account_tree"
        label="proyecto hijo"
        label_plural="proyectos hijos"
        collection_name="actor"
        class="ml-2"
        :horizontal="false"
      />
      <HeaderChip
        :count="mention_counts"
        icon="newspaper"
        label="nota"
        label_plural="notas"
        color="deep-purple"
        class="mr-1 ml-2"
        :is_simple="is_simple"
      />
      <template v-if="!is_simple">
        <LocationsChip
          :project="main"
          class="mr-2"
        />
        <ImpactChip
          :main_array="main.mentions"
          filter_group_name="impact_types"
          child_field="impacts"
        />
      </template>
      <ActorsChip
        :main="main"
        :is_simple="is_simple"
        class="mx-1"
      />
      <HeaderChip
        v-if="main.others_parents && main.others_parents.length"
        :count="main.others_parents.length"
        icon="account_tree"
        label="otros proyectos agrupadores"
        color="warning"
        label_plural="otros actores padres"
        class="ml-2"
      />
      <div class="ml-1 d-flex flex-column align-center">
        <div class="text-grey text-caption">
          {{main.proyecto_id_ref}}
        </div>
        <div class="text-grey-lighten-1 text-caption">
          {{main.id}}
        </div>
      </div>
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>