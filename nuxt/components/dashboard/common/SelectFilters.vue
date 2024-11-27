<script setup>
import StatusDetail from "@/components/dashboard/status/StatusDetail";

import SelectGroup from "~/components/dashboard/common/SelectGroup.vue";

const props = defineProps({
  final_filters: Object,
  visible_filters: Array,
  filter_group: Object,
})
const emits = defineEmits(['apply-filters'])

const applyFilters = () => {
  console.log("debounce apply filters")
  emits('apply-filters')
}

</script>
<template>
  <v-col
    v-for="filter_box in visible_filters"
    :key="filter_box.name"
    :order="filter_box.order"
    cols="auto"
    class="pr-3 pl-0 py-0 d-flex"
  >
<!--      _v-if="filter_box.collection && filter_box.collection_group === 'status'"-->
    <StatusDetail
      v-if="filter_box.collection"
      :final_filters="final_filters"
      :collection="filter_box.key_name"
      collection_group="status"
      clearable
      hide-details
      style="max-width: 300px; min-width: 200px;"
      @change-status="applyFilters"
      is_filter
    />

    <SelectGroup
      v-else-if="filter_box.key_name"
      :filter_group_name="filter_box.key_name"
      :main_object="final_filters"
      :category_group_value="filter_box.category_group_value"
      :forced_level="filter_box.forced_level"
      is_filter
    />
    <h5 v-else>{{filter_box.title || filter_box.name}}</h5>
  </v-col>
</template>

<!--    <GenericSelect-->
<!--      _v-else-if="!filter_box.category_group && !filter_box.category_type"-->
<!--      v-else-if="false"-->
<!--      :filter_group_name="filter_box.key_name"-->
<!--      :final_filters="final_filters"-->
<!--      :collection="filter_box.category_subtype"-->
<!--      :collection_group="filter_box.collection_group"-->
<!--      :field="filter_box.key"-->
<!--      _label="`Status ${filter_box.name}`"-->
<!--      :label="filter_box.name"-->
<!--      :item_id="filter_box.item_id"-->
<!--      :is_autocomplete="filter_box.is_autocomplete"-->
<!--      clearable-->
<!--      hide-details-->
<!--      density="comfortable"-->
<!--      style="max-width: 300px; min-width: 200px;"-->
<!--      @change-status="applyFilters"-->
<!--    />-->
<!--    <SelectGroup-->
<!--      v-else-if="filter_box.collection && false"-->
<!--      :final_filters="final_filters"-->
<!--      :collection="filter_box.collection"-->
<!--      :collection_group="filter_box.collection_group"-->
<!--      :field="filter_box.key"-->
<!--      _label="`Status ${filter_box.name}`"-->
<!--      :label="filter_box.collection_group === 'status'-->
<!--        ? `Status ${filter_box.name}`-->
<!--        : filter_box.title || filter_box.name"-->
<!--      :item_id="filter_box.item_id"-->
<!--      :is_autocomplete="filter_box.is_autocomplete"-->
<!--      clearable-->
<!--      hide-details-->
<!--      density="comfortable"-->
<!--      style="max-width: 300px; min-width: 200px;"-->
<!--      @change-status="applyFilters"-->
<!--    />-->
