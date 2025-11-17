<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import LocationsChip from "~/components/dashboard/project/LocationsChip.vue";

const props = defineProps({
  full_main: Object,
})

</script>

<template>
  <div class="py-2">
    <div class="text-caption" v-if="full_main.parent_project_full">
      <span class="text-grey-darken-1">
        Agrupador:
      </span>
      <span class="text-blue-darken-1 ml-1">
        {{full_main.parent_project_full.name}}
      </span>
    </div>
    <div class="d-flex align-center">
      <v-icon
        v-if="full_main.is_grouper"
        class="mr-2"
        v-tooltip="'Es un agrupador de proyectos.'"
      >
        hub
      </v-icon>
      <div>
        <span class="text-h6">
          {{ full_main.name }}
        </span>
        <span
          v-if="full_main.alternative_name"
          class="text-caption ml-2 mt-1"
        >
          ({{ full_main.alternative_name }})
        </span>
      </div>
    </div>
    <div class="d-flex flex-wrap align-center">
      <ExtractivismIcons
        :project="full_main"
        show_name
      />
      <v-divider
        v-if="full_main.status_validation"
        vertical
        class="mx-3"
      ></v-divider>
      <StatusChip
        v-if="full_main.status_validation"
        :main="full_main"
        collection="validation"
        class="mb-1"
        bold_text
        x_small
        left_label
      />
      <v-divider
        v-if="full_main.status_validation"
        vertical
        class="mx-3"
      ></v-divider>
      <LocationsChip
        v-if="full_main.locations"
        :project="full_main"
        class="ml-3 mb-n1"
        horizontal
      />
    </div>
  </div>
</template>

<style scoped>

</style>