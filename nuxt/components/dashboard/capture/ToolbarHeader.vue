<script setup>

import QuestionMark from "~/components/dashboard/common/utils/QuestionMark.vue";
import AlertInfo from "~/components/dashboard/common/utils/AlertInfo.vue";

const props = defineProps({
  child_collection: Object,
  filter_group: Object,
  parent_object: {
    type: Object,
    default: () => {},
  },
  total_count: Number,
  parent_id: [Number, String],
  second_level: {
    type: Boolean,
    default: false,
  },
  disabled_buttons: {
    type: Boolean,
    default: false,
  },
  emit_add: Boolean,
});

const emits = defineEmits(['add-item', 'unshift-item'])

const addItem = (group=null) => {
  if (props.emit_add){
    emits('add-item', group)
    return
  }
  let new_child = {...props.parent_object}
  if (group){
    const f_group = filter_group.value
    new_child[f_group.category_group || f_group.special_group] = group.id
  }
  const fields = child_collection.value?.fields || []
  fields.forEach(field => {
    if (field.relation_type === 'one_to_many')
      return
    if (['id', props.main_collection_name].includes(field.name))
      return
    if (field.relation_type === 'many_to_many')
      new_child[field.name] = []
    else
      new_child[field.name] = null
  })
  if (props.additional_fields){
    new_child = {...new_child, ...props.additional_fields}
  }
  emits('unshift-item', new_child)
}

</script>

<template>
  <v-toolbar
    :height="second_level ? 32 : 46"
  >
    <v-toolbar-title
      :class="second_level ? '' : 'text-h6'"
    >
      {{ child_collection.plural_name }} ({{ total_count }})
    </v-toolbar-title>
    <QuestionMark
      :size="second_level ? 'small' : 'default'"
      :collection_data="child_collection"
    />
    <slot name="main_buttons">
      <template v-if="filter_group.category_groups">
        <v-btn
          v-for="cat_group in filter_group.category_groups"
          :key="cat_group.name"
          class="ml-1 text-none"
          :color="cat_group.color"
          variant="flat"
          icon
          :size="second_level ? 'small' : 'default'"
          :disabled="disabled_buttons"
          @click="addItem(cat_group)"
        >
          <v-badge color="transparent" icon="add">
            <v-icon
              color="white"
              :icon="cat_group.icon"
            ></v-icon>
          </v-badge>
          <v-tooltip
            activator="parent"
            location="top"
          >
            Agregar {{ cat_group.name }}
          </v-tooltip>
        </v-btn>
      </template>
      <v-btn
        v-else
        class="mr-2 text-none"
        color="success"
        variant="flat"
        :size="second_level ? 'small' : 'default'"
        :disabled="disabled_buttons"
        @click="addItem()"
      >
        <v-icon>add</v-icon>
      </v-btn>
    </slot>
    <template #extension v-if="child_collection.help_text">
      <v-card
        class="ma-2"
        elevation="2"
        style="width: 100%;"
      >
        <AlertInfo :help_text="child_collection.help_text"/>
      </v-card>
    </template>

  </v-toolbar>

</template>

<style scoped>

</style>