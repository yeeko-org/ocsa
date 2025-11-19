<script setup>

import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";

const props = defineProps({
  full_main: Object,
  from_parent_project: Boolean,
})

</script>

<template>
  <div class="py-2 d-flex align-center">
    <div v-if="!from_parent_project">
      <v-icon
        v-if="full_main.is_grouper"
        class="mr-2"
        v-tooltip="'Es un agrupador de proyectos.'"
      >
        hub
      </v-icon>
      <v-icon
        v-else-if="full_main.parent_project"
        class="mr-2"
        v-tooltip="'Pertenece a un agrupador de proyectos.'"
        color="light-blue"
      >
        device_hub
      </v-icon>
    </div>
    <div>
      <div class="d-flex flex-wrap align-center">
        <ExtractivismIcons
          :project="full_main"
          show_name
        />
      </div>
      <div
        v-if="!from_parent_project && full_main.parent_project_full && false"
        class="text-caption"
      >
        <span class="text-grey-darken-1">
          Agrupador:
        </span>
        <span class="text-blue-darken-1 ml-1">
          {{full_main.parent_project_full.name}}
        </span>
      </div>
      <div class="d-flex align-center">
        <div
          :class="from_parent_project ? 'text-body-1' : 'text-h6 font-weight-bold'"
          class="mt-1"
        >
            {{ full_main.name }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>