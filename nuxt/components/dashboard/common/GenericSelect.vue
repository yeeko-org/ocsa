<script setup>

const props = defineProps({
  main_object: {
    type: Object,
    required: true,
  },
  level: String,
  level_name: String,
  is_filter: Boolean,
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
})

const text_value = computed(() => {
  if (props.is_multiple){
    // console.log("is_multiple", props.main_object[props.level_name])
    return props.main_object[props.level_name].map(
        item1 => props.items.find(
            item2 => item2[props.item_value] === item1))
  }
  return props.items.find(
      item => item[props.item_value] === props.main_object[props.level_name])
})

</script>

<template>
  <div
    v-if="is_display"
    class="mr-0 px-2"
    style="border-right: 1px solid #e0e0e0; border-bottom: 1px solid #e0e0e0;"
  >
    <template v-if="text_value && is_multiple">
      <template v-if="level === 'group'">
        <v-icon
          v-for="item in text_value"
          class="mr-1"
          :color="item.color || 'primary'"
          v-tooltip="item[item_title]"
        >
          {{ item.icon }}
        </v-icon>
      </template>
      <div v-else>
        <div
          v-for="item in text_value"
          class="mr-1"
        >
          {{ item[item_title] }}
        </div>
      </div>
    </template>

    <template v-else-if="text_value">
      <v-icon
        v-if="level === 'group' && text_value.icon"
        class="mr-1"
        :color="text_value.color || 'primary'"
        v-tooltip="text_value[item_title]"
      >
        {{ text_value.icon }}
      </v-icon>
      <span v-else>
        {{text_value[item_title]}}
      </span>
    </template>
    <span v-else>
      ?
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
    :style="`max-width: ${main_width}px; min-width: ${main_width}px;`"
    :multiple="is_multiple"
  >
    <template #append-item>
      <v-icon
        color="primary"
        icon="trip_origin"
      ></v-icon>
    </template>
    <template #item="{ item, props: {onClick, title, value} }">
      <v-list-item
        @click="onClick"
        :title="title"
        :subtitle="item.raw.description"
        :value="value"
      >
        <template v-slot:prepend v-if="false">
          <v-icon
            :color="item.raw.color || 'grey'"
            :icon="item.raw.icon || 'trip_origin'"
          ></v-icon>
        </template>
      </v-list-item>
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