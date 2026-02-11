import { useMainStore } from '~/store'

export function actorCounter(participants, field='actor_full', subfield='name') {
  const mainStore = useMainStore()
  const { cats } = mainStore
  const participant_types = cats.participant_type
  let participant_group_dict = cats.participant_group.reduce((acc, pg) => {
    const key = pg.id
    acc[key] = {...pg, count: 0, elements: {}, key: key}
    return acc
  }, {})
  // console.log('new_positions', new_positions)
  const position_counts = participants.reduce((acc, participant) => {
    const part_types = participant_types.filter(
      part_type => participant.participant_types.includes(part_type.id))
    const elem_id = participant[field].id
    part_types.forEach(part_type => {
      const participant_group = part_type.participant_group
      acc[participant_group].elements[elem_id] = participant[field][subfield]
    })
    return acc
  }, participant_group_dict)
  let positions_list = Object.values(position_counts).map(position => {
    const elements = Object.values(position.elements)
    position.count = elements.length
    return position
  })
  return positions_list.filter(position => position.count > 0)
}
