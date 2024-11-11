<script setup>
import {defineComponent, ref, computed} from 'vue'
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
const mainStore = useMainStore()

const props = defineProps({
  final_filters: Object,
  event_group_id: Number,
  show_group: {
    type: Boolean,
    default: false,
  },
  field: {
    type: String,
    default: "event_subtype",
  },
  clearable: {
    type: Boolean,
    default: true,
  },
  density: {
    type: String,
    default: "compact",
  },
})
const emits = defineEmits(['delete-record'])

const { impact_groups, cats, event_types, event_subtypes } = storeToRefs(mainStore)

const event_subtype = computed(() => {
  return event_subtypes.value.find(
    event_subtype => event_subtype.id === props.final_filters.event_subtype)
})

const event_type = computed(() => {
  if (!event_subtype.value)
    return null
  return event_subtype.value.event_type_obj
})

const items_built = computed(() => {
  if (props.final_filters.event_group_id){
    return event_types.value.filter(
      event_type => event_type.group === props.final_filters.event_group_id)
  }
  if (!event_type.value)
    return event_types.value
  return event_types.value.filter(
    ev_type => ev_type.event_group.id === event_type.value.event_group.id)
})

const current_event_subtypes = computed(() => {
  if (!event_type.value)
    return []
  return event_subtypes.value.filter(
    event_subtype => event_subtype.event_type === event_type.value.id)
})

const main_width = computed(() => 200)

</script>

<template>
  <div v-if="show_group" class="d-flex flex-column mr-2">
    <v-icon
      class="mr-1"
      :icon="is_social ? 'groups' : 'eco'"
    ></v-icon>
    <v-btn
      size="x-small"
      color="error"
      variant="outlined"
      class="mt-1"
      @click="$emits('delete-record')"
    >
      Eliminar
    </v-btn>
  </div>
  <v-select
    v-model="final_filters.event_type"
    :items="items_built"
    item-title="name"
    item-value="id"
    label="Tipo de evento"
    :density="density"
    variant="outlined"
    :clearable="clearable"
    _style="max-width: 250px; min-width: 250px;"
    :style="`max-width: ${main_width}px; min-width: ${main_width}px;`"
  >
    <template #prepend-inner v-if="!show_group">
      <v-icon
        :color="is_social ? 'teal' : 'green'"
        :icon="is_social ? 'groups' : 'eco'"
      ></v-icon>
    </template>
    <template #item="{ item, props: {onClick, title, value} }" v-if="true">
      <v-list-item
        @click="onClick"
      >
        <v-list-item-title>
          <b class="mr-1"> {{ item.title }} </b>
          <span v-if="item.raw.has_subtype">
            (tiene subtipos)
          </span>
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ item.raw.description }}
        </v-list-item-subtitle>
      </v-list-item>
    </template>
  </v-select>
  <v-select
    v-if="impact_type_full && impact_type_full.has_subtype"
    v-model="final_filters.impact_subtype"
    :items="impact_subtypes"
    item-title="name"
    item-value="id"
    label="Subtipo de evento"
    :density="density"
    variant="outlined"
    :clearable="clearable"
    style="max-width: 250px;"
    class="ml-2"
  >
    <template #item="{ item, props: {onClick, title, value} }">
      <v-list-item
        @click="onClick"
        :title="title"
        :subtitle="item.raw.description"
      >
      </v-list-item>
    </template>
  </v-select>
</template>

<style scoped>

</style>