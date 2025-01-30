<script setup>
import PanelList from "~/components/dashboard/common/PanelList.vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    default: false,
  },
})

const note_collection = computed(() => {
  return schemas.value.collections_dict['note']
})

</script>

<template>
  <v-card class="mb-4 pa-3">
    Nota en la que se menciona:
    <PanelList
      v-if="full_main.note"
      :results="[full_main.note]"
      :collection_data="note_collection"
      :show_details="true"
    />
  </v-card>
</template>

<style scoped>

</style>