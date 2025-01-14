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
      <v-icon
        v-if="main.is_grouper"
        class="ml-3"
        color="deep-purple"
        v-tooltip="'Es un agrupador de proyectos.'"
      >
        group_work
      </v-icon>
    </template>
    <template #details>
      <span class="ml-2 mr-2 text-grey">
        {{main.proyecto_id_ref}}
      </span>
      <HeaderChip
        :count="mention_counts"
        icon="newspaper"
        label="nota"
        label_plural="notas"
        color="deep-purple"
        class="mx-1"
        :is_simple="is_simple"
      />
      <template v-if="!is_simple">
        <LocationsChip
          :project="main"
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
      />
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>