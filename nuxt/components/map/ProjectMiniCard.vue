<script setup>

import ExtractivismIcons from "~/components/dashboard/project/ExtractivismIcons.vue";
import TitleCommon from "~/components/dashboard/common/utils/TitleCommon.vue";

const props = defineProps({
  full_main: Object,
  from_parent_project: Boolean,
  // Si trae un número, fija la altura de la tarjeta y trunca el título
  // (para v-virtual-scroll). Si es null, altura natural.
  fixed_height: {
    type: Number,
    default: null,
  },
})

</script>

<template>
  <div
    class="d-flex align-center"
    :class="fixed_height ? 'px-3' : 'py-2'"
    :style="fixed_height ? `height: ${fixed_height}px; overflow: hidden;` : ''"
  >
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
        graph_4
      </v-icon>
    </div>
    <div>
      <div
        class="d-flex align-center"
        :class="fixed_height ? 'flex-nowrap' : 'flex-wrap'"
      >
        <ExtractivismIcons
          :project="full_main"
          show_name
          :small_icons="!!fixed_height"
          chip_variant="tonal"
          :chip_size="fixed_height ? 'x-small' : 'small'"
        />
      </div>
      <div
        v-if="!from_parent_project && full_main.parent_project_full && false"
        class="text-caption"
      >
        <v-icon
          size="small"
          color="deep-purple"
        >hub</v-icon>
        <span class="text-grey-darken-1">
          Agrupador:
        </span>
        <span class="text-blue-darken-1 ml-1">
          {{full_main.parent_project_full.name}}
        </span>
      </div>
      <div class="d-flex align-center">
        <TitleCommon
          v-if="fixed_height"
          :title_text="full_main.name"
          :title_width="full_main.is_grouper ? 340 : 360"
          variant="tonal"
          :color="full_main.color"
          :card_class="from_parent_project
            ? ''
            : 'font-weight-bold'"
        />
        <div
          v-else
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