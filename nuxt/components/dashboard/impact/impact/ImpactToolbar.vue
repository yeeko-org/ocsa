<script setup>

import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";

const props = defineProps({
  mention: Object,
})

</script>

<template>
  <ToolbarCommon
    :main_object="mention"
    main_collection_name="mention"
    filter_group_name="impact_types"
    child_relation_name="impact"
    field="impacts"
    two_columns
    required
    partial_save
    required_field="impact_type"
    :additional_fields="{'locations': [], 'displacements': []}"
  >
    <template #rows="{ item }">
      <v-switch
        v-model="item.is_potential"
        label="Se trata de una afectación potencial"
        class="ml-4"
        color="accent"
        append-icon="tips_and_updates"
      />
      <v-textarea
        v-model="item.description"
        label="Descripción de la afectación"
        variant="outlined"
        density="compact"
        hide-details
        rows="1"
        auto-grow
        style="max-width: 600px;"
      ></v-textarea>
      <DisplacementToolbar
        v-if="item"
        :full_main="item"
        main_collection_name="impact"
        second_level
        class="px-0"
      />
    </template>
    <template #second-column="{ item }">
      <LocationsToolbar
        v-if="item"
        :full_main="item"
        main_collection_name="impact"
        second_level
      />
    </template>
  </ToolbarCommon>
</template>

<style scoped>

</style>