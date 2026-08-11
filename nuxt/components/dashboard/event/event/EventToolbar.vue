<script setup>

import ToolbarCommon from "~/components/dashboard/capture/ToolbarCommon.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";
import EventDetails from "~/components/dashboard/event/event/EventDetails.vue";
import ParticipantSelect from "~/components/dashboard/actor/ParticipantSelect.vue";
import PreActorCard from "~/components/dashboard/event/PreActorCard.vue";
const props = defineProps({
  parent_id: Number,
  all_actors: {
    type: Array,
    default: () => []
  },
  note_id: Number,
})
// const mention = defineModel({type: Object, required: true})
const events = defineModel({type: Array, required: true})

const mainToolbarRef = ref(null)
defineExpose({ resetInitialData, validate })

function resetInitialData(){
  if (mainToolbarRef.value)
    mainToolbarRef.value.resetInitialData()
}

function validate(){
  if (mainToolbarRef.value)
    return mainToolbarRef.value.validateAllForms()
  return true
}


</script>

<template>
  <ToolbarCommon
    ref="mainToolbarRef"
    v-model="events"
    filter_group_name="event_types"
    child_relation_name="event"
    field="events"
    two_columns
    color="lime"
    required_field="event_type"
    required_full_category
    :parent_id="parent_id"
    :note_id="note_id"
    :additional_fields="{
      'involvements': [], 'locations': [], 'displacements': []}"
    required
  >
    <template #rows="{ item, index }">
      <EventDetails
        v-model="events[index]"
        :is_edit="false"
      />
      <div
        v-if="item && item.id"
        class="mx-n2"
      >
        <DisplacementToolbar
          v-model="events[index].displacements"
          :parent_id="item.id"
          main_collection_name="event"
          :event_type="events[index].event_type"
          second_level
          is_event
        />
      </div>
    </template>
    <template #second-column="{ item, second_index }">
      <ToolbarCommon
        v-model="events[second_index].involvements"
        main_collection_name="event"
        filter_group_name="involved_roles"
        child_relation_name="involved"
        second_level
        :parent_id="item.id"
        :note_id="note_id"
        required_full_category
        color="blue"
        required
        vertical_actions
      >
        <template #rows_init="{ item }">
          <ParticipantSelect
            v-model="item.participant"
            :all_actors="all_actors"
          />
        </template>
        <template #rows="{item}">
          <PreActorCard
            :item="item"
            :all_actors="all_actors"
          />
        </template>
        <template #footer v-if="false">
          <v-card
            class="ma-2"
            elevation="2"
            variant="flat"
            color="white"
          >
            Sugerencias rápidas (comming soon...)
          </v-card>
        </template>
      </ToolbarCommon>
      <LocationsToolbar
        v-if="item"
        v-model="events[second_index].locations"
        :parent_id="item.id"
        :note_id="parent_id"
        main_collection_name="event"
        second_level
      />
    </template>
  </ToolbarCommon>

</template>

<style scoped>

</style>