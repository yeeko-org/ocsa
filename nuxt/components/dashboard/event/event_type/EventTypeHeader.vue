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
      <SelectGroup
        :main_object="main"
        filter_group_name="event_types"
        main_collection_name="event_type"
        field="event_group"
        forced_level="type"
        is_display
      />
    </template>
    <template #details>
      <HeaderChip
        class="ml-3"
        :count="main.count"
        collection_name="event"
      />
      <HeaderChip
        class="ml-3"
        color="lime-darken-2"
        :count="main.event_subtype_count"
        collection_name="event_subtype"
      />
      <v-icon
        v-if="main.has_displacement"
        color="red darken-2"
        class="ml-3"
        v-tooltip="`Muestra Desplazamiento Forzado`"
      >
      </v-icon>
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>