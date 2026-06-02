<script setup>
// Ícono de ayuda (help_outline) con tooltip de título + descripción.
// Extraído de CollectionListMap.vue (líneas 117-139) para no duplicar el
// patrón en los títulos de los pickers/grupos de filtros del mapa.
// Se auto-oculta si no hay descripción que mostrar.
defineProps({
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  color: { type: String, default: 'primary' },
})
</script>

<template>
  <v-sheet v-if="description" class="d-flex align-center" color="transparent">
    <v-icon :color="color" class="ml-2">help_outline</v-icon>
    <v-tooltip
      activator="parent"
      location="bottom left"
      max-width="400"
      color="primary"
      :content-props="{ background: 'white' }"
    >
      <div v-if="title" class="font-weight-bold pt-3 pb-2">{{ title }}:</div>
      <div class="text-subtitle-2 pb-3">{{ description }}</div>
    </v-tooltip>
  </v-sheet>
</template>