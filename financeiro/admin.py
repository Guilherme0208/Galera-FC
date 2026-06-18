from django.contrib import admin
from .models import Jogador, Pagamento, Despesa, Pelada, PresencaPelada
# Register your models here.

@admin. register(Jogador)
class JogadorAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'tipo',
        'telefone',
        'ativo'
    )
    
    search_fields = (
        'nome',
        'telefone'
    )
    
@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = (
        'jogador',
        'referencia',
        'valor',
        'status',
        'data_pagamento'
    )

    list_filter = (
        'status',
        'forma_pagamento'
    )

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = (
        'descricao',
        'categoria',
        'valor',
        'data'
    )

    list_filter = (
        'categoria',
    )
    
@admin.register(Pelada)
class PeladaAdmin(admin.ModelAdmin):
    list_display = (
        'data',
        'horario',
        'local',
        'valor_diaria',
    )

    search_fields = (
        'local',
    )


@admin.register(PresencaPelada)
class PresencaPeladaAdmin(admin.ModelAdmin):
    list_display = (
        'pelada',
        'jogador',
        'confirmado',
        'pago',
        'valor_cobrado',
    )

    list_filter = (
        'confirmado',
        'pago',
    )

    search_fields = (
        'jogador__nome',
    )