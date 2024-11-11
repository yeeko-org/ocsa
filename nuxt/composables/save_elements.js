import {useMainStore} from "~/store/index.js";

function final_snake_name(collection_data) {
  let snake_name = collection_data.snake_name
  const level = collection_data.level
  if (level.includes('category'))
    snake_name = `catalogs/${snake_name}`
  return snake_name
}

export async function saveElement(collection_data, element) {
  const mainStore = useMainStore()
  const { saveSimple } = mainStore
  const snake_name = final_snake_name(collection_data)
  // console.log("save_element", snake_name, element)
  return await saveSimple([snake_name, element]).then((response) => {
    // console.log("response", response)
    return response
  })
}

export async function getElement(collection_data, el_id) {
  const mainStore = useMainStore()
  const { getSimple } = mainStore
  const snake_name = final_snake_name(collection_data)
  // console.log("save_element", snake_name, element)
  return await getSimple([snake_name, el_id]).then((response) => {
    return response
  })
}
