<script setup>
// export default defineComponent({
//   name: "ActorHeader"
// })
import { defineProps } from 'vue'
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
import HeaderChip from "~/components/dashboard/common/HeaderChip.vue";
import ActorsChip from "~/components/dashboard/actor/ActorsChip.vue";
const mainStore = useMainStore()

const { positions, cats } = storeToRefs(mainStore)

const props = defineProps({
  actor: {
    type: Object,
    required: true,
  },
  show_details: {
    type: Boolean,
    required: false,
    default: true,
  }
})

const emit = defineEmits(['open-panel'])

const position = computed(() => {
  return positions.value[props.actor.position]
})


</script>
<template>
  <v-expansion-panel-title
    class="pl-0 py-0"
    color="blue-lighten-5"
    style="min-height: 60px;"
    @click="emit('open-panel')"
  >
    <v-icon>newspaper</v-icon>
    <v-toolbar-title
      class="text-subtitle-1 mr-6"
      style="max-width: 300px;"
    >
      <div
        class="ml-2"
        style="text-wrap: pretty; width: 300px; max-height: 54px; overflow: hidden;"
        v-tooltip:bottom="actor.name"
      >{{ actor.name }}</div>
    </v-toolbar-title>
    <HeaderChip
      :count="actor.mentions_count"
      icon="newspaper"
      label="mención"
      label_plural="menciones"
      color="deep-purple"
      class="ml-2"
    />
    <ActorsChip
      :main="actor"
      :participants="actor.participants"
      field="project"
      subfield="official_name"
      class="ml-2"
    />
  </v-expansion-panel-title>

</template>

<style scoped>

</style>