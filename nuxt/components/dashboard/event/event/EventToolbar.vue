<script setup>

import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";

import {computed} from "vue";
import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";
import EventDetails from "~/components/dashboard/event/event/EventDetails.vue";

const props = defineProps({
  mention: Object,
})

const all_actors = computed(() => {
  return props.mention.participants.map(participant => {
    return {...participant.actor_full, ...participant}
  })
})

</script>

<template>
  <ToolbarCommon
    :main_object="mention"
    main_collection_name="mention"
    filter_group_name="event_types"
    child_relation_name="event"
    field="events"
    two_columns
    partial_save
    color="lime"
    required_field="event_type"
    :additional_fields="{
      'involvements': [], 'locations': [], 'displacements': []}"
    required
  >
    <template #rows="{ item }">
      <EventDetails
        :full_main="item"
        :is_edit="false"
      />
      <div
        v-if="item && item.id"
        class="mx-n2"
      >
        <DisplacementToolbar
          :full_main="item"
          main_collection_name="event"
          second_level
          is_event
        />
      </div>
    </template>
    <template #second-column="{ item }">
      <ToolbarCommon
        :main_object="item"
        main_collection_name="event"
        filter_group_name="involved_roles"
        child_relation_name="involved"
        field="involvements"
        second_level
        color="blue"
        required
      >
        <template #rdows="{ item }">
          <v-select
            v-model="item.participant"
            :items="all_actors"
            item-title="name"
            item-value="id"
            label="Participante"
            variant="outlined"
          ></v-select>
        </template>
        <template #footer>
          <v-card
            class="ma-2"
            elevation="2"
            variant="flat"
            color="white"
          >
            Sugerencias rápidas (comming soon...)
          </v-card>
        </template>
        <template #rows_init="{ item }">
          <v-select
            v-model="item.participant"
            :items="all_actors"
            item-title="name"
            item-value="id"
            label="Participante"
            variant="outlined"
          ></v-select>
        </template>
      </ToolbarCommon>
      <LocationsToolbar
        v-if="item"
        :full_main="item"
        main_collection_name="event"
        second_level
      />
    </template>
  </ToolbarCommon>

</template>

<style scoped>

</style>