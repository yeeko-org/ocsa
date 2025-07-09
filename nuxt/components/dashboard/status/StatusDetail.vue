<script setup>
import {defineComponent, ref, computed} from 'vue'
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'
import {useAuthStore} from "~/store/auth.js";
const authStore = useAuthStore()
const mainStore = useMainStore()
// export default defineComponent({
//   name: "StatusDetail"
// })
// const final_filters = ref({})
// const collection = ref("status_location")
const { is_staff } = storeToRefs(authStore);

const props = defineProps({
  final_filters: Object,
  collection: String,
  is_filter: Boolean,
  collection_group: {
    type: String,
    default: "status",
  },
  density: {
    type: String,
    default: "default",
  },
  hide_details: {
    type: Boolean,
    default: false,
  },
  // label: {
  //   type: String,
  //   default: "Status",
  // },
  // clearable: {
  //   type: Boolean,
  //   default: false,
  // },
  // hide_details: {
  //   type: Boolean,
  //   default: false,
  // },
})

const { status, cats } = storeToRefs(mainStore)

const simple_name = computed(() => {
  return props.collection.replace('status_', '');
})
const items_built = computed(() => {
  // const status_collection = props.collection.split('_')[1]
  return props.collection_group === "status"
      ? status.value[simple_name.value]
      : cats.value[simple_name.value]
})

const label = computed(() => {
  const txt = simple_name.value === 'register'
    ? "registro"
    : simple_name.value === 'validation'
      ? "validación"
      : "ubicación"
  return "Status de " + txt
})

const field = computed(() => {
  if (props.collection.includes('status_'))
    return props.collection
  return `status_${props.collection}`
})

const status_selected = computed(() => {
  const status_name = props.final_filters[field.value]
  if (!status_name) return {open_editor: true}
  return items_built.value.find(item => item.name === status_name)
})

</script>

<template>
  <v-select
    v-model="final_filters[field]"
    :items="items_built"
    item-title="public_name"
    item-value="name"
    :variant="is_filter ? 'underlined' : 'outlined'"
    :clearable="is_filter"
    :label="label"
    max-width="320"
    min-width="260"
    :hide-details="hide_details"
    density="compact"
    :readonly="!is_staff && !status_selected.open_editor"
  >
    <template #item="{ item, props: {onClick, title, value} }">
      <v-list-item
        @click="onClick"
        :title="title"
        :subtitle="item.raw.description"
        :value="value"
        :disabled="!is_filter && !is_staff && !item.raw.open_editor"
      >
        <template v-slot:prepend>
          <v-icon
            :color="item.raw.color || 'grey'"
            :icon="item.raw.icon || 'trip_origin'"
          ></v-icon>
        </template>
      </v-list-item>
    </template>
    <template #selection="{ item }">
      <div
        :class="`text-${item.raw.color || 'grey'}`"
        class="d-flex pb-1 pt-2"
      >
        <v-icon
          class="mr-2"
          :color="item.raw.color || 'grey'"
          :icon="item.raw.icon || 'trip_origin'"
        ></v-icon>
        {{ item.title }}
      </div>
    </template>

  </v-select>
</template>

<style scoped>

</style>