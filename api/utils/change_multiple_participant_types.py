def clean_participant_types():
    from actor.models import Participant
    all_participants = Participant.objects.all()
    combinations = {}
    print(f"Cleaning {all_participants.count()} participants")
    for participant in all_participants:
        # print(participant.participant_types.all().count())
        # break
        count = participant.participant_types.all().count()
        if count > 1:
            cleaned = False
            print(f"\nMany participan_types: {participant.actor}")
            note = participant.mention.note
            print(f"Nota {note.id}: {note}")
            all_participant_types = participant.participant_types.all()
            for participant_type in all_participant_types:
                print(participant_type)
            together = tuple(all_participant_types)
            for participant_type in all_participant_types:
                if 'reclassify' in participant_type.status_validation_id:
                    participant.participant_types.remove(participant_type)
                    cleaned = True
                    break
            # print()
            if not cleaned:
                combinations.setdefault(together, 0)
                combinations[together] += 1
            # status_validation_id
    print("*" * 40)
    for combination, count in combinations.items():
        print("combination:", combination, count)
