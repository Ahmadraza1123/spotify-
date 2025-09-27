

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('albums', '0002_album_artist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='cover_image',
            field=models.ImageField(blank=True, default=1, upload_to='albums/covers/'),
            preserve_default=False,
        ),
    ]
