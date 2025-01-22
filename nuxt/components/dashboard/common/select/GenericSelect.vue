<script setup>

import CollectionDisplay from "~/components/dashboard/CollectionDisplay.vue";

const props = defineProps({
  main_object: {
    type: Object,
    required: true,
  },
  level: String,
  level_name: String,
  collection_data: Object,

  is_filter: Boolean,
  filter_null: Boolean,
  filter_multiple: Boolean,

  main_width: Number,
  item_value: {
    type: String,
    default: 'id',
  },
  item_title: {
    type: String,
    default: 'name',
  },
  items: {
    type: Array,
    required: true,
  },
  is_display: Boolean,
  is_multiple: Boolean,
  required: Boolean,
})

const dialog_add = ref(false)
const emits = defineEmits(['open-dialog'])

const final_value = computed(() => {
  if (props.is_multiple){
    // console.log("is_multiple", props.main_object[props.level_name])
    return props.main_object[props.level_name].map(
        item1 => props.items.find(
            item2 => item2[props.item_value] === item1))
  }
  return props.items.find(
    item => item[props.item_value] === props.main_object[props.level_name])
})

const show_add = computed(() => {
  if (props.is_filter)
    return false
  if (!props.collection_data)
    return false
  return props.collection_data.open_insertion
})

const rules = computed(() => {
  const rules = []
  if (props.required)
    rules.push(value => !!value || 'Campo requerido')
  return rules
})

function disabledNull(){
  props.main_object[`${props.level_name}_null`] = null
}

function sendNull(){
  props.main_object[props.level_name] = null
  props.main_object[`${props.level_name}_null`] = true
}

function openDialog(){
  emits('open-dialog')
}

</script>

<template>
  <div
    v-if="is_display"
    class="mr-0 px-2"
    style="border-right: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0;"
  >
    <template v-if="final_value && is_multiple">
      <template v-if="level === 'group'">
        <v-icon
          v-for="item in final_value"
          class="mr-1"
          :color="item.color || 'primary'"
          v-tooltip="item[item_title]"
        >
          {{ item.icon }}
        </v-icon>
      </template>
      <div v-else>
        <div
          v-for="item in final_value"
          class="mr-1"
        >
          {{ item[item_title] }}
        </div>
      </div>
    </template>

    <template v-else-if="final_value">
      <v-icon
        v-if="['group', 'type'].includes(level) && final_value.icon"
        class="mr-1"
        :color="final_value.color || 'primary'"
        v-tooltip="final_value[item_title]"
      >
        {{ final_value.icon }}
      </v-icon>
      <v-chip
        v-else-if="final_value.color"
        :color="final_value.color"
        :prepend-icon="final_value.icon"
        size="small"
      >
        {{final_value[item_title]}}
      </v-chip>
      <span
        v-else
      >
        {{final_value[item_title]}}
      </span>
    </template>
    <span v-else>
      !?
    </span>
  </div>
  <v-select
    v-else
    v-model="main_object[level_name]"
    :items="items"
    :item-title="item_title"
    :item-value="item_value"
    :variant="is_filter ? 'underlined' : 'outlined'"
    :clearable="is_filter"
    :hide-details="is_filter"
    :density="is_filter ? 'compact' : 'default'"
    :style="`max-width: ${main_width}px; min-width: ${main_width}px;`"
    :multiple="is_multiple || filter_multiple"
    :rules="rules"
    @update:model-value="disabledNull"
  >
    <template #append-item v-if="show_add">
      <div class="px-2">
        <v-btn
          variant="elevated"
          color="accent"
          class="mt-3 mb-1"
          append-icon="add"
          block
          @click="openDialog"
        >
          Agregar
        </v-btn>
      </div>
    </template>
    <template #append-item v-else-if="filter_null">
      <v-list-item
        title="Filtrar vacíos"
        @click="sendNull"
      >
        <template v-slot:prepend>
          <v-icon
            class="mr-n3"
            :color="'grey'"
            :icon="'circle'"
          ></v-icon>
        </template>
      </v-list-item>

    </template>
    <template #item="{ item, props: {onClick, title, value} }">
      <v-list-item
        @click="onClick"
        :title="title"
        :subtitle="item.raw.description"
        :value="value"
      >
        <template v-slot:prepend v-if="item.raw.icon">
          <v-icon
            :color="item.raw.color || 'grey'"
            :icon="item.raw.icon || 'trip_origin'"
          ></v-icon>
        </template>
      </v-list-item>
    </template>
    <template #selection="{ item }" v-if="!is_multiple">
      <v-icon
        v-if="item.raw.icon"
        :color="item.raw.color || 'grey'"
        :icon="item.raw.icon || 'trip_origin'"
        class="mr-2"
      ></v-icon>
      {{ item.title }}
    </template>

<!--    <template #item="{ item, props: {onClick, title, value} }">-->
<!--      <v-list-item-->
<!--        @click="onClick"-->
<!--        :title="title"-->
<!--        :subtitle="item.raw.description"-->
<!--      >-->
<!--      </v-list-item>-->
<!--    </template>-->
<!--    <template #item="{ item, props: {onClick, title, value} }" v-if="true">-->
<!--      <v-list-item-->
<!--        @click="onClick"-->
<!--      >-->
<!--        <v-list-item-title>-->
<!--          <b class="mr-1"> {{ item.title }} </b>-->
<!--          <span v-if="item.raw.has_subtype">-->
<!--            (tiene subtipos)-->
<!--          </span>-->
<!--        </v-list-item-title>-->
<!--        <v-list-item-subtitle>-->
<!--          {{ item.raw.description }}-->
<!--        </v-list-item-subtitle>-->
<!--      </v-list-item>-->
<!--    </template>-->
<!--    </v-select>-->
<!--  </template>-->
  </v-select>
</template>

<style scoped>

</style>