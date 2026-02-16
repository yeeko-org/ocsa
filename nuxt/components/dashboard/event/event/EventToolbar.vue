<script setup>

import ToolbarCommon from "~/components/dashboard/capture/ToolbarCommon.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";
import EventDetails from "~/components/dashboard/event/event/EventDetails.vue";
import ActorCard from "~/components/dashboard/actor/actor/ActorCard.vue";
import { useRules } from '~/composables/useRules'
import PreActorCard from "~/components/dashboard/event/PreActorCard.vue";
const props = defineProps({
  parent_id: Number,
  all_actors: {
    type: Array,
    default: () => []
  },
  note_id: Number,
})
const { rules } = useRules()
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

const registered_actors = computed(() => {
  return props.all_actors.filter(actor => actor.id)
})

</script>

<template>
  <ToolbarCommon
    ref="mainToolbarRef"
    v-model="events"
    filter_group_name="event_types"
    child_relation_name="event"
    field="events"
    two_columns
    partial_save
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
      >
        <template #rows_init="{ item }">
          <v-select
            v-model="item.participant"
            :items="registered_actors"
            item-title="name"
            item-value="id"
            label="Participante"
            variant="outlined"
            :rules="[rules.required]"
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
                    :title="item.title"
                    is_simple
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