<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import CategoryNotesDialog from "~/components/map/CategoryNotesDialog.vue";

const mainStore = useMainStore()
const { all_nodes } = storeToRefs(mainStore)

const props = defineProps({
  objects: {
    type: Array,
    required: true,
  },
  node_name: String,
  type_key: String,
  subtype_key: String,
  mentions: {
    type: Array,
    default: () => [],
  },
  current_project_id: Number,
  clickable: {
    type: Boolean,
    default: true,
  },
})

const dialog_open = ref(false)
const selected_group = ref(null)
const selected_type_elem = ref(null)

function openCategoryDialog(group, type_elem) {
  if (!props.clickable) return
  selected_group.value = group
  selected_type_elem.value = type_elem
  dialog_open.value = true
}

function calcFinalGroup(group, title='', extra_filter=null){
  // console.log("props.objects", props.objects)
  let final_types = []
  group.children.forEach(elem_type => {
    const filter_objects = props.objects.filter(object => {
      return object[props.type_key] === elem_type.data.id
        && (!extra_filter || object.purpose === extra_filter)
    })

    if (filter_objects.length > 0)
      final_types.push({...elem_type.data, filter_objects})
  })
  final_types.sort(
    (a, b) => b.filter_objects.length - a.filter_objects.length)

  if (final_types.length > 0){
    if (title === ''){
      title = props.node_name === 'impact_types'
        ? `Afectaciones ${group.data.name}es`
        : `${group.data.name}s`
    }
    return {
      ...group.data, final_types, title,
    }
  }
}

const hierarchical_objects = computed(() => {
  // console.log('props.full_main.impacts', props.full_main.impacts)
  // console.log('node_data', all_nodes.value[props.node_name])
  // console.log('impact_types', all_nodes.value.impact_types)
  // console.log('schemas', schemas.value)
  let groups = []
  all_nodes.value[props.node_name].children.forEach(group => {
    if (!group.children)
      return
    if (group.data.show_position){
      // console.log("all_nodes.value", all_nodes.value.purposes)
      all_nodes.value.purposes.children.forEach(purpose => {
        const title = `${group.data.name} para ${purpose.data.name}`
        const final_group = calcFinalGroup(group, title, purpose.data.id)
        if (final_group)
          groups.push(final_group)
      })
    }
    else{
      const final_group = calcFinalGroup(group)
      if (final_group)
        groups.push(final_group)
    }

  })
  // console.log('groups', groups)
  return groups
})

</script>

<template>
  <v-card
    v-for="group in hierarchical_objects"
    :key="group.id"
    class="mb-2 pb-1 px-2"
    variant="tonal"
    :color="group.color"
  >
    <div
      class="text-subtitle-1 mt-2 mb-1 font-weight-bold d-flex"
    >
      <v-icon
        :color="group.color"
        class="mr-1"
      >
        {{ group.icon }}
      </v-icon>
      {{group.title}}:
      <v-spacer></v-spacer>
      <v-sheet
        class="d-flex align-center"
        v-if="group.description"
      >
        <v-icon :color="group.color" class="ml-2">
          help_outline
        </v-icon>
        <v-tooltip
          activator="parent"
          location="bottom left"
          max-width="400"
          color="primary"
          class="py-3 px-2"
          :content-props="{ background: 'white' }"
        >
          <div class="font-weight-bold pt-3 pb-2">
            {{group.title}}:
          </div>
          <div class="text-subtitle-2 pb-3">
            {{ group.description }}
          </div>
        </v-tooltip>
      </v-sheet>
    </div>
    <v-card
      v-for="type_elem in group.final_types"
      :key="type_elem.id"
      class=" pl-2 pr-1 mb-1 py-1"
      variant="text"
      :ripple="clickable"
      :style="clickable ? 'cursor: pointer;' : ''"
      @click="openCategoryDialog(group, type_elem)"
    >

      <span class="text-subtitle-1 font-weight-medium text-black">
        {{type_elem.name}}
      </span>
      <span class="text-caption text-grey text-no-wrap">
        ({{type_elem.filter_objects.length}}
        nota{{ type_elem.filter_objects.length === 1 ? '' : 's' }})
      </span>
      <v-tooltip
        activator="parent"
        location="left"
        max-width="340"
      >
        <div>
          <b>{{type_elem.name}}:</b>
          {{ type_elem.description }}
        </div>
      </v-tooltip>
    </v-card>
  </v-card>
  
  <CategoryNotesDialog
    v-if="clickable"
    v-model="dialog_open"
    :type_elem="selected_type_elem"
    :group="selected_group"
    :filter_objects="selected_type_elem?.filter_objects || []"
    :mentions="mentions"
    :current_project_id="current_project_id"
  />
</template>

<style scoped>

</style>