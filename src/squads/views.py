from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext_lazy as _

from .decorators import squad_member_required
from .forms import ProfileForm, RegistrationForm
from .models import Squad, SquadMember
from .utils import get_squad_member


@never_cache
@login_required
def main(request):
    squad_member = get_squad_member(request.user)
    if not squad_member:
        return render(request, 'squads/main_wo_squad.html')

    if request.POST and squad_member.is_admin:
        _action, member_id = request.POST.get('action'), request.POST.get('member_id')
        try:
            member = SquadMember.objects.get(member_id=member_id, squad_id=squad_member.squad.pk)
        except SquadMember.DoesNotExist:
            member = None

        if member and squad_member != member:
            # TODO добавить мессаги
            if _action == 'kick':
                member.kick_from_squad()
            elif _action == 'give_admin':
                member.give_admin_role()
            elif _action == 'remove_admin':
                member.remove_admin_role()
        elif not member:
            if _action == 'gen_new_url':
                squad_member.squad.regenerate_join_code()

        return redirect(request.path)

    squad_members = (SquadMember.objects.select_related('member')
                     .filter(squad_id=squad_member.squad.pk).order_by('date_joined'))
    return render(request, 'squads/main_with_squad.html', {
        'squad': squad_member.squad,
        'squad_member': squad_member,
        'squad_members': squad_members,
    })


@never_cache
@login_required
def registration(request):
    if get_squad_member(user=request.user):
        return HttpResponseForbidden()
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        squad = form.save()
        SquadMember.objects.create(squad_id=squad.pk, member_id=request.user.pk, is_admin=True)
        messages.success(request, _('Your squad has been successfully registered.'))
        return redirect('squads:profile')
    return render(request, 'squads/registration.html', {'form': form})


@never_cache
@login_required
@squad_member_required(admin=True)
def profile(request):
    squad_member = request.user.squad_member
    form = ProfileForm(request.POST or None, request.FILES or None, instance=squad_member.squad)
    if form.is_valid():
        squad = form.save()
        if form.cleaned_data['rm_logo']:
            squad.logo.delete()
        messages.success(request, _('Squad profile successfully changed.'))
        return redirect(request.path)
    return render(request, 'squads/profile.html', {'form': form, 'squad': squad_member.squad})


@never_cache
@login_required
@squad_member_required()
def leave(request):
    squad_member = request.user.squad_member
    # есть ли админы в скваде помимо текущего члена
    squad_admins = (SquadMember.objects
                    .filter(squad_id=squad_member.squad.id, is_admin=True)
                    .exclude(member_id=squad_member.pk).exists())

    if request.POST:
        # TODO добавить мессаги
        if squad_member.is_admin and not squad_admins:
            squad_member.squad.remove()
        else:
            squad_member.leave_squad()
        return redirect('squads:main')

    return render(request, 'squads/leave.html', {
        'squad_member': squad_member,
        'squad_admins': squad_admins,
    })


@never_cache
@login_required
@squad_member_required(admin=True)
def remove(request):
    squad_member = request.user.squad_member

    if request.POST:
        # TODO добавить мессаги
        squad_member.squad.remove()
        return redirect('squads:main')

    return render(request, 'squads/remove.html', {
        'squad_member': squad_member,
    })


@never_cache
@login_required
def join(request, squad_id, code):
    try:
        squad = Squad.objects.get(id=squad_id, is_removed=False)
    except Squad.DoesNotExist:
        raise Http404()

    squad_member = get_squad_member(request.user)
    if squad_member:
        return render(request, 'squads/join.html', {'squad_member': squad_member})

    if squad.join_code != code:
        return render(request, 'squads/join.html', {'bad_join_url': True})

    if request.POST:
        SquadMember.objects.create(squad_id=squad.pk, member_id=request.user.pk)
        return redirect('squads:main')

    return render(request, 'squads/join.html', {
        'squad_member': squad_member,
        'squad': squad,
    })
