<script setup>

import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #icon>
      <v-card
        color="grey"
        rounded="lg"
        variant="outlined"
        class="mx-2 d-flex _flex-column align-center"
      >
        <SelectGroup
          :main_object="main"
          filter_group_name="impact_types"
          main_collection_name="impact_subtype"
          field="impact_type"
          forced_level="subtype"
          is_display
        />
      </v-card>
    </template>
    <template #details>
      <HeaderChip
        class="ml-3"
        :count="main.mentions_count"
        collection_name="note"
      />
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>
