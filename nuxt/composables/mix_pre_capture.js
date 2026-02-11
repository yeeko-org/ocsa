import {useMainStore} from "~/store/index.js";

const init_fields = {
  1: [ "participants", "events", "impacts", "status_history" ],
  2: [ "locations", "involvements", "interests" ]
}

const full_fields = ['project_full', 'actor_full']

export function mixOrigins(saved_mention, pre_mention, level=1) {
  let mixed_mention = {
    ...saved_mention,
    pre_data: pre_mention,
    path: pre_mention.path,
    paragraphs: pre_mention.paragraphs
  }
  full_fields.forEach(field => {
    if (saved_mention[field]){
      mixed_mention[field] = mixOrigins(
        saved_mention[field],
        pre_mention[field] || {},
        level + 1
      )
    }
  })
  const list_fields = init_fields[level] || []
  list_fields.forEach(field => {
    const saved_data = saved_mention[field]
    const pre_data = pre_mention[field] || []
    if (!saved_data)
      return
    mixed_mention[field] = orderMix(saved_data, pre_data, level + 1)
  })
  return mixed_mention
}

export function orderMix(saved_data, pre_data, level=1) {
  let mixed_data = []
  let discarded_data = []
  let used_ids = new Set()
  pre_data.forEach(pre_item => {
    if (pre_item.discarded === false){
      const saved_item = saved_data.find(
        sd => sd.id === pre_item.element_id)
      if (saved_item){
        used_ids.add(saved_item.id)
        const mixed_item = mixOrigins(saved_item, pre_item, level)
        mixed_data.push(mixed_item)
      }
      else
        mixed_data.push(pre_item)
    }
    else if (pre_item.discarded === true){
      discarded_data.push(pre_item)
    }
    else if (pre_item.discarded === null)
      mixed_data.push(pre_item)
  })
  saved_data.forEach(item => {
    if (!used_ids.has(item.id)) {
      mixed_data.push(item)
    }
  })
  mixed_data = mixed_data.concat(discarded_data)
  return mixed_data
}

export async function savePreItem(path, collection_name, note_id, params) {
  const mainStore = useMainStore()
  const { saveSimple, savePreCapture } = mainStore
  const is_mention = collection_name === 'mention'
  const saved_item = await saveSimple([collection_name, params])
  // console.log("savePreItem - saved_item", saved_item)
  const data = {
    path,
    element_id: saved_item.id,
    discarded: false,
  }
  const res_pre_item = await savePreCapture({data, note_id})
  const level = is_mention ? 1 : 2
  return mixOrigins(saved_item, res_pre_item.content, level)
}

export async function saveItemMixed(
  collection_name, params, pre_capture=null
) {
  const mainStore = useMainStore()
  const { saveSimple } = mainStore
  const saved_item = await saveSimple([collection_name, params])
  if (saved_item.errors)
    return saved_item
  if (!pre_capture)
    return saved_item

  const is_mention = collection_name === 'mention'
  let level = is_mention ? 1 : 2
  return mixOrigins(saved_item, pre_capture, level)
}

export async function discardPreItem(path, collection_name, note_id) {
  const mainStore = useMainStore()
  const { savePreCapture } = mainStore

  const data = {path, discarded: true}
  const res_pre_item = await savePreCapture({data, note_id})
  return res_pre_item.content
}

