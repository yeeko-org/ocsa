<script setup>
import {computed} from 'vue'
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import BelongIcons from "~/components/dashboard/classify/BelongIcons.vue";

import { useMainStore } from '~/store/index.js'
import { storeToRefs } from 'pinia'
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    required: false,
    default: true,
  },
  is_simple: Boolean,
})

const actor = computed(() => props.main)

const unique_projects = computed(() => {
  let projects = participants.value.map(participant => {
    return participant.mention.project_full.name
  })
  return [...new Set(projects)]
})

const unique_notes = computed(() => {
  let source_dict = {}
  cats.value.source.forEach(source => {
    source_dict[source.id] = source.name
  })
  let set_notes = new Set()
  let titles = []
  participants.value.forEach(participant => {
    if (!set_notes.has(participant.mention.note)) {
      const note_full = participant.mention.note_full
      const source = source_dict[note_full.source]
      titles.push(`${note_full.title}-${source}`)
      set_notes.add(participant.mention.note)
    }
  })
  return titles
})

const participants = computed(() => {
  let projects_dict = {}
  if (props.main.projects)
    projects_dict = props.main.projects.reduce((acc, project) => {
      acc[project.id] = project
      return acc
    }, {})
  let notes_dict = {}
  if (props.main.notes)
    notes_dict = props.main.notes.reduce((acc, note) => {
      acc[note.id] = note
      return acc
    }, {})
  return props.main.participants.map(participant => {
    const project = participant.mention.project_full
      ? participant.mention.project_full
      : projects_dict[participant.mention.project]
    const note = participant.mention.note_full
      ? participant.mention.note_full
      : notes_dict[participant.mention.note]
    return {
      ...participant,
      mention: {
        ...participant.mention,
        project_full: project,
        note_full: note,
      }
    }
  })
})

</script>
<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #icon>
      <SelectGroup
        :main_object="main"
        filter_group_name="sectors"
        main_collection_name="actor"
        forced_level="subtype"
        is_display
      />
    </template>
    <template #title>
      <div class="d-flex flex-column align-start justify-start">
        <div class="ml-2 text-caption" v-if="main.parent_actor_full">
          <span class="text-grey-darken-1">
            Padre:
          </span>
          <span class="text-blue-darken-1 ml-1">
            {{main.parent_actor_full.name}}
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
      <template v-if="!is_simple">
        <HeaderChip
          :count="actor.mentions_count"
          class="ml-2"
          collection_name="note"
          :tooltip_complement="unique_notes.join('<br>')"
        />
        <HeaderChip
          :count="unique_projects.length"
          :tooltip_complement="unique_projects.join('<br>')"
          collection_name="project"
          class="ml-2"
        />
        <ActorsChip
          :main="actor"
          :participants="participants"
          field="project_full"
          subfield="name"
          class="ml-2"
        />
      </template>
      <BelongIcons :actor="actor"/>
      <HeaderChip
        v-if="actor.children_actors && actor.children_actors.length"
        :count="actor.children_actors.length"
        icon="account_tree"
        label="actor hijo"
        label_plural="actores hijos"
        collection_name="actor"
        class="ml-2"
      />
      <HeaderChip
        v-if="actor.others_parents && actor.others_parents.length"
        :count="actor.others_parents.length"
        icon="account_tree"
        label="otro actor padre"
        color="warning"
        label_plural="otros actores padres"
        class="ml-2"
      />
      <span v-if="actor.network_seq" class="ml-2">
        <v-icon color="deep-purple">lan</v-icon>
        <span class="text-body-2">Red {{ actor.network_seq }}</span>
      </span>
    </template>
  </HeaderCommon>

</template>

<style scoped>

</style>