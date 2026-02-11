<script setup >

import ProjectMiniList from "~/components/dashboard/project/ProjectMiniList.vue";
import CriteriaChip from "~/components/dashboard/capture/CriteriaChip.vue";

const props = defineProps({
  paragraph: {
    type: Object,
    required: true,
  },
  show_all: Boolean,
  selected_fields: {
    type: Array,
    default: () => [],
  },
  active_external: Boolean,
  external_paragraphs: {
    type: Array,
    required: true,
  },
})

const emits = defineEmits(['show-all'])

const show_paragraph = computed(() => {
  if (props.show_all)
    return true
  if (props.active_external && props.external_paragraphs.length)
    return props.external_paragraphs.includes(props.paragraph.idx)
  if (!props.selected_fields.length)
    return !!props.paragraph.projects.length
  return props.paragraph.criteria.some(c => props.selected_fields.includes(c.name))
})

</script>

<template>
  <v-card
    v-if="show_paragraph"
    :key="paragraph.idx"
    variant="outlined"
    class="mb-1"
    color="grey-lighten-1"

    style="width: 100%;"
  >
    <v-card-text class="pb-1 pt-2 text-black">
      <div class="d-flex" v-for="project in paragraph.projects">
        <ProjectMiniList
          :mentions="[project]"
          show_full
        />
        <CriteriaChip
          is_simple
          :direct_criteria="project.criteria"
        />
      </div>
      <template v-if="paragraph.image">

        <v-btn
          variant="text"
          size="small"
          @click="paragraph.show_image = !paragraph.show_image"
        >
          [IMAGEN]
        </v-btn>
        <v-img
          v-if="paragraph.show_image"
          :src="paragraph.image"
          class="my-2"
          max-height="400"
          contain
        >
        </v-img>
      </template>
      <span v-html="paragraph.text" class="text-body-1">
      </span>
    </v-card-text>
  </v-card>
  <v-btn
    v-else
    :key="paragraph.idx"
    class="mb-1"
    variant="text"
    color="accent"
    icon
    @click="$emit('show-all')"
  >
    <v-icon>subject</v-icon>
    <v-tooltip
      activator="parent"
      location="bottom"
      :max-width="400"
    >
      <v-card
        class="mx-n4 my-n2"
      >
        <v-card-title class="text-subtitle-1">
          {{ paragraph.idx }}. Click para ver todos los párrafos
        </v-card-title>
        <v-card-text>
          {{ paragraph.text }}
        </v-card-text>
      </v-card>
    </v-tooltip>
  </v-btn>
</template>

<style scoped>

</style>