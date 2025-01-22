<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import PanelsResult from "~/components/dashboard/common/PanelsResult.vue";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";

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
  collection_data: Object,
})

// const init_filters = ref({page: 1, page_size: 40})

const child_collections = computed(() => {
  if (!props.collection_data)
    return []
  console.log("collection_data", props.collection_data)
  let collections = []
  props.collection_data.child_relations.forEach(child => {
    let is_category = false
    if (!child.is_multiple && child.link_type !== "category")
      is_category = true
    const child_collection = schemas.value.collections_dict[child.child]
    const results = props.full_main[`${child.child}s`]
    const count = props.full_main[`${child.child}s_count`]
    let child_data = {
      collection_data: child_collection,
      relation: child,
      count: count,
    }
    if (results || !is_category){
      child_data.results = results
      collections.push(child_data)
    }
    else if (is_category && count !== undefined && count !== null){
      collections.push(child_data)
    }
  })
  // console.log("result", result)
  return collections
})

const elem_id = computed(() => {
  return props.collection_data.pk
})

</script>

<template>
  <v-card
    v-for="child_collection in child_collections"
    :key="child_collection.relation.id"
    class="mb-4"
  >
    <v-card-title>
      {{ child_collection.collection_data.plural_name }}
      <span v-if="child_collection.results">
        ({{ child_collection.results.length }})
      </span>
      <span v-else-if="child_collection.count !== null && child_collection.count !== undefined">
        ({{ child_collection.count }})
      </span>
      <span v-else class="text-error">
        Sin data heredada!!
      </span>
    </v-card-title>
    <v-card-text>
<!--      <PanelList-->
<!--        v-if="false"-->
<!--        :results="child_collection.results"-->
<!--        :collection_data="child_collection.collection_data"-->
<!--        :show_details="show_details"-->
<!--      />-->
      <PanelsResult
        v-if="child_collection.results"
        :results="child_collection.results"
        :collection_data="child_collection.collection_data"
        :show_details="show_details"
        :total_count="child_collection.results.length"
        in_sheet
      />
      <CollectionDisplay
        v-else
        :parent_collection="child_collection.collection_data"
        :init_filters="{[collection_data.snake_name]: props.full_main[elem_id]}"
        :init_total_count="child_collection.count"
        direct_sheet
      />
    </v-card-text>
  </v-card>
</template>

<style scoped>

</style>