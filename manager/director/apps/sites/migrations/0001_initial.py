# Generated by Django 5.1.3 on 2024-11-28 20:54

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseHost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=255)),
                ('port', models.PositiveIntegerField()),
                ('dbms', models.CharField(choices=[('postgres', 'PostgreSQL'), ('mysql', 'MySQL')], max_length=16)),
                ('admin_hostname', models.CharField(blank=True, default='', max_length=255)),
                ('admin_port', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('admin_username', models.CharField(max_length=255)),
                ('admin_password', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DockerOS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('ubuntu', 'Ubuntu'), ('alpine', 'Alpine'), ('debian', 'Debian')], help_text='The name of the OS, in all ascii lowercase.', max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'Docker OS',
                'verbose_name_plural': "Docker OS's",
            },
        ),
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=255)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sites.databasehost')),
            ],
        ),
        migrations.CreateModel(
            name='DockerImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('tag', models.CharField(help_text="For parent images, this should always be a tag of the form 'alpine:3.20'.", max_length=255, unique=True, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+(\\/[a-zA-Z0-9]+)?:[a-zA-Z0-9._-]+$')])),
                ('logo', models.ImageField(blank=True, upload_to='docker_image_logos')),
                ('description', models.TextField(blank=True)),
                ('language', models.CharField(blank=True, choices=[('', 'No language'), ('python', 'Python'), ('node', 'Node.js'), ('php', 'PHP')], help_text='The programming language of the image. Do not include the version.', max_length=30)),
                ('operating_system', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='docker_os_set', to='sites.dockeros')),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.RegexValidator(message='Site names must consist of lowercase letters, numbers, and dashes. Dashes must go between two non-dash characters.', regex='^[a-z0-9]+(-[a-z0-9]+)*$')])),
                ('description', models.TextField(blank=True)),
                ('mode', models.CharField(choices=[('S', 'Static'), ('D', 'Dynamic')], max_length=1)),
                ('purpose', models.CharField(choices=[('legacy', 'Legacy'), ('user', 'User'), ('project', 'Project'), ('activity', 'Activity'), ('other', 'Other')], help_text='What the site was created for.', max_length=10)),
                ('availability', models.CharField(choices=[('enabled', 'Enabled (fully functional)'), ('not-served', 'Not served publicly'), ('disabled', 'Disabled (not served, only viewable/editable by admins)')], default='enabled', help_text='Controls who can access the site', max_length=20)),
                ('database', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='site', to='sites.database')),
                ('users', models.ManyToManyField(blank=True, related_name='site_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=255, validators=[django.core.validators.RegexValidator(message='Invalid domain. (Note: You can only have one sites.tjhsst.edu domain, and it must match the name of your site.)', regex='^(?!(.*\\.)?sites\\.tjhsst\\.edu$)[a-z0-9]+(-[a-z0-9]+)*(\\.[a-z0-9]+(-[a-z0-9]+)*)+$$')])),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('deleted', 'Deleted'), ('blocked', 'Blocked')], default='active', max_length=8)),
                ('creating_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('site', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='sites.site')),
            ],
        ),
        migrations.CreateModel(
            name='DockerAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('command', models.TextField()),
                ('allows_arguments', models.BooleanField(default=False, help_text='Does the command expect arguments?')),
                ('version', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('operating_systems', models.ManyToManyField(help_text='The operating systems this action can be run on. Mostly used for filtering.', related_name='docker_action_set', to='sites.dockeros')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('name', 'version'), name='unique_action_version')],
            },
        ),
    ]
