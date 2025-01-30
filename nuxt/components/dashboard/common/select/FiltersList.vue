<script setup>
import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";

import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import TripleBooleanFilter from "~/components/dashboard/custom_filters/TripleBooleanFilter.vue";
import RangeDates from "~/components/dashboard/custom_filters/RangeDates.vue";
import UserSelect from "~/components/dashboard/custom_filters/UserSelect.vue";
import OnlyByFilter from "~/components/dashboard/custom_filters/OnlyByFilter.vue";
import LocationType from "~/components/dashboard/custom_filters/LocationType.vue";

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
<!--  <v-col-->
<!--    v-for="filter_box in visible_filters"-->
<!--    :key="filter_box.name"-->
<!--    :order="filter_box.order"-->
<!--    cols="auto"-->
<!--    class="pr-3 pl-0 py-0 d-flex"-->
<!--  >-->
  <template
    v-for="filter_box in visible_filters"
    :key="filter_box.name"
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
      class="pr-3 pl-0 py-1"
    />
    <div
      v-else-if="filter_box.key_name"
      class="pr-3 pl-0 py-1 d-flex"
    >

      <SelectGroup
        :filter_group_name="filter_box.key_name"
        :main_object="final_filters"
        :category_group_value="filter_box.category_group_value"
        :forced_level="filter_box.forced_level"
        is_filter
      />
    </div>
    <template
      v-else-if="filter_box.component"
    >

      <TripleBooleanFilter
        v-if="filter_box.component === 'TripleBooleanFilter'"
        :final_filters="final_filters"
        :field="filter_box.field"
        :label="filter_box.title"
        class="pr-3 pl-0 py-1"
      />
      <RangeDates
        v-else-if="filter_box.component === 'RangeDates'"
        :final_filters="final_filters"
        :field="filter_box.field"
        :label="filter_box.title"
      />
      <UserSelect
        v-else-if="filter_box.component === 'UserSelect'"
        :final_filters="final_filters"
        :field="filter_box.field"
        :label="filter_box.title"
        class="pr-3 pl-0 py-1"
        is_filter
      />
      <OnlyByFilter
        v-else-if="filter_box.component === 'OnlyByFilter'"
        :final_filters="final_filters"
        :field="filter_box.field"
        :label="filter_box.title"
        :filter_box="filter_box"
        class="pr-3 pl-0 py-1"
      />
      <LocationType
        v-else-if="filter_box.component === 'LocationType'"
        :full_main="final_filters"
        is_filter
      />
      <h5 v-else>{{filter_box.title || filter_box.name}}</h5>
    </template>
    <h5 v-else>{{filter_box.title || filter_box.name}}</h5>
  </template>

</template>