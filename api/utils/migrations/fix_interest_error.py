

def main():
    from actor.models import Interest
    all_interests = Interest.objects\
        .filter(interest_type__isnull=False, interest_subtype__isnull=True)
    print(f"Found {all_interests.count()} interests with type but no subtype")
    for interest in all_interests:
        interest_type_id = interest.interest_type.id
        interest.interest_subtype_id = interest_type_id
        interest.save()

