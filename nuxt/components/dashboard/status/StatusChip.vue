<script setup>
import { computed } from 'vue';
import { useMainStore } from '~/store'
import { storeToRefs } from 'pinia'

const props = defineProps({
  main: {
    type: Object,
    required: true,
  },
  collection: {
    type: String,
    required: true,
  },
  hide_details: {
    type: Boolean,
    required: false,
    default: false,
  },
  left_label: {
    type: Boolean,
    required: false,
    default: false,
  },
  bold_text: {
    type: Boolean,
    required: false,
    default: false,
  },
  small: {
    type: Boolean,
    required: false,
    default: true,
  },
  x_small: {
    type: Boolean,
    required: false,
    default: false,
  },
  disabled: {
    type: Boolean,
    required: false,
    default: false,
  },
  show_icon: {
    type: Boolean,
    required: false,
    default: true,
  },
  only_icon: {
    type: Boolean,
    required: false,
    default: false,
  },
});
const mainStore = useMainStore();

const want_edit_note = ref(false);

const { status_dict } = storeToRefs(mainStore);

// Compute item_built using the status_dict and props
const field = computed(() => `status_${props.collection}`);
const item_built = computed(() => {
  const status_field = props.main[field.value];
  return status_dict.value[props.collection][status_field] ||
    {
      public_name: "Sin definir",
      color: "grey",
      color_text: "white",
      icon: "help",
      back_text: "grey--text text--darken-1",
    };
});

const label = computed(() => {
  switch (props.collection) {
    case 'register':
      return 'Registro:';
    case 'validation':
      return 'Validación:';
    case 'location':
      return 'Ubicación:';
    default:
      return 'Status:';
  }
  // return props.collection === 'register'
  //   ? 'Registro:' : 'Validación:';
})

</script>

<template>
  <div
    class="d-flex text-body-3 align-center"
    :class="props.left_label ? 'flex-row mb-1' : 'flex-column'"
  >
    <span
      v-if="!props.hide_details"
      class="text-caption text-grey-darken-1"
      :class="props.left_label ? 'mr-2' : 'mb-n1'"
    >
      {{ label }}
    </span>
    <v-icon
      v-if="props.x_small"
      :color="item_built.color"
      class="ml-1"
      x-small
    >{{item_built.icon}}</v-icon>
    <v-chip
      v-else
      :color="item_built.color || 'grey'"
      :size="(props.disabled || props.small) ? 'small' : 'default'"
      :disabled="props.disabled"
      :icon="props.only_icon"
      :class="`${item_built.back_text} ${props.bold_text ? 'font-weight-bold' : ''}`"
      variant="flat"
    >
      <v-icon
        v-if="props.show_icon"
        :color="item_built.color_text"
        class="mr-1"
        :size="(props.disabled || props.small) ? 'small' : 'default'"
      >
        {{(!item_built.icon || item_built.icon === 'mdi-check-circle')
          ? 'fiber_manual_record'
          : item_built.icon
        }}
      </v-icon>
      <template v-if="!props.only_icon">
        {{ item_built.public_name }}
      </template>
    </v-chip>
    <v-tooltip
      activator="parent"
      location="end"
    >
      <div
        style="max-width: 400px;"
        :class="item_built.back_text"
      >
        <b>{{item_built.public_name}}</b> <br>
        {{item_built.description || 'Sin descripción'}}
      </div>
    </v-tooltip>
  </div>
</template>

<style lang="scss">

</style>
