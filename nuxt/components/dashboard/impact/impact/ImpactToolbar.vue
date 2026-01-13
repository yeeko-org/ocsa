<script setup>

import DisplacementToolbar from "~/components/dashboard/df/DisplacementToolbar.vue";
import LocationsToolbar from "~/components/dashboard/space_time/LocationsToolbar.vue";
import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";
import DescriptionIcon from "~/components/dashboard/utils/DescriptionIcon.vue";

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
    partial_save
    required_field="impact_type"
    :additional_fields="{'locations': [], 'displacements': []}"
  >
    <template #rows="{ item, in_edition }">
      <v-switch
        v-if="in_edition"
        v-model="item.is_potential"
        label="Se trata de una afectación potencial"
        class="ml-4"
        color="accent"
        append-icon="tips_and_updates"
      />
      <v-icon
        v-else-if="item.is_potential"
        color="orange"
        class="ml-4"
        title="Afectación potencial"
      >tips_and_updates</v-icon>
      <v-textarea
        v-if="in_edition"
        v-model="item.description"
        label="Descripción de la afectación"
        variant="outlined"
        density="compact"
        hide-details
        rows="1"
        auto-grow
        style="max-width: 600px;"
      ></v-textarea>
      <DescriptionIcon
        v-else
        :description="item.description"
      />
      <DisplacementToolbar
        v-if="item"
        :full_main="item"
        main_collection_name="impact"
        second_level
        class="px-0"
      />
    </template>
    <template #second-column="{ item, in_edition }">
      <LocationsToolbar
        v-if="item"
        :full_main="item"
        main_collection_name="impact"
        second_level
        :external_in_edition="in_edition"
      />
    </template>
  </ToolbarCommon>
</template>

<style scoped>

</style>