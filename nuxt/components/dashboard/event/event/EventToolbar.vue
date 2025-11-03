<script setup>

import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";

import {computed} from "vue";
import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";
import EventDetails from "~/components/dashboard/event/event/EventDetails.vue";
import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import ActorCard from "~/components/dashboard/actor/actor/ActorCard.vue";

const props = defineProps({
  mention: Object,
})

const mainToolbarRef = ref(null)
defineExpose({ resetInitialData })

const all_actors = computed(() => {
  return props.mention.participants.map(participant => {
    return {...participant.actor_full, ...participant}
  })
})


function resetInitialData(){
  if (mainToolbarRef.value)
    mainToolbarRef.value.resetInitialData()
}


</script>

<template>
  <ToolbarCommon
    ref="mainToolbarRef"
    :main_object="mention"
    main_collection_name="mention"
    filter_group_name="event_types"
    child_relation_name="event"
    field="events"
    two_columns
    partial_save
    color="lime"
    required_field="event_type"
    required_full_category
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
        <template v-if="false" #rdows="{ item }">
          <v-select
            v-model="item.participant"
            :items="all_actors"
            item-title="name"
            item-value="id"
            label="Participante"
            variant="outlined"
          >
          </v-select>
        </template>
        <template #rows_init="{ item }">
          <v-select
            v-model="item.participant"
            :items="all_actors"
            item-title="name"
            item-value="id"
            label="Participante"
            variant="outlined"
          >
            <template #item="{ item, props: {onClick, title, value} }">
              <v-list-item
                @click="onClick"
                :value="value"
              >
                <template
                  v-slot:default
                >
                  <ActorCard
                    :full_main="item.raw"
                    :title="item.name"
                  />
                </template>
              </v-list-item>
            </template>
            <template #selection="{ item }">
              <ActorCard
                :full_main="item.raw"
                :title="item.name"
                is_simple
              />
            </template>
          </v-select>
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