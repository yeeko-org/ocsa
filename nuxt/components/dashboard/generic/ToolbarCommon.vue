<script setup>
import { computed } from 'vue'
import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";
import SelectGroup from "~/components/dashboard/common/select/SelectGroup.vue";
import QuestionMark from "~/components/dashboard/generic/QuestionMark.vue";
import AlertInfo from "~/components/dashboard/common/AlertInfo.vue";

const props = defineProps({
  main_object: Object,  // Mention
  main_collection_name: String,  // Mention
  filter_group_name: String,  // event_types
  child_relation_name: String,  // event
  additional_fields: Object,
  required: Boolean,
  field: {
    type: String,
    required: true,
  }, // events
  forced_level: String,
  second_level: Boolean,
  two_columns: Boolean,
  emit_add: Boolean,
  cols: {
    type: Number,
    default: 12,
  },
  color: {
    type: String,
    default: 'indigo',
  },
})

const dialog_delete = ref(false)
const delete_text = ref('')
const record_to_delete = ref({})

const mainStore = useMainStore()
const { schemas } = storeToRefs(mainStore)
const { deleteSimple } = mainStore

const emits = defineEmits(['add-item'])

const filter_group = computed(() =>
  schemas.value.filter_groups.find(
    cat_group => cat_group.key_name === props.filter_group_name)
)

const main_collection = computed(() =>
  schemas.value.collections_dict[props.main_collection_name])

// Event Collection
const child_collection = computed(() =>
  schemas.value.collections_dict[props.child_relation_name])

const addItem = (group=null) => {
  // console.log("child_collection", child_collection.value)
  if (props.emit_add){
    emits('add-item')
    return
  }
  let new_child = {}
  if (group)
    new_child[filter_group.value.category_group] = group.id
  new_child[props.main_collection_name] = props.main_object.id
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
  // console.log("additional_fields", props.additional_fields)
  if (props.additional_fields){
    new_child = {...new_child, ...props.additional_fields}
    // props.additional_fields.forEach((field, idx) => {
    //   new_child[field] = []
    // })
  }
  // console.log("new_child", new_child)
  // props.collection[props.field].push(new_child)
  props.main_object[props.field].push(new_child)
}

const wantDeleteRecord = (item, index) => {
  const saved = item.id
  record_to_delete.value = { item, index, saved }
  dialog_delete.value = true
  // props.main_object[field.value].splice(index, 1)
}

const deleteRecord = () => {
  const {item, index, saved} = record_to_delete.value
  if (saved && delete_text.value !== 'eliminar')
    return
  // console.log("item", item)
  // console.log("index", index)
  if (item.id){
    deleteSimple([child_collection.value.snake_name, item.id])
      .then(() => {
        props.main_object[props.field].splice(index, 1)
      })
  }
  else
    props.main_object[props.field].splice(index, 1)
  dialog_delete.value = false
  record_to_delete.value = {}
  // props.main_object[props.field].splice(index, 1)
  // dialog_delete.value = false
}
const total_count = computed(() => {
  try {
    return props.main_object[props.field].length
  } catch (e) {
    console.log("error", e)
    console.log("main_object:", props.main_object)
    console.log("field:", props.field)
    return 0
  }

})

</script>


<template>
  <v-col :cols="cols" class="py-2 px-2">
    <v-card
      :class="second_level ? 'mt-2' : ''"
      elevation="4"
      variant="elevated"
      :color="`${color}-lighten-${second_level ? 4 : 3}`"
    >
      <v-toolbar
        :color="`${color}-lighten-${second_level ? 2 : 1}`"
        :height="second_level ? 32 : 46"
      >
        <v-toolbar-title
          style="min-width: 300px;"
          :class="second_level ? '' : 'text-h6'"
        >
          {{child_collection.plural_name}} ({{total_count}})
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
              @click="addItem(cat_group)"
              :size="second_level ? 'small' : 'default'"
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
                Agregar {{cat_group.name}}
              </v-tooltip>
            </v-btn>
          </template>
          <v-btn
            v-else
            class="mr-2 text-none"
            color="success"
            variant="flat"
            @click="addItem()"
            :size="second_level ? 'small' : 'default'"
          >
            <v-icon>add</v-icon>
          </v-btn>
        </slot>
      </v-toolbar>
      <v-card
        v-if="child_collection.help_text"
        class="ma-2"
        elevation="2"
      >
        <AlertInfo
          :help_text="child_collection.help_text"
        />
      </v-card>
      <v-card
        v-for="(item, index) in main_object[field]"
        :key="index"
        class="ma-2"
        elevation="2"
        variant="flat"
        :color="second_level ? 'white' : `${color}-lighten-5`"
      >
        <v-row
          no-gutters
          class="d-flex flex-wrap"
          _class="{'ml-6': second_level && !two_columns}"
        >
          <v-col
            :cols="two_columns ? 6 : 12"
            class="pa-2"
          >
            <div class="d-flex flex-wrap">
              <SelectGroup
                :filter_group_name="filter_group_name"
                :main_collection="child_collection"
                :main_object="item"
                is_toolbar
                :forced_level="forced_level"
                @delete-record="wantDeleteRecord(item, index)"
              >
                <template #chip>
                  <slot name="rows_init" :item="item">
                  </slot>
                </template>
              </SelectGroup>
            </div>
            <slot name="rows" :item="item">
            </slot>
          </v-col>
          <v-col
            v-if="two_columns"
            cols="6"
            class="my-0"
          >
            <slot name="second-column" :item="item">
            </slot>
          </v-col>
        </v-row>
      </v-card>
      <v-alert
        v-if="total_count === 0"
        :type="required ? 'error' : 'warning'"
        variant="flat"
      >
        {{ required ? 'Debes' : 'Intenta' }}
        agregar al menos un {{child_collection.name}}
        <v-btn
          v-if="!filter_group.category_groups && false"
          color="white"
          class="ml-2 my-n1"
          variant="tonal"
          @click="addItem()"
          icon="add"
          size="small"
        >
        </v-btn>
      </v-alert>
      <slot name="footer">
      </slot>
    </v-card>
    <v-dialog
      v-model="dialog_delete"
      max-width="500"
    >
      <v-card>
        <v-card-title>
          ¿Confirmas la eliminación de este registro?
        </v-card-title>
        <v-card-subtitle>
          Esta acción no se puede deshacer
        </v-card-subtitle>
        <v-card-text>
          <v-row>
            <v-col
              v-if="record_to_delete.saved"
              cols="12"
            >
              <v-text-field
                v-model="delete_text"
                label="Escribe 'eliminar' para confirmar"
                outlined
                dense
                clearable
              ></v-text-field>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="accent"
            variant="outlined"
            @click="dialog_delete = false"
          >
            Cancelar
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            color="error"
            variant="elevated"
            @click="deleteRecord"
          >
            Eliminar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-col>
</template>

<style scoped>

</style>