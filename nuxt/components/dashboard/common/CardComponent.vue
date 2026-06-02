<script setup>

import {shallowRef} from "vue";
const props = defineProps({
  collection_data: {
    type: Object,
    required: true,
  },
  full_main: {
    type: Object,
    required: true,
  },
  title: String,
  note_id: Number,
})

const card_component = shallowRef('')
const route_key = computed(() => props.collection_data.app_label)
const snake_name = computed(() => props.collection_data.snake_name)
const card_name = computed(() => `${props.collection_data.model_name}Card`)

import(`~/components/dashboard/${route_key.value}/${snake_name.value}/${card_name.value}.vue`)
  .then(module => {
    card_component.value = module.default
  })
  .catch(e => {
    import(`~/components/dashboard/common/generic/CardGeneric.vue`).then(module => {
      card_component.value = module.default
    })
  })
</script>

<template>
  <component
    v-if="card_component && full_main"
    :is="card_component"
    :full_main="full_main"
    :title="title"
    :note_id="note_id"
  />
  <span v-else class="text-title-large mr-2 text-warning">
    Sin {{title || collection_data.name}}
  </span>
</template>

<style scoped>

</style>