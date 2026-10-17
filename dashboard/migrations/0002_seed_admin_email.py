from django.db import migrations


def seed_admin_email(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    # Update superusers to emondeveloper@gmail.com if not already set or default
    superusers = User.objects.filter(is_superuser=True)
    for u in superusers:
        if not u.email or u.email in ('admin@gadgetdeluxe.shop', 'admin@example.com'):
            u.email = 'emondeveloper@gmail.com'
            u.save(update_fields=['email'])

    # Also update 'admin' user specifically
    admin_user = User.objects.filter(username='admin').first()
    if admin_user and admin_user.email != 'emondeveloper@gmail.com':
        admin_user.email = 'emondeveloper@gmail.com'
        admin_user.save(update_fields=['email'])


def reverse_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_admin_email, reverse_func),
    ]
