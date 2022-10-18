from ...giftcard import models


def resolve_gift_card(id):
    return models.GiftCard.objects.filter(pk=id).first()


def resolve_gift_cards():
    return models.GiftCard.objects.all()
