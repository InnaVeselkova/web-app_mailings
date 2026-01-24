from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Создать группу модератора"

    def handle(self, *args, **kwargs):
        group_name = "модератор"
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Группа '{group_name}' успешно создана."))
        else:
            self.stdout.write(f"Группа '{group_name}' уже существует.")
