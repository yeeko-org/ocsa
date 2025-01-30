<script setup>

import { computed, ref } from 'vue'
import {useMainStore} from '~/store/index'

import {storeToRefs} from "pinia";
import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";
import PanelList from "~/components/dashboard/common/PanelList.vue";
import PanelsResult from "~/components/dashboard/common/PanelsResult.vue";

definePageMeta({
  middleware: 'dashboard',
  layout: 'dashboard',
})

const mainStore = useMainStore()
const {
  cats_ready,
  all_nodes,
  current_filter_group_data,
  schemas,
} = storeToRefs(mainStore)
const { setCollection } = mainStore

const levels = ['group', 'type', 'subtype']
const options_tab = ref('group')

const need_tabs = computed(() => {
  console.log('current_filter_group_data', current_filter_group_data.value)
  let filter_data = current_filter_group_data.value
  if (!filter_data)
    return false
  filter_data = filter_data.data
  return Boolean(filter_data.category_group || filter_data.category_type)
})

const filter_node = computed(() => current_filter_group_data.value)
const filter_group = computed(() => filter_node.value.data)

const level_names = computed(() => {
  return levels.reduce((acc, level) => {
    const cat_name = filter_group.value[`category_${level}`]
    if (cat_name)
      acc[level] = cat_name
    return acc
  }, {})
})

const collections = computed(() => {
  return Object.entries(level_names.value).reduce((acc, [level, cat_name]) => {
    acc[level] = schemas.value.collections_dict[cat_name]
    return acc
  }, {})
})

const group_results = computed(() => {
  if (!level_names.value.group)
    return []
  console.log("group_results", filter_node.value)
  console.log("filter_group", filter_group.value)
  console.log("level_names", level_names.value)
  const type_name = level_names.value.type
  return filter_node.value.children.map(child => {
    return {...child.data,
      [`${type_name}s_count`]: child.children ? child.children.length : 0}
  })
})

</script>

<template>
  <div v-if="current_filter_group_data && cats_ready" style="width: 100%">
    <CollectionDisplay
      v-if="!need_tabs"
      :parent_collection="collections.subtype"
    />
    <template v-else>
      <v-tabs
        v-model="options_tab"
        grow
        bg-color="accent"
      >
        <v-tab
          v-for="(collection, key) in collections"
          :key="key"
          :href="`#${key}`"
          @click="setCollection(collection.snake_name)"
        >
          {{ collection.plural_name }}
        </v-tab>
      </v-tabs>
      <v-tabs-window v-model="options_tab">
        <v-tabs-window-item
          v-for="(collection, key) in collections"
          :key="key"
          :value="key"
        >
<!--          <PanelList-->
<!--            v-if="key === 'group'"-->
<!--            :results="group_results"-->
<!--            :collection_data="collection"-->
<!--            show_details-->
<!--          />-->
          <div
            v-if="key === 'group'"
            class="mt-2"
          >
            <PanelsResult
              :results="group_results"
              :collection_data="collection"
              show_details
              in_sheet
            />
          </div>
          <CollectionDisplay
            v-else
            :parent_collection="collection"
            :filter_group="filter_group"
          />

        </v-tabs-window-item>
      </v-tabs-window>
    </template>
  </div>
  <v-progress-linear
    v-else
    color="yellow-darken-2"
    indeterminate
  ></v-progress-linear>
</template>
