<script setup>

import TitleCommon from "~/components/dashboard/generic/TitleCommon.vue";
import {computed} from "vue";
import dayjs from "dayjs";
import {storeToRefs} from "pinia";
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
const { cats } = storeToRefs(mainStore)

const props = defineProps({
  main: Object,
  forced_title: Boolean,
})

const source = computed(() => {
  return cats.value.source.find(src => src.id === props.main.source)
})

const pretty_date = computed(() => {
  return dayjs(props.main.date).format("DD/MM/YYYY")
})
</script>

<template>
  <div class="d-flex flex-column align-start justify-start">
    <div class="ml-2 text-caption">
      <span class="text-grey-darken-1">
        {{pretty_date}}
      </span>
      <span class="text-purple-darken-1 ml-3">
        {{source.name}}
      </span>
    </div>
    <div
      v-if="forced_title"
      class="ml-2 text-body-1 text-purple-darken-3"
    >
      {{ main.title }}
    </div>
    <TitleCommon
      v-else
      :title_text="main.title"
      card_class="ml-2 font-weight-normal text-body-1 mt-n1"
    />
  </div>

</template>

<style scoped>

</style>