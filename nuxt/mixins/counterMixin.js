
let counterMixin = {
  computed: {
    actor_by_position() {
      // console.log("date init", new Date().getMilliseconds())
      const participant_types = cats.value.participant_types
      let new_positions = Object.entries(positions.value).reduce((acc, [key, position]) => {
        acc[key] = {...position, count: 0, actors: {}, key: key}
        return acc
      }, {})
      const position_counts = props.project.mentions.reduce((acc, mention) => {
        mention.participants.forEach(participant => {
          const part_types = participant_types.filter(
            part_type => participant.participant_types.includes(part_type.id))
          const actor_id = participant.actor.id
          part_types.forEach(part_type => {
            const position = part_type.position
            acc[position].actors[actor_id] = participant.actor.name
          })
        })
        return acc
      }, new_positions)
      // console.log("position counts", position_counts)
      let positions_list = Object.values(position_counts).map(position => {
        const actors = Object.values(position.actors)
        position.count = actors.length
        // const actors_text = actors.join("<br>")
        return position
      })
      return positions_list.filter(position => position.count > 0)
    },
  }
}