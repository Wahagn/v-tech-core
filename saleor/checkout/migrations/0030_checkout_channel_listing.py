# Generated by Django 3.1 on 2020-09-04 10:00

import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def add_channel_slug(apps, schema_editor):
    Channel = apps.get_model("channel", "Channel")
    Checkout = apps.get_model("checkout", "Checkout")

    channels_dict = {}

    for checkout in Checkout.objects.iterator():
        currency = checkout.currency
        channel = channels_dict.get(currency)

        if not channel:
            name = f"Channel {currency}"
            channel, _ = Channel.objects.get_or_create(
                currency_code=currency,
                defaults={"name": name, "slug": slugify(name)},
            )
            channels_dict[currency] = channel

        checkout.channel = channel

        checkout.save(update_fields=["channel"])


class Migration(migrations.Migration):

    dependencies = [
        ("channel", "0001_initial"),
        ("checkout", "0029_auto_20200904_0529"),
    ]

    operations = [
        migrations.AddField(
            model_name="checkout",
            name="channel",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="checkouts",
                to="channel.channel",
            ),
        ),
        migrations.AlterField(
            model_name="checkout",
            name="currency",
            field=models.CharField(max_length=3),
        ),
        migrations.RunPython(add_channel_slug),
        migrations.AlterField(
            model_name="checkout",
            name="channel",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="checkouts",
                to="channel.channel",
            ),
        ),
    ]
