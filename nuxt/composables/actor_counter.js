import { useMainStore } from '~/store'

export function actorCounter(participants, field='actor_full', subfield='name') {
  const mainStore = useMainStore()
  const { cats, positions } = mainStore
  const participant_types = cats.participant_type
  let new_positions = Object.entries(positions).reduce((acc, [key, position]) => {
    acc[key] = {...position, count: 0, elements: {}, key: key}
    return acc
  }, {})
  const position_counts = participants.reduce((acc, participant) => {
    const part_types = participant_types.filter(
      part_type => participant.participant_types.includes(part_type.id))
    const elem_id = participant[field].id
    part_types.forEach(part_type => {
      const position = part_type.position
      acc[position].elements[elem_id] = participant[field][subfield]
    })
    return acc
  }, new_positions)
  let positions_list = Object.values(position_counts).map(position => {
    const elements = Object.values(position.elements)
    position.count = elements.length
    return position
  })
  return positions_list.filter(position => position.count > 0)
}
