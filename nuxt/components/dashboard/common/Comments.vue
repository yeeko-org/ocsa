<script setup>
import dayjs from 'dayjs'
const props = defineProps({
  main: Object,
})
const want_edit_comment = ref(false)

function changeWantEdit(value) {
  want_edit_comment.value = value
}
// console.log('addComment')
// this.model_obj[this.field] = this.model_obj[this.field]
//   ? `${this.model_obj[this.field]}\n\n` : ''
// const today = dayjs().format('DD/MM/YYYY')
// console.log("today", today)
// console.log("final", `${today} - ${this.user.first_name}: `)
// this.model_obj[this.field] += `${today} - ${this.user.first_name}: `

function addComment() {
  console.log("addComment")
  props.main.comments = props.main.comments
    ? `${props.main.comments}\n\n` : ''
  const today = dayjs().format('DD/MM/YYYY')
  console.log("today", today)
  const user = "USUARIO"
  // console.log("final", `${today} - ${props.main.user.first_name}: `)
  props.main.comments += `${today} - ${user}: `

}
function saveNote() {
  console.log("save note")
}

</script>

<template>
  <v-card
    v-if="main.comments"
    type="info"
    variant="flat"
    color="yellow-accent-4"
    width="280"
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
      <v-textarea
        v-model="main.comments"
        variant="outlined"
        style="min-width: 500px;"
        label="Notas:"
        rows="3"
        auto-grow
        append-outer-icon="close"
        @click:append-outer="changeWantEdit(false)"
      ></v-textarea>
      <slot name="action">
        <v-card-actions>
          <v-btn
            @click="addComment"
            color="accent"
            class="ml-3"
            variant="outlined"
          >Agregar comentario</v-btn>
          <v-spacer></v-spacer>
          <v-btn
            @click="saveNote"
            color="accent"
            class="ml-3"
            variant="elevated"
          >Guardar</v-btn>
        </v-card-actions>
      </slot>
    </v-card>
  </v-dialog>

</template>

<style scoped>

</style>