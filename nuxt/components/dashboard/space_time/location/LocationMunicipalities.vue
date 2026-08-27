<script setup>

const props = defineProps({
  municipalities_full: {
    type: Array,
    default: () => [],
  },
  type_location: {
    type: String,
    default: null,
  },
})

const VISIBLE_COUNT = 8

const expanded = ref(false)

// Un punto con un solo municipio ya lo muestra el selector de LocationMex
const show = computed(() => props.municipalities_full.length > 0
    && (props.municipalities_full.length > 1
        || props.type_location !== 'point'))

const visible = computed(() => expanded.value
    ? props.municipalities_full
    : props.municipalities_full.slice(0, VISIBLE_COUNT))

const hidden_count = computed(
    () => props.municipalities_full.length - VISIBLE_COUNT)

</script>

<template>
  <div
    v-if="show"
    class="d-flex align-center flex-wrap ga-1 mb-2"
  >
    <span class="text-body-2 text-medium-emphasis mr-1">
      Municipios que abarca la ubicación:
    </span>
    <v-chip
      v-for="mun in visible"
      :key="mun.id"
      size="small"
      variant="tonal"
    >
      {{ mun.name }}
    </v-chip>
    <v-btn
      v-if="hidden_count > 0"
      variant="text"
      size="small"
      color="accent"
      @click="expanded = !expanded"
    >
      {{ expanded ? 'ver menos' : `ver ${hidden_count} más` }}
    </v-btn>
  </div>
</template>
