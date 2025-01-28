import { useMainStore } from '~/store'

export function positionCounter(participants) {
  const mainStore = useMainStore()
  const { cats, positions } = mainStore
  const participant_types = cats.participant_type
  let new_positions = Object.entries(positions).reduce((acc, [key, position]) => {
    acc[key] = {...position, count: 0, projects: {}, key: key}
    return acc
  }, {})
  const position_counts = participants.reduce((acc, participant) => {
    const part_types = participant_types.filter(
      part_type => participant.participant_types.includes(part_type.id))
    const elem_id = participant.project.id
    part_types.forEach(part_type => {
      const position = part_type.position
      acc[position].projects[elem_id] = participant.project.name
    })
    return acc
  }, new_positions)
  let positions_list = Object.values(position_counts).map(position => {
    const projects = Object.values(position.projects)
    position.count = projects.length
    return position
  })
  return positions_list.filter(position => position.count > 0)
}
