<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import FullLocationsChip from "~/components/dashboard/project/FullLocationsChip.vue";
import PreLocationsChip from "~/components/dashboard/project/PreLocationsChip.vue";
import {discardPreItem} from "~/composables/mix_pre_capture.js";

const props = defineProps({
  full_main: Object,
  note_id: Number,
})
const emits = defineEmits(['discard-location'])

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
        <v-icon
          size="small"
          color="deep-purple"
        >hub</v-icon>
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
        chip_size="x-small"
        chip_variant="outlined"
        left_label
      />

    </div>
    <div>
      <div class="d-flex align-center">
        <v-icon
          v-if="full_main.is_grouper"
          class="mr-2"
          v-tooltip="'Agrupa proyectos.'"
        >
          hub
        </v-icon>
        <div class="text-h6">
            {{ full_main.name }}
        </div>
      </div>
      <div
        v-if="full_main.alternative_name"
        class="text-caption"
      >
        ({{ full_main.alternative_name }})
      </div>
    </div>
    <div class="d-flex flex-wrap align-center mt-2">
      <ExtractivismIcons
        :project="full_main"
        show_name
        chip_variant="tonal"
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
    </div>
    <PreLocationsChip
      v-if="full_main.locations"
      :locations="full_main.locations"
      horizontal
      :can_edit_pre_save="!!full_main.id"
      @discard-location="emits('discard-location', $event)"
    />
  </div>
</template>

<style scoped>

</style>