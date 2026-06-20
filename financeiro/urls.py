from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    path('jogadores/', views.jogador_lista, name='jogador_lista'),
    path('jogadores/novo/', views.jogador_novo, name='jogador_novo'),
    path('jogadores/editar/<int:pk>/', views.jogador_editar, name='jogador_editar'),
    path('jogadores/excluir/<int:pk>/', views.jogador_excluir, name='jogador_excluir'),
    
    path('peladas/', views.pelada_lista, name='pelada_lista'),
    path('peladas/nova/', views.pelada_nova, name='pelada_nova'),
    path('peladas/editar/<int:pk>/', views.pelada_editar, name='pelada_editar'),
    path('peladas/excluir/<int:pk>/', views.pelada_excluir, name='pelada_excluir'),
    path('peladas/<int:pk>/', views.pelada_detalhe, name='pelada_detalhe'),
    
    path('peladas/<int:pk>/adicionar-jogador/', views.adicionar_presenca, name='adicionar_presenca'),
    path('peladas/<int:pk>/importar-whatsapp/', views.importar_lista_whatsapp, name='importar_lista_whatsapp'),
    
    path('presenca/excluir/<int:pk>/', views.remover_presenca, name='remover_presenca'),
    path('presenca/editar/<int:pk>/', views.editar_presenca, name='editar_presenca'),
    path('presenca/<int:pk>/marcar-paga/', views.marcar_presenca_paga, name='marcar_presenca_paga'),
    path('presenca/<int:pk>/marcar-pendente/', views.marcar_presenca_pendente, name='marcar_presenca_pendente'),
    path('presenca/<int:pk>/isentar/', views.marcar_isento, name='marcar_isento'),
    path('presenca/<int:pk>/remover-isencao/', views.remover_isencao, name='remover_isencao'),
    
    path('pendencias/', views.pendencias, name='pendencias'),
    
    path('relatorio-mensal/', views.relatorio_mensal, name='relatorio_mensal'),
    
    path('ranking/', views.ranking_participacao, name='ranking_participacao'),
    
    path('despesas/', views.despesa_lista, name='despesa_lista'),
    path('despesas/nova/', views.despesa_nova, name='despesa_nova'),
    path('despesas/editar/<int:pk>/', views.despesa_editar, name='despesa_editar'),
    path('despesas/excluir/<int:pk>/', views.despesa_excluir, name='despesa_excluir'),
    
    path('pagamentos', views.pagamento_lista, name='pagamento_lista'),
    path('pagamentos/registrar/<int:pk>/', views.registrar_pagamento, name='registrar_pagamento'),
    
    path('logs/', views.log_sistema, name='log_sistema'),
    
    path('configuracoes/', views.configuracoes, name='configuracoes'),
]    