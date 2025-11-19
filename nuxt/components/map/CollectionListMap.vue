<script setup>

import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
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
})

function calcFinalGroup(group, title='', extra_filter=null){
  // console.log("props.objects", props.objects)
  let final_types = []
  group.children.forEach(elem_type => {
    const filter_objects = props.objects.filter(object => {
      return object[props.type_key] === elem_type.data.id
        && (!extra_filter || object.purpose === extra_filter)
    })
    const descriptions = filter_objects.reduce((acc, object) => {
      const key = object.description || "Sin descripción"
      acc[key] = (acc[key] || 0) + 1
      return acc
    }, {})
    const list_descriptions = Object.entries(descriptions)
      .map(([description, count]) => ({description, count}))
      .sort((a, b) => b.count - a.count)

    if (filter_objects.length > 0)
      final_types.push({
        ...elem_type.data, filter_objects, descriptions: list_descriptions
      })
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
      class=" pl-2 mb-1 py-1"
      variant="text"
    >

      <span class="text-subtitle-1 font-weight-medium text-black">
        {{type_elem.name}}
      </span>
      <span class="ml-1 text-caption text-grey">
        ({{type_elem.filter_objects.length}} notas)
      </span>
      <v-tooltip
        activator="parent"
        location="left"
        max-width="340"
      >
        <div class="mb-2">
          <b>{{type_elem.name}}:</b>
          {{ type_elem.description }}

        </div>
        <div
          v-for="description in type_elem.descriptions"
          :key="description.description"
          class="mb-1"
        >
          <span class="font-weight-bold mr-2">
            {{description.count}}
          </span>
          <span>
            {{description.description}}
          </span>
        </div>
      </v-tooltip>
    </v-card>
<!--    <v-expansion-panels elevation="0">-->
<!--      <v-expansion-panel-->
<!--        v-for="type_elem in group.final_types"-->
<!--        :key="type_elem.id"-->
<!--        xclass="mb-1"-->
<!--        :color="`${group.color}-lighten-4`"-->
<!--      >-->
<!--        <v-expansion-panel-title-->
<!--          class="pl-2 py-0"-->
<!--          height="40"-->
<!--          min-height="40"-->
<!--        >-->
<!--          <span class="text-subtitle-1 font-weight-medium text-black">-->
<!--            {{type_elem.name}}-->
<!--          </span>-->
<!--          <span class="ml-1 text-caption text-grey">-->
<!--            ({{type_elem.filter_objects.length}} notas)-->
<!--          </span>-->
<!--          <v-tooltip-->
<!--            activator="parent"-->
<!--            location="left"-->
<!--            max-width="340"-->
<!--          >-->
<!--            <div class="mb-2">-->
<!--              <b>{{type_elem.name}}:</b>-->
<!--              {{ type_elem.description }}-->

<!--            </div>-->
<!--            <div-->
<!--              v-for="description in type_elem.descriptions"-->
<!--              :key="description.description"-->
<!--              class="mb-1"-->
<!--            >-->
<!--              <span class="font-weight-bold mr-2">-->
<!--                {{description.count}}-->
<!--              </span>-->
<!--              <span>-->
<!--                {{description.description}}-->
<!--              </span>-->
<!--            </div>-->
<!--          </v-tooltip>-->
<!--        </v-expansion-panel-title>-->
<!--        <v-expansion-panel-text-->
<!--          class="pa-0"-->
<!--        >-->
<!--          <v-card color="transparent" variant="text" class="text-green">-->

<!--            Hola descripciones-->
<!--          </v-card>-->
<!--        </v-expansion-panel-text>-->
<!--      </v-expansion-panel>-->
<!--    </v-expansion-panels>-->
  </v-card>
</template>

<style scoped>

</style>