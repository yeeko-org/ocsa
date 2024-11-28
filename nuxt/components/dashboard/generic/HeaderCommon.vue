<script setup>
import {computed, nextTick, watch} from "vue";
import StatusChip from "~/components/dashboard/status/StatusChip.vue";
import CommentIcon from "~/components/dashboard/common/CommentIcon.vue";

const props = defineProps({
  main: Object,
  collection_data: Object,
  show_details: {
    type: Boolean,
    default: false,
  },
})
const expansionHeader = ref(null);
const is_active = ref(false)
const real_show_details = ref(false)

const title_width = computed(() => {
  // return props.group.key === 'project' ? 300 : 350
  return ['project', 'note'].includes(props.collection_data.name) ? 300 : 350
})
const title_text = computed(() => {
  const name_field = props.collection_data.name_field
  return props.main[name_field] || 'Título genérico'
})

const background_color = computed(() => {
  // console.log("main", props.main)
  // console.log("collection", props.collection_data)
  const base_color = props.collection_data.color || 'blue-grey'
  return `${base_color}-lighten-5`
})

onMounted(() => {
  changeShowDetails()
})

watch(
  props.collection_data, (newVal) => {
    // real_show_details.value = true
    changeShowDetails()
  }, {immediate: true}
)

function changeShowDetails(){
  nextTick(() => {
    setTimeout(() => {
      real_show_details.value = true
    }, 1)
  })
}

function wantOpenPanel(){
  if (!is_active.value)
    emits('open-panel')
  is_active.value = !is_active.value
}

const emits = defineEmits(['open-panel'])

</script>

<template>
  <v-expansion-panel-title
    id="expansion-header"
    ref="expansionHeader"
    :color="background_color"
    class="pl-0 py-0"
    height="60"
    style="min-height: 60px;"
    @click="wantOpenPanel"
  >
<!--    v-slot="{ expanded }"-->
    <slot name="icon">
      <v-icon
        v-if="main.icon || props.collection_data.icon"
        :color="main.color || props.collection_data.color || 'black'"
      >
        {{ main.icon || props.collection_data.icon }}
      </v-icon>
    </slot>
    <v-toolbar-title
      class="text-subtitle-1 mr-4"
      :style="`max-width: ${title_width + 10}px;`"
    >

      <div class="d-flex align-center">
        <slot name="title" class="d-flex">
          <div
            class="ml-2"
            style="text-wrap: pretty; max-height: 54px; overflow: hidden;"
            :style="`width: ${title_width}px;`"
            v-tooltip:bottom="title_text"
          >{{ title_text }}</div>
        </slot>
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
    </v-toolbar-title>
    <template v-if="real_show_details">
      <template v-if="collection_data.status_groups">
        <StatusChip
          v-for="status_group in collection_data.status_groups"
          :main="main"
          :collection="status_group"
          small
          class="ml-1"
          :bold_text="false"
        />
      </template>
      <CommentIcon
        v-if="main.comments"
        :main="main"
        class="ml-1"
      />
      <slot  name="details">
        ----
      </slot>
    </template>
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