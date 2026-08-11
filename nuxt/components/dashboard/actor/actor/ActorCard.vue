<script setup>

import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import BelongIcons from "~/components/dashboard/classify/BelongIcons.vue";
import DisplayGroup from "~/components/dashboard/common/select/DisplayGroup.vue";

const props = defineProps({
  full_main: Object,
  title: String,
  is_simple: {
    type: Boolean,
    default: false,
  },
})

// const full_main = defineModel({type: Object, required: true})

const full_belongs = computed(() => {
  return {belongs: props.full_main.belongs.map(b => ({"key_name": b}))}
})

</script>

<template>
  <div
    :class="{ 'py-2': !is_simple}"
  >
    <div class="d-flex flex-wrap align-center">
      <span v-if="title" class="text-body-small mr-2 text-grey-darken-2">
        ({{ title }})
      </span>
      <v-card
        rounded="xl"
        variant="plain"
        class="mr-2 d-flex"
      >
        <div
          v-if="full_main.status_validation === 'yk_proposed'
          && full_main.sector_text"
          class="px-3"
        >
          {{ full_main.sector_text }}
          <BelongIcons :actor="full_belongs"/>
        </div>
        <DisplayGroup
          v-else
          :main_object="full_main"
          filter_group_name="sectors"
          main_collection_name="actor"
          :width="160"
        />
      </v-card>
      <div v-if="full_main.belongs?.length" class="my-n1">
        <BelongIcons
          :actor="full_main"
          size="x-small"
        />
      </div>
      <StatusChip
        v-if="full_main.status_validation && !is_simple"
        :main="full_main"
        collection="validation"
        class="mb-1 mr-2"
        only_icon
        x_small
        hide_details
      />
    </div>
    <div class="d-flex align-center">
      <span
        :class="is_simple ? 'text-body-medium font-weight-medium' : 'text-title-large'"
      >
        {{ full_main.name }}
      </span>
      <span
        v-if="!is_simple && full_main.alternative_names"
        class="text-body-small ml-2 mt-1"
      >
        ({{ full_main.alternative_names }})
      </span>
    </div>
    <v-card
      v-if="full_main.participant_type"
      variant="elevated"
      class="d-flex align-center px-3"
    >
      <span class="text-accent mr-3">
        Agregar sugerencia como:
      </span>
      <DisplayGroup
        filter_group_name="participant_types"
        :main_object="full_main"
      />
    </v-card>
  </div>
</template>

<style scoped>

</style>