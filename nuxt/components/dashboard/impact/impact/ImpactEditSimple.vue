<script setup>

import ImpactToolbar from "~/components/dashboard/impact/impact/ImpactToolbar.vue";

const full_main = defineModel({type: Object, required: true})
const impacts = ref([])

// const artificial_mention = computed(() => {
//   return {"impacts": [full_main.value]}
// })
watch(
  full_main, (newVal) => {
    impacts.value = [newVal]
  }, {immediate: true}
)

</script>

<template>
  <v-col
    cols="12"
    class="d-flex pa-0"
    :order="col_order"
  >
    <v-card class="mb-4 pa-0">
      <ImpactToolbar
        v-model="impacts"
      />
    </v-card>
  </v-col>
</template>

<style scoped>

</style>