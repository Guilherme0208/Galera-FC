from django import forms
from .models import Jogador, Pelada, PresencaPelada, Despesa, Pagamento, ConfiguracaoSistema

class JogadorForm(forms.ModelForm):
    
    class Meta:
        model = Jogador
        
        fields = [
            'nome',
            'telefone',
            'tipo',
            'valor_mensal',
            'desconto_percentual',
            'ativo',
        ]
        
        widgets = {
            'nome': forms.TextInput(
                attrs={'placeholder': 'Nome do jogador'}
            ),
            'telefone': forms.TextInput(
                attrs={'placeholder': '(62) 99999-9999'}
            ),
        }
        
class PeladaForm(forms.ModelForm):

    class Meta:
        model = Pelada

        fields = [
            'data',
            'horario',
            'local',
            'valor_diaria',
            'custo_quadra',
            'observacao',
        ]

        widgets = {
            'data': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            ),
            'horario': forms.TimeInput(
                attrs={
                    'type': 'time'
                }
            ),
            'local': forms.TextInput(
                attrs={
                    'placeholder': 'Ex: Arena Futebol Society'
                }
            ),
            'observacao': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Observações sobre a pelada'
                }
            ),
        }
        
class PresencaPeladaForm(forms.ModelForm):

    class Meta:
        model = PresencaPelada

        fields = [
            'jogador',
            'tipo_lista',
            'posicao_lista',
            'confirmado',
            'pago',
            'valor_cobrado',
            'observacao',
        ]
        
class DespesaForm(forms.ModelForm):

    class Meta:
        model = Despesa

        fields = [
            'descricao',
            'categoria',
            'valor',
            'data',
            'observacao',
        ]

        widgets = {
            'data': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'observacao': forms.Textarea(
                attrs={'rows': 3}
            ),
        }
        
class PagamentoForm(forms.ModelForm):
    
    class Meta:
        model = Pagamento
        
        fields = [
            'forma_pagamento',
            'data_pagamento',
            'observacao',
        ]
        
        widgets = {
            'data_pagamento': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'observacao': forms.Textarea(
                attrs={'rows': 3}
            ),
        }
        
class ConfiguracaoSistemaForm(forms.ModelForm):

    class Meta:
        model = ConfiguracaoSistema

        fields = [
            'nome_grupo',
            'valor_diaria_padrao',
            'limite_lista_principal',
            'limite_goleiros',
            'limite_reservas_casa',
            'limite_reservas_visitantes',
        ]
        
class ImportarListaWhatsAppForm(forms.Form):
    texto = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 18,
                'placeholder': 'Cole aqui a lista do WhatsApp...'
            }
        ),
        label='Lista do WhatsApp'
    )