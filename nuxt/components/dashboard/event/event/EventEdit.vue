<script setup>

import EventDetails from "~/components/dashboard/event/event/EventDetails.vue";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
const props = defineProps({
  is_massive_edit: Boolean,
  is_edit: Boolean,
  col_order: {
    type: Number,
    default: 5,
  }
})
const full_main = defineModel({type: Object, required: true})


</script>

<template>
  <v-col :order="col_order">
    <v-alert
      type="info"
    >
      No guardes desde aquí
    </v-alert>
<!--    <SelectGroup-->
<!--      filter_group_name="event_types"-->
<!--      :main_object="full_main"-->
<!--      main_collection_name="event"-->
<!--      :width="360"-->

<!--    />-->
<!--    <EventDetails-->
<!--      :full_main="full_main"-->
<!--      is_edit-->
<!--    />-->
  </v-col>
</template>

<style scoped>

</style>