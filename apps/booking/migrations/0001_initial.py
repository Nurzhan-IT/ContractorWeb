from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TimeSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('service_type', models.CharField(blank=True, max_length=50)),
                ('is_available', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['date', 'start_time'],
                'unique_together': {('date', 'start_time')},
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('service_type', models.CharField(max_length=50)),
                ('comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(
                    choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
                    default='pending',
                    max_length=20,
                )),
                ('slot', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='booking',
                    to='booking.timeslot',
                )),
            ],
        ),
    ]
