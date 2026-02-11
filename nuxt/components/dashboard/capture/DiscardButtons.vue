<script setup>
defineProps({
  discarded: {
    type: [Boolean, null],
    required: true,
  },
  can_edit_pre_save: Boolean,
  btn_size: {
    type: [String, Number],
    default: 'small',
  },
  icon_size: {
    type: String,
    default: 'default',
  },
  vertical_actions: Boolean,
})

const emits = defineEmits(['accept-record', 'discard-record'])

</script>

<template>
  <div
    class="d-flex ga-1"
    :class="{'flex-column': vertical_actions}"
  >
    <v-chip
      v-if="discarded"
      class="mt-1"
      color="red lighten-4"
      variant="outlined"
    >
      Descartado
    </v-chip>
    <v-btn
      color="success"
      icon
      variant="outlined"
      :size="btn_size"
      v-tooltip="'Aceptar y guardar'"
      :disabled="!can_edit_pre_save"
      @click="emits('accept-record')"
    >
      <v-icon
        :size="icon_size"
      >
        done_outline
      </v-icon>
    </v-btn>
    <v-btn
      v-if="!discarded"
      color="error"
      icon
      variant="outlined"
      :size="btn_size"
      v-tooltip="'Descartar'"
      :disabled="!can_edit_pre_save"
      @click="emits('discard-record')"
    >
      <v-icon
        :size="icon_size"
      >
        close
      </v-icon>
    </v-btn>
  </div>
</template>