from rolepermissions.roles import assign_role

from SberBank.roles import VIPUser
from cards import MESSAGE_NOT_ENOUGH_BALANCE
from cards.models import Card
from vip_users import VIP_COST


class VIPService:
    def buy_vip(self, user, card_id):
        card = Card.objects.get(id=card_id)
        # TODO: TransferService().transfer()

        if card.balance < VIP_COST:
            return MESSAGE_NOT_ENOUGH_BALANCE, False
        card.balance -= VIP_COST
        card.save()
        assign_role(user, VIPUser)
        return "", True
