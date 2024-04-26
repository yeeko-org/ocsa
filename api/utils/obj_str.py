def nombre_or_pk(obj, pk, attr='nombre'):
    name = getattr(obj, attr, None) or pk
    return str(name)
