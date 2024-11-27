<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import BelongIcons from "~/components/dashboard/classify/BelongIcons.vue";
import SelectGroup from "~/components/dashboard/common/SelectGroup.vue";

const props = defineProps({
  full_main: Object,
})


</script>

<template>
  <div class="py-2">
    <div class="d-flex flex-wrap align-center">
      <v-chip
        v-if="false"
        class="mb-2"
        prepend-icon="recent_actors"
        :text="full_main.name"
        color="indigo lighten-4"
        append-icon="edit"
        @click="editItem(full_main)"
      >
      </v-chip>
      <StatusChip
        v-if="full_main.status_validation"
        :main="full_main"
        collection="validation"
        class="mb-1 mr-2"
        only_icon
        x_small
        hide_details
      />
      <v-card
        rounded="xl"
        variant="plain"
        class="mx-2 d-flex"
      >
        <SelectGroup
          :main_object="full_main"
          filter_group_name="sectors"
          main_collection_name="actor"
          :width="160"
          is_display
        />
      </v-card>
      <div v-if="full_main.belongs.length" class="my-n1">
        <BelongIcons :actor="full_main"/>
      </div>
    </div>
    <div class="d-flex">
      <span class="text-h6">

        {{ full_main.name }}
      </span>

    </div>
  </div>
</template>

<style scoped>

</style>