import {useMainStore} from "~/store/index.js";

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
  const { patchSimple } = mainStore
  // console.log("collection_data", collection_data)
  const { snake_name, is_category } = final_snake_name(collection_data)
  const path = is_category ? `catalogs/${snake_name}` : snake_name
  return await patchSimple([path, elem_id, params]).then((response) => {
    return response
  })
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
