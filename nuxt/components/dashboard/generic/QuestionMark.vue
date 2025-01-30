<script setup>
import {useMainStore} from "~/store/index.js";
const mainStore = useMainStore()
// const { saveCollection } = mainStore

const props = defineProps({
  size: {
    type: String,
    default: "default",
  },
  collection_data: {
    type: Object,
    required: true,
  },
})

const dialog = ref(false)

function saveDefinition() {
  console.log('props.collection_data', props.collection_data)
  mainStore.saveCollection(props.collection_data).then((res) => {
    console.log('res', res)
    dialog.value = false
  })
}


</script>

<template>
  <v-btn
    class="hidden-xs-only px-0"
    icon
    :size="size"
    @click="dialog = true"
  >
    <v-icon>question_mark</v-icon>
    <v-tooltip
      activator="parent"
      location="end"
    >
      <div
        style="max-width: 600px; white-space: pre-line;"
        v-text="collection_data.description"
      >
      </div>
    </v-tooltip>
    <v-dialog
      v-model="dialog"
      max-width="1100"
    >
      <v-card>
        <v-card-title class="d-flex">
          <span class="">
            Acerca de {{collection_data.plural_name}}
          </span>
          <v-spacer></v-spacer>
          <v-btn
            icon
            variant="text"
            @click="dialog = false"
          >
            <v-icon>close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-textarea
            v-model="collection_data.description"
            label="Descripción"
            rows="4"
            auto-grow
          >
          </v-textarea>
          <v-code v-if="false">
            {{ collection_data }}
          </v-code>
          <v-textarea
            v-model="collection_data.help_text"
            label="Texto visible de ayuda"
            rows="4"
            auto-grow
            hint="Aparece siempre arriba de los elementos como 'alerta'"
            persistent-hint
          >
          </v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="accent"
            variant="elevated"
            @click="saveDefinition"
          >
            Guardar definición
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-btn>


</template>

<style scoped>

</style>