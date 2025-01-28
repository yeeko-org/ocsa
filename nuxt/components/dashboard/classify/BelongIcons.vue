<script setup>
import { useMainStore } from '~/store/index.js'
import { storeToRefs } from 'pinia'
const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  actor: {
    type: Object,
    required: true,
  },
})

const all_belongs = computed(() => {
  return cats.value.belong.filter(
      belong => props.actor.belongs.includes(belong.key_name))
})

</script>

<template>
  <v-btn
    v-for="belong in all_belongs"
    :key="belong.key_name"
    icon
    size="small"
    variant="tonal"
    color="secondary"
    class="ml-2"
  >
    <v-icon
      size="large"
    >
      {{ belong.icon }}
    </v-icon>
    <v-tooltip
      location="bottom"
      activator="parent"
    >
      {{ belong.name }}
    </v-tooltip>

  </v-btn>
</template>

<style scoped>

</style>