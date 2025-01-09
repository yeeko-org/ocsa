<script setup>

const props = defineProps({
  results: {
    type: Array,
    required: true,
  },
  sel: {
    type: Object,
    required: true,
  },
  collection_data: {
    type: Object,
    required: true,
  },
})

const emits = defineEmits([
    'want-merge', 'want-massive-edit', 'select-all'
])

const all_selected = computed(() => {
  return props.results.length === props.sel.selected_elems.length
})

</script>

<template>
  Acciones grupales:
  <span
    v-if="sel.selected_elems.length"
  >({{sel.selected_elems.length}}):</span>
  <v-btn
    :variant="all_selected ? 'elevated' : 'outlined'"
    color="accent"
    class="ml-3"
    :disabled="props.results.length < 2"
    @click="emits('select-all')"
    size="small"
    :icon="all_selected ? 'check_box' : 'check_box_outline_blank'"
  ></v-btn>
  <v-btn
    v-if="collection_data.available_actions.includes('merge')"
    outlined
    color="accent"
    class="ml-3"
    variant="elevated"
    @click="emits('want-merge')"
    :disabled="!sel.selected_elems.length"
  >
    <v-icon class="mr-2">merge</v-icon>
    Fusionar
  </v-btn>
  <v-btn
    v-if="collection_data.available_actions.includes('massive_edit')"
    outlined
    color="accent"
    class="ml-3"
    @click="emits('want-massive-edit')"
    :disabled="!sel.selected_elems.length"
  >
    <v-icon class="mr-2">app_registration</v-icon>
    Edición masiva
  </v-btn>
  <v-btn
    v-if="collection_data.available_actions.includes('massive_delete')"
    :disabled="!sel.selected_elems.length"
    outlined
    color="error"
    class="ml-3"
  >
    <v-icon class="mr-2">delete</v-icon>
    Eliminar
  </v-btn>
  <v-btn
    v-if="false"
    icon="close"
    class="float-right"
    size="small"
    variant="text"
    @click="changeGroupActions"
  ></v-btn>

</template>

<style scoped>

</style>