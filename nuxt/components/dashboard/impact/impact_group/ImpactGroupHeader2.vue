<script setup>

import {computed} from "vue";
import HeaderCommon from "~/components/dashboard/generic/HeaderCommon.vue";

import {useMainStore} from '~/store/index.js'
import {storeToRefs} from 'pinia'
const mainStore = useMainStore()
const { groups } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  mentions: Array,
  group: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  parent: String,
})

const final_group = computed(() => {
  return props.group || groups.value.find(gr => gr.key === 'note')
})

const note = computed(() => props.main)
// const emit = defineEmits(['open-panel'])


</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :group="final_group"
  >
  </HeaderCommon>
</template>

<style scoped>

</style>