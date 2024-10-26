<script setup>
import {computed} from "vue";

const props = defineProps({
  main: Object,
  group: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
  name_field: {
    type: String,
    default: 'name',
  },
})

const title_width = computed(() => {
  // return props.group.key === 'project' ? 300 : 350
  return ['project', 'note'].includes(props.group.key) ? 300 : 350
})
const title_text = computed(() => {
  // console.log('props.main', props.main)
  // console.log('props.name_field', props.name_field)
  return props.main[props.name_field] || 'Título genérico'
})

const background_color = computed(() => {
  const base_color = props.group.color ||
      (props.group.parent ? props.group.parent.color : 'grey')
  return `${base_color}-lighten-5`
})

const emit = defineEmits(['open-panel'])

</script>

<template>
  <v-expansion-panel-title
    :color="background_color"
    class="pl-0 py-0"
    @click="emit('open-panel')"
    height="60"
    style="min-height: 60px;"
  >
    <slot name="icon">
      <v-icon
        :color="main.color || props.group.color || 'black'"
      >
        {{ main.icon || props.group.icon }}
      </v-icon>
    </slot>
    <v-toolbar-title
      class="text-subtitle-1 mr-4"
      :style="`max-width: ${title_width + 10}px;`"
    >
      <slot name="title" class="d-flex">
        <div class="d-flex align-center">
          <div
            class="ml-2"
            style="text-wrap: pretty; max-height: 54px; overflow: hidden;"
            :style="`width: ${title_width}px;`"
            v-tooltip:bottom="title_text"
          >{{ title_text }}</div>
          <v-icon
            v-if="main.description"
            color="grey-darken-1"
          >
            subject
          </v-icon>
          <v-tooltip
            activator="parent"
            location="end"
          >
            {{ main.description }}
          </v-tooltip>

        </div>
      </slot>
    </v-toolbar-title>
    <slot v-if="show_details" name="details">
      ---
    </slot>
    <v-btn
      v-else
      color="blue"
      variant="plain"
    >
      Cargando detalles...
    </v-btn>

<!--      <v-spacer></v-spacer>-->
<!--      <v-icon-->
<!--        color="purple"-->
<!--        class="mr-2"-->
<!--      >-->
<!--        expand_more-->
<!--      </v-icon>-->
<!--    </v-toolbar>-->

  </v-expansion-panel-title>

</template>

<style scoped>

</style>