from django.apps import apps
from django.db import transaction
from django.db.models.deletion import Collector
from django.db import router


class RecordMerger:
    def __init__(self, model_name: str):

        self.model_class = self.get_model_class(model_name)
        if not self.model_class:
            raise ValueError(
                f"No se pudo encontrar el modelo con el nombre '{model_name}'")
        self.errors = []

    def get_model_class(self, model_name: str):

        if "." in model_name:
            app_label, model_name = model_name.split(".")
            try:
                return apps.get_model(app_label, model_name)
            except LookupError:
                raise ValueError(
                    f"No se encontró el modelo '{model_name}' en la "
                    f"aplicación '{app_label}'.")
        else:
            model_name = model_name.lower()
            found_models = []

            for app_config in apps.get_app_configs():
                for model in app_config.get_models():
                    if model.__name__.lower() == model_name:
                        found_models.append(model)

            if len(found_models) == 0:
                raise ValueError(
                    "No se encontró ningún modelo con el nombre "
                    f"'{model_name}'.")
            elif len(found_models) > 1:
                raise ValueError(
                    "Se encontraron múltiples modelos con el nombre "
                    f"'{model_name}'. Por favor, utiliza el formato "
                    "'app_label.ModelName'. Modelos encontrados: "
                    f"{[model._meta.label for model in found_models]}"
                )
            return found_models[0]

    @transaction.atomic
    def merge_registers(
            self, main_id: int, merge_id: int, delete_merge=True,
            just_report=False
    ):

        self.errors = []
        self.report = []
        self.deleted_report = {}

        if not self.model_class:
            self.errors.append("No se ha especificado una clase de modelo.")
            return

        try:
            main_instance = self.model_class.objects.get(id=main_id)
        except self.model_class.DoesNotExist:
            self.errors.append(
                f"No se encontró el registro principal con ID {main_id}.")
            return

        try:
            merge_instance = self.model_class.objects.get(id=merge_id)
        except self.model_class.DoesNotExist:
            self.errors.append(
                f"No se encontró el registro a fusionar con ID {merge_id}.")
            return

        related_objects = merge_instance._meta.related_objects
        self._generate_report(merge_instance, related_objects)
        if just_report:
            return

        for related in related_objects:
            try:
                if related.field.many_to_one or related.field.one_to_one:
                    self._merge_foreignkey_or_onetoone(
                        related, main_instance, merge_instance)
                elif related.field.many_to_many:
                    self._merge_many_to_many(
                        related, main_instance, merge_instance)
            except Exception as e:
                self.errors.append(
                    f"Error al procesar relación '{related.field.name}' "
                    f"del modelo '{related.related_model}': {e}"
                )
        if delete_merge:
            try:
                self.delet_instance(merge_instance)
            except Exception as e:
                self.errors.append(
                    f"Error al eliminar el registro con ID {merge_id}: {e}")

    def _merge_foreignkey_or_onetoone(
            self, related, main_instance, merge_instance
    ):

        related_manager = getattr(merge_instance, related.get_accessor_name())
        field_name = related.field.name

        if related.one_to_one:
            try:
                obj = related_manager
                setattr(obj, field_name, main_instance)
                obj.save()
            except related.related_model.DoesNotExist:
                pass
        else:
            related_manager.update(**{field_name: main_instance})

    def _merge_many_to_many(self, related, main_instance, merge_instance):

        related_manager = getattr(merge_instance, related.field.name)
        field_name = related.field.name

        for obj in related_manager.all():
            getattr(main_instance, field_name).add(obj)

        related_manager.clear()

    def _generate_report(self, merge_instance, related_objects):

        for related in related_objects:
            try:
                related_name = related.get_accessor_name()
                if related.field.many_to_one or related.field.one_to_one:
                    related_manager = getattr(merge_instance, related_name)
                    related_items = list(related_manager.all()) if not related.one_to_one else [
                        related_manager]
                    related_ids = [item.id for item in related_items if item]
                    related_count = len(related_items)
                    self.report.append({
                        "relation_type": "ForeignKey" if not related.one_to_one else "OneToOne",
                        "related_model": related.related_model.__name__,
                        "related_model_app": related.related_model._meta.app_label,
                        "affected_records": related_count,
                        "affected_ids": related_ids,
                        "field": related.field.name,
                    })
                elif related.field.many_to_many:
                    related_manager = getattr(
                        merge_instance, related.field.name)
                    related_items = related_manager.all()
                    related_ids = [item.id for item in related_items]
                    related_count = related_items.count()
                    self.report.append({
                        "relation_type": "ManyToMany",
                        "related_model": related.related_model.__name__,
                        "related_model_app": related.related_model._meta.app_label,
                        "affected_records": related_count,
                        "affected_ids": related_ids,
                        "field": related.field.name,
                    })
            except Exception as e:
                self.errors.append(
                    f"Error al generar informe para la relación '{related.field.name}' {related.__dict__}: {e}")

    def delet_instance(self, merge_instance):
        using = router.db_for_write(merge_instance.__class__)
        collector = Collector(using=using)
        collector.collect([merge_instance])
        self.deleted_report = {}
        for model, instances in collector.data.items():  # type:ignore
            self.deleted_report[model.__name__] = [obj.pk for obj in instances]

        with transaction.atomic():
            merge_instance.delete()
