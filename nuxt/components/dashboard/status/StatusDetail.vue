<script setup>
import StatusChip from '~/components/dashboard/status/StatusChip.vue'
import {useStatusGroup} from '~/composables/useStatusGroup.js'

const props = defineProps({
  collection: [String, Object],
  is_filter: Boolean,
  density: {
    type: String,
    default: "default",
  },
  hide_details: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
})

const final_filters = defineModel({type: Object, required: true})

const {field, label, items, display, is_readonly, isSelectable} =
  useStatusGroup(() => props.collection, {
    record: final_filters,
    is_filter: () => props.is_filter,
    readonly: () => props.readonly,
  })

// El `#item` slot no informa al v-select de qué opciones están
// deshabilitadas; sin `item-props` seguirían siendo elegibles con teclado.
const item_props = (item) => ({disabled: !isSelectable(item)})

const emits = defineEmits(['change-status'])

</script>

<template>
  <StatusChip
    v-if="is_readonly && display"
    :main="final_filters"
    :collection="collection"
    left_label
    custom_class="flex-row"
    :hide_details="hide_details"
  />
  <v-select
    v-else
    v-model="final_filters[field]"
    :items="items"
    item-title="public_name"
    item-value="name"
    :variant="is_filter ? 'underlined' : 'outlined'"
    :clearable="is_filter"
    :label="label"
    max-width="320"
    min-width="260"
    :hide-details="hide_details"
    density="compact"
    :readonly="is_readonly"
    :loading="loading"
    :item-props="item_props"
    @update:modelValue="emits('change-status', $event)"
  >
    <template
      #item="{ internalItem: item, props: {onClick, title, value, disabled} }"
    >
      <v-list-item
        @click="onClick"
        :title="title"
        :subtitle="item.raw.description"
        :value="value"
        :disabled="disabled"
      >
        <template v-slot:prepend>
          <v-icon
            :color="item.raw.color || 'grey'"
            :icon="item.raw.icon || 'trip_origin'"
          ></v-icon>
        </template>
      </v-list-item>
    </template>
    <template #selection="{ internalItem: item }">
      <div
        :class="`text-${item.raw.color || 'grey'}`"
        class="d-flex pb-1 pt-2"
      >
        <v-icon
          class="mr-2"
          :color="item.raw.color || 'grey'"
          :icon="item.raw.icon || 'trip_origin'"
        ></v-icon>
        {{ item.title }}
      </div>
    </template>

  </v-select>
</template>

<style scoped>

</style>
