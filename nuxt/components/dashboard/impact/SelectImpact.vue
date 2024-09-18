<script setup>
import {defineComponent, ref, computed, defineProps} from 'vue'
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
const mainStore = useMainStore()

const props = defineProps({
  final_filters: Object,
  label: String,
  collection: {
    type: String,
    default: "all",
  },
  show_group: {
    type: Boolean,
    default: false,
  },
  field: {
    type: String,
    default: "impact_type",
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
const emit = defineEmits(['delete-impact'])

const { impact_groups, cats } = storeToRefs(mainStore)
const impact_type_full = computed(() => {
  return impact_groups.value["all"].find(
    impact_group => impact_group.id === props.final_filters.impact_type)
})
const is_social = computed(() => {
  if (!impact_type_full.value && props.final_filters.is_social !== undefined)
    return props.final_filters.is_social
  return impact_type_full.value.is_social
})
const items_built = computed(() => {
  const final_collection = props.collection === "all"
      ? is_social.value !== undefined
        ? is_social.value
          ? "social"
          : "environmental"
        : "all"
      : props.collection
  return impact_groups.value[final_collection]
})

const show_subtypes = computed(() => {
  return impact_type_full.value && impact_type_full.value.has_subtype
})

const impact_subtypes = computed(() => {
  if (!impact_type_full.value)
    return []
  return cats.value.impact_subtypes.filter(
    subtype => subtype.impact_type === impact_type_full.value.id)
})

const main_width = computed(() => show_subtypes.value ? 200 : 260)

</script>

<template>
  <div v-if="show_group" class="d-flex flex-column mr-2">
    <v-chip
      class="mr-1"
      :color="is_social ? 'teal' : 'green'"
      min-width="150"
      :prepend-icon="is_social ? 'groups' : 'eco'"
    >
      {{ is_social ? 'Social' : 'Ambiental' }}
    </v-chip>
    <v-btn
      size="x-small"
      color="error"
      variant="outlined"
      class="mt-1"
      @click="$emit('delete-impact')"
    >
      Eliminar
    </v-btn>
  </div>
  <v-select
    v-model="final_filters.impact_type"
    :items="items_built"
    item-title="name"
    item-value="id"
    :label="label"
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
    label="Subtipo de afectación"
    :density="density"
    variant="outlined"
    :clearable="clearable"
    style="max-width: 250px;"
    class="ml-2"
  >
    <template #item="{ item, props: {onClick, title, value} }" v-if="true">
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