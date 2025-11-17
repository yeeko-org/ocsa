<script setup>

const props = defineProps({
  full_main: Object,
  in_map: Boolean,
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