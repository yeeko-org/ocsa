<script setup>
import HeaderCommon from "~/components/dashboard/common/generic/HeaderCommon.vue";
import HeaderChip from "~/components/dashboard/common/utils/HeaderChip.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    required: false,
    default: true,
  }
})
</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
    <template #details>
      <v-chip
        v-if="main.is_official"
        class="ml-3"
        size="small"
        color="primary"
        variant="tonal"
        label
      >
        INPI
        <v-tooltip activator="parent" location="bottom">
          Es del catálogo oficial del INPI
        </v-tooltip>
      </v-chip>
      <HeaderChip
        class="ml-3"
        :count="main.count"
        collection_name="actor"
      />
    </template>
  </HeaderCommon>
</template>

<style scoped>

</style>