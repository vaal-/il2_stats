from .models import SquadMember


def get_squad_member(user):
    try:
        squad_member = SquadMember.objects.select_related('squad').get(member_id=user.pk)
        return squad_member
    except SquadMember.DoesNotExist:
        return None
