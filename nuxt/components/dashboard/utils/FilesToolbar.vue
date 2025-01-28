<script setup>

import ToolbarCommon from "~/components/dashboard/generic/ToolbarCommon.vue";

import {useMainStore} from '~/store/index'
const mainStore = useMainStore()
const { saveFile } = mainStore

const props = defineProps({
  full_main: {
    type: Object,
    required: true,
  },
  main_collection_name: String,
  child_relation_name: {
    type: String,
    default: 'note_file',
  },
  second_level: Boolean,
})

// const ready_files = ref(0)
const pdf = ref()
const main_file = ref(null)
const saving = ref(false)
const show_img = ref(false)
const show_pdf = ref(false)

// const { pdf } = usePDF(/

function uploadFile(e){
  let files = e.target.files || e.dataTransfer.files;
  // console.log("files", files)
  const first_file = files[0]
  main_file.value = {file: first_file, url: URL.createObjectURL(first_file)}
  sendFile()
}

function sendFile(){
  let formData = new FormData();
  formData.append("file", main_file.value.file, main_file.value.file.name);
  const elem_id = props.full_main.id
  const params = [elem_id, formData, props.main_collection_name]
  saveFile(params).then(res=>{
    console.log("res", res);
    // ready_files.value += 1
    saving.value = false
    props.full_main.files.push(res)
    main_file.value = null
  })
}

function downloadFile(file){
  window.open(file, '_blank');
}

function trashFile(file){
  console.log("trashFile", file)
}

</script>

<template>
  <ToolbarCommon
    :main_object="full_main"
    :cols="12"
    filter_group_name="states"
    :main_collection_name="main_collection_name"
    :child_relation_name="child_relation_name"
    field="files"
    color="brown"
    forced_level="group"
    :second_level="second_level"
  >
    <template #main_buttons>
      <v-file-input
        label="Subir archivo"
        name="logo"
        variant="solo"
        rounded="lg"
        hide-details
        density="compact"
        class="normal-field mr-2"
        bg-color="success"
        :loading="saving"
        @change="uploadFile($event)"
        style="max-width: 200px;"
      ></v-file-input>
    </template>
    <template #rows_init="{item}">
      <div
        v-if="!second_level"
        class="d-flex align-start align-self-start"
      >
        <v-chip variant="outlined" color="grey" min-width="150" label>
          Archivo
        </v-chip>
      </div>
      <template v-if="item.file">
        <v-chip
          v-if="!show_img"
          large
          class="ml-6 px-6 my-1"
          color="accent lighten-1"
          close-icon="delete"
          text-color="red"
          @click="show_img = !show_img"
          @click:close="trashFile(item.file)"
          prepend-icon="picture_as_pdf"
        >
          <span class="white--text" v-if="item.url">
            {{item.name}}
          </span>
          <span class="white--text" v-else>
            {{item.file.name}}
          </span>
        </v-chip>
        <div
          v-else
          class="resizable-container ml-6 my-1"
        >
          <embed
            v-if="item.file.includes('.pdf')"
            type="application/pdf"
            :src="item.file"
            class="_ml-6 _my-1 resizable-pdf"
          />
          <v-img
            v-else
            :src="item.file"
            class="resizable-content"
          ></v-img>
        </div>
      </template>
      <v-btn
        v-if="false"
        @click="loadPDF"
        variant="text"
        color="accent"
      >Ampliar</v-btn>
    </template>
  </ToolbarCommon>
</template>

<style scoped>
.resizable-container{
  border: 1px solid black;
  width: 640px;
  height: 440px;
  overflow: auto;
  resize: both;
  max-width: 1020px;
}
.resizable-content{
  object-fit: contain;
}
.resizable-pdf{
  width: 100%;
  height: 98%;
}
</style>