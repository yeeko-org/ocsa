import {useMainStore} from "~/store/index.js";
import {storeToRefs} from "pinia";

function final_snake_name(collection_data) {
  const is_category = collection_data.is_category
  const snake_name = collection_data.snake_name
  return { snake_name, is_category }
}

export async function saveElement(collection_data, element) {
  const mainStore = useMainStore()
  const { saveSimple, saveCatalog } = mainStore
  // console.log("collection_data", collection_data)
  const { snake_name, is_category } = final_snake_name(collection_data)
  if (is_category)
    return await saveCatalog([collection_data, element]).then((response) => {
      return response
    })
  else
    return await saveSimple([snake_name, element]).then((response) => {
      return response
    })
}

export async function patchElement(collection_data, elem_id, params) {
  const mainStore = useMainStore()
  const { patchSimple, patchCatalog } = mainStore
  // console.log("collection_data", collection_data)
  const { snake_name, is_category } = final_snake_name(collection_data)
  // const path = is_category ? `catalogs/${snake_name}` : snake_name
  if (is_category) {
    return await patchCatalog([collection_data, elem_id, params]).then((response) => {
      return response
    })
  }
  else {
    return await patchSimple([snake_name, elem_id, params]).then((response) => {
      return response
    })
  }
}

export async function deleteElement(collection_data, obj_id) {
  const mainStore = useMainStore()
  const { deleteSimple, deleteCatalog } = mainStore
  const { snake_name, is_category } = final_snake_name(collection_data)
  if (is_category)
    return await deleteCatalog([collection_data, obj_id]).then((response) => {
      return response
    })
  else
    return await deleteSimple([snake_name, obj_id]).then((response) => {
      return response
    })
}

export async function getElement(collection_data, el_id) {
  const mainStore = useMainStore()
  const { getSimple } = mainStore
  // const snake_name = final_snake_name(collection_data)
  let { snake_name, is_category } = final_snake_name(collection_data)
  if (is_category)
    snake_name = `catalogs/${snake_name}`
  // console.log("save_element", snake_name, element)
  return await getSimple([snake_name, el_id]).then((response) => {
    return response
  })
}

export function useSaveElements() {
  const total_requests = ref(0)
  const resolved_requests = ref(0)
  const save_errors = ref([])
  const participants_dict = ref({})
  const normal_save = ref(true)

  function saveComplex(collection_name, element, copy_id=null) {
    normal_save.value = !copy_id

    return new Promise((resolve, reject) => {
      total_requests.value = 0
      resolved_requests.value = 0
      save_errors.value = []

      const checkFinished = () => {
        if (resolved_requests.value === total_requests.value) {
          // console.log("All requests finished", save_errors.value)
          if (save_errors.value.length > 0) {
            reject(save_errors.value)
          } else {
            resolve()
          }
        }
      }

      saveOneToMany(collection_name, element, checkFinished, copy_id)
    })
  }

  function saveOneToMany(snake_name, main_item, onFinished, parent_id=null) {
    const mainStore = useMainStore()
    const { schemas } = storeToRefs(mainStore)
    const { saveSimple } = mainStore

    const main_schema = schemas.value.collections_dict[snake_name]
    const one_to_many_fields = main_schema.fields.filter(
      field => field.relation_type === 'one_to_many')
    // console.log("one_to_many_fields", one_to_many_fields)

    one_to_many_fields.forEach(field => {
      if (['involved', "eventlocation", "clicks"].includes(field.name))
        return
      if (field.name.includes('displacement_'))
        return

      const related_collection = schemas.value.collections_dict[
        field.related_model]
      // if (!related_collection) {
      //   console.error('Related collection not found for field', field)
      //   // return
      // }
      const snake_name2 = related_collection.snake_name

      main_item[field.name].forEach(item => {
        const new_item = {...item}

        if (!normal_save.value) {
          new_item[snake_name] = parent_id
          new_item.id = null
          if (snake_name2 === 'involved')
            new_item['participant'] = participants_dict.value[item.participant]
        }

        total_requests.value += 2
        // console.log(`snake_name2', ${snake_name2}, 'new_item`, new_item)

        saveSimple([snake_name2, new_item]).then(res => {
          if (res.errors) {
            console.error(`Error saving ${snake_name2} item:`, res.errors)
            save_errors.value.push({
              field: field.name,
              item: new_item,
              errors: res.errors,
            })
          }
          if (!normal_save.value){
            if (snake_name2 === 'participant')
              participants_dict.value[item.id] = res.id
            saveOneToMany(snake_name2, new_item, onFinished, res.id)
          }
          resolved_requests.value += 1
          onFinished()
        })
        if (normal_save.value){
          saveOneToMany(snake_name2, item, onFinished)
        }
        resolved_requests.value += 1
        onFinished()
      })
    })

    if (total_requests.value === 0) {
      onFinished()
    }
  }

  return {
    saveComplex,
    save_errors
  }
}
