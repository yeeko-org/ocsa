<script setup>
const props = defineProps({
  description: {
    type: String,
    default: '',
  },
})

const show_text = ref(false)

</script>

<template>
  <div>
<!--    <v-tooltip-->
<!--      v-if="description"-->
<!--      :text="description"-->
<!--      location="bottom"-->
<!--      max-width="300"-->
<!--    >-->
<!--      <template v-slot:activator="{ props }">-->
<!--        <v-btn-->
<!--          v-bind="props"-->
<!--          icon-->
<!--          color="transparent"-->
<!--          class="mt-n1 mb-n1 ml-2"-->
<!--          variant="flat"-->
<!--          size="x-small"-->
<!--        >-->

<!--          <v-icon size="x-large">-->
<!--            subject-->
<!--          </v-icon>-->
<!--        </v-btn>-->
<!--      </template>-->
<!--    </v-tooltip>-->
    <span class="caption" v-if="description">
      {{ description }}
    </span>
  </div>

</template>

<style scoped>

</style>