import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Student', '0007_alter_student_options_student_student_id'),
        ('payments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='student',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='payments',
                to='Student.student'
            ),
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
            },
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='date_paid',
            new_name='created_at',
        ),
        migrations.AddField(
            model_name='payment',
            name='fee_type',
            field=models.CharField(
                choices=[('tuition', 'Tuition'), ('bus fee', 'Bus fee'), ('feeding fee', 'Feeding fee')],
                default='tuition',
                max_length=32
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='metadata',
            field=models.JSONField(
                blank=True,
                null=True,
                help_text='Raw response from payment gateway'
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='payer',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payments',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.PositiveIntegerField(
                help_text='Amount in kobo (e.g., GHS 10.00 => 1000)'
            ),
        ),
        migrations.AlterField(
            model_name='payment',
            name='reference',
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')],
                default='pending',
                max_length=16
            ),
        ),
       
    ]

