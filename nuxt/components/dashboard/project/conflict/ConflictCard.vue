<script setup>

import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)

const props = defineProps({
  full_main: Object,
})


</script>
<template>
  <div class="d-flex align-center">
    <v-icon
      color="pink"
      class="mr-2"
    >
      local_fire_department
    </v-icon>
    <div class="text-subtitle-1">
      {{ full_main.name }}
    </div>
  </div>
</template>

<style scoped>

</style>