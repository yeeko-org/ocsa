<script setup>
import {useStatusGroup} from '~/composables/useStatusGroup.js'

const props = defineProps({
  main: {
    type: Object,
    required: true,
  },
  collection: {
    type: [String, Object],
    required: true,
  },
  hide_details: Boolean,
  left_label: Boolean,
  custom_class: {
    type: String,
    required: false,
    default: 'flex-column',
  },
  x_small: Boolean,
  disabled: Boolean,
  only_icon: Boolean,
  show_icon: {
    type: Boolean,
    required: false,
    default: true,
  },
  chip_variant: {
    type: String,
    required: false,
    default: 'flat',
  },
  chip_size: {
    type: String,
    required: false,
    default: 'default',
  },
});

const {short_label, display} = useStatusGroup(() => props.collection, {
  record: () => props.main,
})
</script>

<template>
  <div
    v-if="display"
    class="d-flex text-body-medium align-center"
    :class="custom_class"
  >
    <span
      v-if="!props.hide_details"
      class="text-body-small text-grey-darken-1"
      :class="props.left_label ? 'mr-1' : 'mb-n1'"
    >
      {{ short_label }}
    </span>
    <v-icon
      v-if="props.x_small"
      :color="disabled ? `${display.color}-lighten-2` : display.color"
      class="ml-1"
      x-small
    >{{display.icon}}</v-icon>
    <v-chip
      v-else
      :color="display.color || 'grey'"
      :size="props.disabled ? 'small' : chip_size"
      :disabled="props.disabled"
      :icon="props.only_icon"
      :class="display.back_text"
      :variant="props.chip_variant"
    >
      <v-icon
        v-if="props.show_icon"
        :color="display.color_text"
        class="mr-1"
      >
        {{(!display.icon || display.icon === 'check_circle')
          ? 'fiber_manual_record'
          : display.icon
        }}
      </v-icon>
      <template v-if="!props.only_icon">
        {{ display.public_name }}
      </template>
    </v-chip>
    <v-tooltip
      activator="parent"
      location="end"
    >
      <div
        style="max-width: 300px;"
        :class="display.back_text"
      >
        <b>{{display.public_name}}</b> <br>
        {{display.description || '--'}}
      </div>
    </v-tooltip>
  </div>
</template>

<style lang="scss">

</style>
