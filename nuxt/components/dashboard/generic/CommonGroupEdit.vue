<script setup>

const props = defineProps({
  is_edit: Boolean,
  is_massive_edit: Boolean,
  full_main: {
    type: Object,
    required: true,
  },
})

</script>

<template>

  <v-row>
    <v-col cols="6">
      <v-text-field
        v-model="full_main.icon"
        label="Ícono (material icons)"
        variant="outlined"
        class="ml-2"
        _style="max-width: 200px;"
      />
    </v-col>
    <v-col cols="6">
      <v-text-field
        v-model="full_main.color"
        label="Color"
        variant="outlined"
        class="ml-2"
        _style="max-width: 200px;"
      />
    </v-col>
  </v-row>
</template>

<style scoped>

</style>