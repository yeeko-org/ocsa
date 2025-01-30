<script setup>
import dayjs from 'dayjs'

const props = defineProps({
  main: Object,
  final_collection_data: Object,
  collection_name: String,
  width: {
    type: Number,
    default: 280,
  },
})

const want_edit_comment = ref(false)
import {useAuthStore} from '~/store/auth.js'
import {useMainStore} from '~/store/index.js'
const mainStore = useMainStore()
const authStore = useAuthStore()
const { user_details_ocsa } = authStore

function changeWantEdit(value) {
  want_edit_comment.value = value
}

function addComment() {
  console.log("addComment")
  props.main.comments = props.main.comments
    ? `${props.main.comments}\n\n` : ''
  const today = dayjs().format('DD/MM/YYYY')
  const user = user_details_ocsa.first_name
  props.main.comments += `${today} - ${user}: `

}
function saveComment() {
  if (props.main.id){
    const params = {comments: props.main.comments}
    const collection = props.final_collection_data
      ? props.final_collection_data.snake_name
      : props.collection_name
    // const collection = props.final_collection_data.snake_name
    mainStore.patchSimple([collection, props.main.id, params]).then(() => {
      want_edit_comment.value = false
    })
  }
  else
    want_edit_comment.value = false
}

</script>

<template>
  <v-card
    v-if="main.comments"
    type="info"
    variant="flat"
    color="yellow-accent-4"
    :width="width"
    max-height="62"
    class="d-flex ml-3 border-lg"
  >
    <v-icon class="ml-2 align-self-center" color="yellow-darken-3">
      sticky_note_2
    </v-icon>

    <v-card-text
      class="px-2 py-1"
      style="text-wrap: pretty; overflow: hidden;"
      v-html="main.comments"
    >
    </v-card-text>
    <v-btn
      icon
      class="mr-2 align-self-center"
      variant="tonal"
      size="small"
      @click="changeWantEdit(true)"
    >

      <v-icon>
        edit
      </v-icon>
    </v-btn>
    <v-tooltip
      activator="parent"
      top
      content-class="pa-0"
    >
      <v-card
        color="yellow-accent-4"
        class="pa-2 ma-0"
        width="560"
        style="white-space: pre-line;"
        v-html="main.comments"
      >
      </v-card>
    </v-tooltip>
  </v-card>
  <v-btn
    v-else
    class="ml-3"
    color="yellow-accent-4"
    variant="elevated"
    size="small"
    @click="changeWantEdit(true)"
    prepend-icon="sticky_note_2"
  >
    Comentar
  </v-btn>
  <v-dialog
    v-model="want_edit_comment"
    max-width="600"
    scrollable
  >
    <v-card class="d-flex flex-column pa-3">
      <v-card-text>
        <v-textarea
          v-model="main.comments"
          variant="outlined"
          style="min-width: 500px;"
          label="Notas:"
          rows="3"
          auto-grow
          append-outer-icon="close"
          hide-details
          @click:append-outer="changeWantEdit(false)"
        ></v-textarea>
      </v-card-text>
      <slot name="action">
        <v-card-actions>
          <v-btn
            @click="addComment"
            color="accent"
            _class="ml-3"
            variant="outlined"
          >Agregar comentario</v-btn>
          <v-spacer></v-spacer>
          <v-btn
            @click="saveComment"
            color="accent"
            _class="ml-3"
            variant="elevated"
          >Guardar</v-btn>
        </v-card-actions>
      </slot>
    </v-card>
  </v-dialog>

</template>

<style scoped>

</style>