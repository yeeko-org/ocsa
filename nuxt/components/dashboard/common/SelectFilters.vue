<script setup>
import StatusDetail from "@/components/dashboard/status/StatusDetail";

import { defineProps, ref, watch } from 'vue'
import GenericSelect from "~/components/dashboard/impact/GenericSelect.vue";

const props = defineProps({
  final_filters: Object,
  visible_filters: Array,
})
const emit = defineEmits(['apply-filters'])

const applyFilters = () => {
  console.log("debounce apply filters")
  emit('apply-filters')
}

</script>
<template>
  <v-col
    v-for="filter_box in visible_filters"
    :key="filter_box.name"
    :order="filter_box.order"
    cols="auto"
    class="px-2"
  >
    <StatusDetail
      v-if="filter_box.collection && filter_box.collection_type === 'status'"
      :final_filters="final_filters"
      :collection="filter_box.collection.split('_')[1]"
      collection_type="status"
      :field="filter_box.collection"
      :label="`Status ${filter_box.name}`"
      clearable
      hide_details
      style="max-width: 300px; min-width: 200px;"
      @change-status="applyFilters"
    />
    <GenericSelect
      v-else-if="filter_box.collection"
      :final_filters="final_filters"
      :collection="filter_box.collection"
      :collection_type="filter_box.collection_type"
      :field="filter_box.key"
      _label="`Status ${filter_box.name}`"
      :label="filter_box.collection_type === 'status'
        ? `Status ${filter_box.name}`
        : filter_box.title || filter_box.name"
      :item_id="filter_box.item_id"
      clearable
      hide_details
      style="max-width: 300px; min-width: 200px;"
      @change-status="applyFilters"
    />

    <h5 v-else>{{filter_box.title || filter_box.name}}</h5>
  </v-col>
</template>
