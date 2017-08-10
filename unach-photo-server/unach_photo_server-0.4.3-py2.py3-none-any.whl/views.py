# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.shortcuts import render
from jsonview.decorators import json_view
from .models import PhotoRepository, AppRegister


def home_test(request):
    return render(request, 'unach_photo_server/home_test.html')


@json_view
def get_photo_by_name(request):

    all_repos = PhotoRepository.objects.filter(
        active=True
    )

    if request.is_ajax():
        photo_name = request.GET.get('photo_name', None)
        refresh = request.GET.get('refresh', False)
        token = request.GET.get('token', None)

        '''
            Si photo_name y token existen en la solicitud
        '''
        if photo_name and token:
            '''
                Si token es registrado en alguna app y activo
            '''
            if AppRegister.objects.filter(token__iexact=token, active=True).exists():

                '''
                    Excluir solicitudes de dominios no conocidos
                '''
                can_reply = False

                if not settings.DEBUG:
                    '''
                        Si estamos en modo produccion entonces
                        solo se aceptan solicitudes de dominios conocidos.
                    '''
                    if AppRegister.objects.filter(
                            token__iexact=token,
                            active=True,
                            domain_name__icontains=request.get_host()).exists():
                        can_reply = True

                else:
                    '''
                        Si estamos en modo DEBUG aceptamos solicitudes 
                        de cualquier dominio.
                    '''
                    can_reply = True

                if can_reply:
                    if PhotoRepository.is_rut(photo_name):

                        data_info = PhotoRepository.search_photo_by_name(
                            all_repos,
                            photo_name,
                            refresh
                        )

                        return data_info
                    else:
                        return {
                            'error': 'Formato de nombre no permitido',
                            'success': False
                        }

            else:
                return {
                    'error': 'No tiene permisos',
                    'success': False
                }

    return {
        'error': 'Solicitud no permitida',
        'success': False
    }


@json_view
def get_photo_blob(request):

    all_repos = PhotoRepository.objects.filter(
        repo_type='database',
        is_blob=True,
        active=True
    )

    if request.is_ajax():
        photo_name = request.GET.get('photo_name', None)
        token = request.GET.get('token', None)

        '''
            Si photo_name y token existen en la solicitud
        '''
        if photo_name and token:
            '''
                Si token es registrado en alguna app y activo
            '''
            if AppRegister.objects.filter(token__iexact=token, active=True).exists():

                '''
                    Excluir solicitudes de dominios no conocidos
                '''
                can_reply = False

                if not settings.DEBUG:
                    '''
                        Si estamos en modo produccion entonces
                        solo se aceptan solicitudes de dominios conocidos.
                    '''
                    if AppRegister.objects.filter(
                            token__iexact=token,
                            active=True,
                            domain_name__icontains=request.get_host()).exists():
                        can_reply = True

                else:
                    '''
                        Si estamos en modo DEBUG aceptamos solicitudes 
                        de cualquier dominio.
                    '''
                    can_reply = True

                if can_reply:
                    if PhotoRepository.is_rut(photo_name):

                        data_info = PhotoRepository.search_photo_by_name(
                            all_repos,
                            photo_name,
                            refresh=True
                        )

                        return data_info
                    else:
                        return {
                            'error': 'Formato de nombre no permitido',
                            'success': False
                        }

            else:
                return {
                    'error': 'No tiene permisos',
                    'success': False
                }

    return {
        'error': 'Solicitud no permitida',
        'success': False
    }
