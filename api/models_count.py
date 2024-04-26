from django.apps import apps


def models_count():

    all_models = apps.get_models()

    print()
    print("---Model counts:---")
    for model in all_models:
        model_name = model._meta.db_table
        count = model.objects.count()
        print(f"{model_name}: {count}")
    print("---End of model counts---")
    print()


def models_count_data():
    all_models = apps.get_models()
    data = {}
    for model in all_models:
        model_name = model._meta.db_table
        count = model.objects.count()
        data[model_name] = count
    return data


def models_print_first():
    all_models = apps.get_models()
    data = []
    errors = []
    for model in all_models:
        try:
            first_model = model.objects.first()
            model_name = model._meta.db_table
            print(first_model)
            first_model_name = str(first_model) if first_model else None
            print(f"First model of {model_name}: {first_model_name}")
        except Exception as e:
            errors.append(e)
    print("----------------------------Errors----------------------------")
    for error in errors:
        print(error)
