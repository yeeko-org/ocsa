<script setup>

const props = defineProps({
  element_value: {
    type: [Array, String, Number],
    required: false,
  },
  level: String,
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
  is_multiple: Boolean,
})

const final_value = computed(() => {
  if (props.is_multiple){
    return props.element_value.map(
        item1 => props.items.find(
            item2 => item2[props.item_value] === item1))
  }
  return props.items.find(
    item => item[props.item_value] === props.element_value)
})

</script>

<template>
  <div
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
        {{ final_value[item_title] }}
      </v-chip>
      <span
        v-else
      >
        {{ final_value[item_title] }}
      </span>
    </template>
    <span v-else>
      !?
    </span>
  </div>
</template>

<style scoped>

</style>