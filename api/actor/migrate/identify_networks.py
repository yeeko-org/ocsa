from actor.models import Actor


class IdentifyNetworks:

    def __init__(self):
        self.ready_actors = set()
        self.network_seq = 0
        self.actors = Actor.objects.all()\
            .select_related("parent_actor")\
            .prefetch_related("children_actors")
        self.current_network = set()

    def __call__(self):
        for actor in self.actors:
            if actor.id in self.ready_actors:
                continue
            if not actor.parent_actor:
                continue
            self.identify_network(actor)
            self.finish_network()
            self.current_network = set()

    def identify_network(self, actor, only_children=False):
        if actor.id in self.current_network:
            return
        self.current_network.add(actor.id)
        if actor.parent_actor and not only_children:
            self.identify_network(actor.parent_actor)
        for parent in actor.others_parents.all():
            self.identify_network(parent)
        for child in actor.children_actors.all():
            self.identify_network(child, only_children=True)

    def finish_network(self):
        self.ready_actors.update(self.current_network)
        network_size = len(self.current_network)
        if network_size <= 2:
            return
        self.network_seq += 1
        Actor.objects\
            .filter(id__in=self.current_network)\
            .update(network_seq=self.network_seq)


def add_comment_to_only_related():
    actors = Actor.objects.filter(is_only_related=True)
    for actor in actors:
        actor.add_comment("YEEKO: Se creó solo por relación")
        actor.save()
