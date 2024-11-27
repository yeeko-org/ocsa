import {useMainStore} from "~/store/index.js";

function final_snake_name(collection_data) {
  let snake_name = collection_data.snake_name
  const level = collection_data.level
  const is_catalog = level.includes('category')
  // if (level.includes('category'))
  //   snake_name = `catalogs/${snake_name}`
  return { snake_name, is_catalog }
}

export async function saveElement(collection_data, element) {
  const mainStore = useMainStore()
  const { saveSimple, saveCatalog } = mainStore
  // const snake_name = final_snake_name(collection_data)
  const { snake_name, is_catalog } = final_snake_name(collection_data)
  // console.log("save_element", snake_name, element)
  if (is_catalog)
    return await saveCatalog([collection_data, element]).then((response) => {
      return response
    })
  else
    return await saveSimple([snake_name, element]).then((response) => {
      return response
    })
}

export async function getElement(collection_data, el_id) {
  const mainStore = useMainStore()
  const { getSimple } = mainStore
  // const snake_name = final_snake_name(collection_data)
  let { snake_name, is_catalog } = final_snake_name(collection_data)
  if (is_catalog)
    snake_name = `catalogs/${snake_name}`
  // console.log("save_element", snake_name, element)
  return await getSimple([snake_name, el_id]).then((response) => {
    return response
  })
}
