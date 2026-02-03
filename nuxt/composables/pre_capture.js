
function hydratePreMention(mention) {
  mention.participants = mention.actors.map(actor=>{
    const {
      name, belongs, sector_text,
      interest_text, ...participant
    } = actor
    return {
      ...participant,
      actor_full : {
        name, belongs, sector_text,
        status_validation: 'yk_proposed'
      }
    }
  })
  return mention
}

const init_fields = {
  1: [ "participants", "events", "impacts", "status_history" ],
  2: [ "locations", "involvements", "interests" ]
}

export function mixOrigins(saved_mention, pre_mention, level=1) {
  let mixed_mention = { ...saved_mention }
  mixed_mention.pre_data = pre_mention
  const fields = init_fields[level] || []
  fields.forEach(field => {
    const saved_data = saved_mention[field]
    const pre_data = pre_mention[field] || []
    if (!saved_data)
      return
    mixed_mention[field] = orderMix(field, saved_data, pre_data, level + 1)
  })
  return mixed_mention
}

export function orderMix(field, saved_data, pre_data, level=1) {
  let want_print = false
  if (level === 1 && field === 'mentions'){
    want_print = true
  }
  let mixed_data = []
  let discarded_data = []
  let used_ids = new Set()
  pre_data.forEach(pre_item => {
    if (level === 1 && field === 'mentions'){
      pre_item = hydratePreMention(pre_item)
      console.log("orderMix mentions", pre_item)
      console.log("saved_data", saved_data)
    }
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
