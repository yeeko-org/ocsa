<script setup>

import StatusDetail from "~/components/dashboard/status/StatusDetail.vue";
import {ref} from "vue";


const visible_filters = ref([])


function changeFilters() {
  // let current_filters
  // current_filters = project_filters
  final_filters.value = {...pr_filters, ...comm_filters}
  console.log('current_filters', current_filters)
  current_filters.value = project_filters.sort((a, b) => a.order - b.order)
  visible_filters.value = current_filters.value.filter(f => f.init_visible)
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
      v-if="filter_box.collection"
      :petition="final_filters"
      :collection="filter_box.collection.split('_')[1]"
      :field="filter_box.collection"
      :label="`Status ${filter_box.name}`"
      clearable
      hide_details
      style="max-width: 300px;"
      _loading="loading_edition"
      @change-status="applyFilters"
    />
    <h5 v-else>{{filter_box.title || filter_box.name}}</h5>

  </v-col>

</template>

<style scoped>

</style>