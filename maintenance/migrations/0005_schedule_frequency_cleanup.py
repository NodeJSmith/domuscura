import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0004_migrate_frequency_data'),
    ]

    operations = [
        # Make frequency non-nullable now that data migration has populated it
        migrations.AlterField(
            model_name='schedule',
            name='frequency',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='schedules',
                to='maintenance.frequency',
            ),
        ),
        # Drop the old denormalised columns
        migrations.RemoveField(
            model_name='schedule',
            name='frequency_days',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='frequency_label',
        ),
    ]
