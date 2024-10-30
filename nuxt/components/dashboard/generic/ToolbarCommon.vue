<script setup>
import { computed } from 'vue'
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import SelectGroup from "~/components/dashboard/common/SelectGroup.vue";

const props = defineProps({
  main_object: Object,  // Mention
  main_collection_name: String,  // Mention
  filter_group_name: String,  // event_types
  child_relation_name: String,  // event
  field: String,  // events
  hide_select: Boolean,
  second_level: Boolean,
  slot_before: Boolean,
  two_columns: Boolean,
  cols: {
    type: Number,
    default: 12,
  },
  color: {
    type: String,
    default: 'indigo',
  },
})

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const filter_group = computed(() =>
  schemas.value.filter_groups.find(
    group => group.key_name === props.filter_group_name)
)

const main_collection = computed(() =>
  schemas.value.collections_dict[props.main_collection_name])

// Event Collection
const child_collection = computed(() =>
  schemas.value.collections_dict[props.child_relation_name])

// const child_relation = computed(() =>{
//   // console.log("main_collection", main_collection.value)
//   // console.log("main_object", props.main_object)
//   // console.log("filter_group", filter_group.value)
//   // console.log("child_collection", child_collection.value)
//   const main = main_collection.value.child_relations.find(
//     child => child.child === props.child_relation_name)
//   // console.log("child_relation", main)
//   return main
// })

// const field = computed(() => `${props.child_relation_name}s`)

const addItem = (group=null) => {
  let new_child = {}
  if (group)
    new_child[filter_group.value.category_group] = group.id
  // props.collection[props.field].push(new_child)
  props.main_object[props.field].push(new_child)
}

const deleteRecord = (index) => {
  console.log("index", index)
  // props.main_object[field.value].splice(index, 1)
}

</script>


<template>
  <v-col :cols="cols" class="py-2 px-2">
    <v-card
      :class="second_level ? 'mt-2' : ''"
      elevation="4"
      variant="elevated"
      :color="`${color}-lighten-${second_level ? 4 : 3}`"
    >
      <v-toolbar
        :color="`${color}-lighten-${second_level ? 2 : 1}`"
        _clipped-left="second_level"
        _class="second_level ? 'ml-6 pr-8' : ''"
        :height="second_level ? 32 : 46"
      >
        <v-toolbar-title
          style="min-width: 300px;"
          :class="second_level ? '' : 'text-h6'"
        >
    <!--      Eventos ({{mention.events.length}})-->
          {{child_collection.plural_name}} ({{main_object[field].length}})
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn
          class="hidden-xs-only"
          icon
          :size="second_level ? 'small' : 'default'"
        >
          <v-icon>question_mark</v-icon>
        </v-btn>
        <template v-if="filter_group.category_groups">
          <v-btn
            v-for="group in filter_group.category_groups"
            :key="group.name"
            class="ml-2 text-none"
            :color="group.color"
            variant="flat"
            @click="addItem(group)"
          >
            <v-badge color="transparent" icon="add">
              <v-icon
                color="white"
                :icon="group.icon"
              ></v-icon>
            </v-badge>
          </v-btn>
        </template>
        <v-btn
          v-else
          class="mr-2 text-none"
          color="success"
          variant="flat"
          @click="addItem()"
          :size="second_level ? 'small' : 'default'"
        >
          <v-icon>add</v-icon>
        </v-btn>
      </v-toolbar>
      <v-card
        v-for="(item, index) in main_object[field]"
        :key="index"
        class="ma-2"
        elevation="2"
        variant="flat"
        :color="second_level ? 'white' : `${color}-lighten-5`"
      >
        <v-row
          no-gutters
          class="d-flex flex-wrap"
          _class="{'ml-6': second_level && !two_columns}"
        >
          <v-col
            :cols="two_columns ? 6 : 12"
            class="pa-2"
          >
            <slot name="rows_init" :item="item">
            </slot>
            <div v-if="!hide_select" class="d-flex flex-wrap">
              <SelectGroup
                :filter_group_name="filter_group_name"
                :main_collection="child_collection"
                :main_object="item"
                @delete-record="deleteRecord(index)"
              />
            </div>
            <slot name="rows" :item="item">
            </slot>
          </v-col>
          <v-col
            v-if="two_columns"
            cols="6"
            class="my-0"
          >
            <slot name="second-column" :item="item">
            </slot>
          </v-col>
        </v-row>
      </v-card>
      <v-alert
        v-if="!main_object[field].length"
        type="warning"
        variant="flat"
        border="start"
        :text="`Debes agregar al menos un ${child_collection.name}`"
      >
        <v-btn
          color="success"
          class="ml-2"
          variant="tonal"
          @click="addItem()"
        >
          Agregar
        </v-btn>
      </v-alert>
    </v-card>
  </v-col>
</template>

<style scoped>

</style>