<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import LocationsChip from "~/components/dashboard/project/LocationsChip.vue";
import FullLocationsChip from "~/components/dashboard/project/FullLocationsChip.vue";

const props = defineProps({
  full_main: Object,
})

const parent_project = computed(() => {
  if (props.full_main.parent_project_text)
    return props.full_main.parent_project_text
  else if (props.full_main.parent_project_full)
    return props.full_main.parent_project_full.name
  else
    return null
})

</script>

<template>
  <div class="py-2">
    <div
      v-if="parent_project || full_main.status_validation"
      class="text-caption d-flex ga-4"
    >
      <div v-if="parent_project" class="mt-n1">
        <span class="text-grey-darken-1">
          Agrupador:
        </span>
        <span class="text-blue-darken-1 ml-1">
          {{parent_project}}
        </span>
      </div>
      <v-divider
        v-if="parent_project"
        vertical
        class="mx-3 mt-n1"
      ></v-divider>
      <StatusChip
        v-if="full_main.status_validation"
        :main="full_main"
        collection="validation"
        custom_class="flex-row mt-n1"
        bold_text
        x_small
        left_label
      />

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
        vertical
        class="mx-3"
      ></v-divider>
      <FullLocationsChip
        v-if="full_main.locations"
        :locations="full_main.locations"
        class="mb-n1"
        horizontal
      />
      <span
        v-if="!full_main.id && full_main.locations?.length > 0"
        class="text-indigo"
      >
        + {{ full_main.locations[0].details }}
      </span>
    </div>
  </div>
</template>

<style scoped>

</style>