<script setup>

import ParagraphsProjectsContent from "~/components/dashboard/capture/ParagraphsProjectsContent.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import {computed} from "vue";
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import CardComponent from "~/components/dashboard/common/CardComponent.vue";

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

// const dialog_visible = defineModel({ type: Boolean, default: false });
const props = defineProps({
  show_base: Boolean,
  full_main: Object,
  full_article: Object,
  collection_data: Object,
  collection_name: String,
  title: String,
  note_id: Number,
  init_filters: {
    type: Object,
    default: () => ({}),
  },
});
const emits = defineEmits(['selected-item', 'close-dialog']);

const base_element = computed(() => {
  if (!props.show_base) return false
  // if (!props.collection_data) return false;
  // return true
  return !!final_collection_data.value
})

const final_collection_data = computed(() => {
  if (props.collection_data)
    return props.collection_data
  else if (props.collection_name)
    return schemas.value.collections_dict[props.collection_name]
  return null
})

// function closeSearchDialog(new_item) {
//   if (new_item)
//     emits('selected-item', new_item)
//   // dialog_visible.value = false
//   emits('close-dialog')
// }
</script>

<template>
<!--  <v-dialog-->
<!--    v-model="dialog_visible"-->
<!--    max-width="920"-->
<!--  >-->
  <v-card>
    <v-card-text class="py-0 px-0">
      <v-row
        no-gutters
        :class="{ 'dual-scroll-layout ga-3': base_element || true }"
        class="my-0"
      >
        <v-col
          v-if="base_element"
          cols="5"
          class="scroll-column px-2 mx-0"
        >
          <v-card
            class="d-flex align-center px-3"
            :color="final_collection_data.color"
            variant="tonal"
            style="width: 100%;"
          >
            <CardComponent
              :full_main="full_main"
              :collection_data="final_collection_data"
              title=""
            />

          </v-card>
          <ParagraphsProjectsContent
            v-if="full_article && full_article.second_criteria"
            :full_main="full_article"
            :sending_link="false"
            :note_id="note_id"
            class="mx-n1 px-2"
            :show_init="false"
            two_columns
          />
        </v-col>
        <v-col
          :cols="base_element ? 7 : 12"
          :class="{ 'scroll-column': true }"
          class="px-2 mx-0"
        >
          <CollectionDisplay
            :parent_collection="final_collection_data"
            is_mini
            @select-item="emits('selected-item', $event)"
            :init_filters="init_filters"
          />
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
<!--  </v-dialog>-->
</template>


<style scoped>

.dual-scroll-layout {
  height: calc(100vh - 100px); /* Ajusta según tu layout */
  flex-wrap: nowrap !important;
  margin-top: 8px;
}

.scroll-column {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

/* Scrollbar personalizado (opcional) */
.scroll-column::-webkit-scrollbar {
  width: 8px;
}

.scroll-column::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.scroll-column::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.scroll-column::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>