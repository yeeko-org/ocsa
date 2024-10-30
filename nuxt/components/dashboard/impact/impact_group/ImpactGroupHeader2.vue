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
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  parent: String,
})

// const emit = defineEmits(['open-panel'])


</script>

<template>
  <HeaderCommon
    :main="main"
    :show_details="show_details"
    :collection_data="collection_data"
  >
  </HeaderCommon>
</template>

<style scoped>

</style>