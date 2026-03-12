from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        # Drop the old auto timestamp
        migrations.RemoveField(
            model_name='beforeafterproject',
            name='created_at',
        ),
        # Add new fields (preserve_default=False removes the temp default from schema)
        migrations.AddField(
            model_name='beforeafterproject',
            name='duration',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='beforeafterproject',
            name='savings',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='beforeafterproject',
            name='client_location',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='beforeafterproject',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        # Tighten service_type: max_length 100→50, add choices
        migrations.AlterField(
            model_name='beforeafterproject',
            name='service_type',
            field=models.CharField(
                choices=[
                    ('plumbing',   'Plumbing'),
                    ('electrical', 'Electrical'),
                    ('roofing',    'Roofing'),
                    ('hvac',       'HVAC'),
                ],
                max_length=50,
            ),
        ),
        # description: remove blank=True
        migrations.AlterField(
            model_name='beforeafterproject',
            name='description',
            field=models.TextField(),
        ),
        # before_image / after_image: new upload_to paths
        migrations.AlterField(
            model_name='beforeafterproject',
            name='before_image',
            field=models.ImageField(upload_to='portfolio/before/'),
        ),
        migrations.AlterField(
            model_name='beforeafterproject',
            name='after_image',
            field=models.ImageField(upload_to='portfolio/after/'),
        ),
        # Change ordering from [-created_at] to [order]
        migrations.AlterModelOptions(
            name='beforeafterproject',
            options={'ordering': ['order']},
        ),
    ]
