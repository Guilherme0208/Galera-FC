from django.db import models

# Create your models here.
class Jogador(models.Model):
    TIPO_CHOICES = [
        ('MENSALISTA', 'Mensalista'),
        ('DIARISTA', 'Diarista'),
        ('VISITANTE', 'Visitante'),
    ]
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True)
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='DIARISTA'
    )
    
    valor_mensal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    desconto_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return self.nome
    
class Pagamento(models.Model):
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
    ]
    
    FORMA_CHOICES =[
        ('PIX', 'Pix'),
        ('DINHEIRO', 'Dinheiro'),
        ('CARTAO', 'Cartao'),
    ]
    
    jogador = models.ForeignKey(
        Jogador,
        on_delete=models.CASCADE,
        related_name='pagamentos'
    )
    
    presenca = models.ForeignKey(
        'PresencaPelada',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagamentos'
    )
    
    referencia = models.CharField(
        max_length=20
    )
    
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )
    
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_CHOICES,
        blank=True
    )
    
    data_pagamento = models.DateField(
        null=True,
        blank=True
    )
    
    observacao = models.TextField(
        blank=True
    )
    
    criado_em = models.DateTimeField(
        auto_now_add=True
    )
    
    def __str__(self):
        return f'{self.jogador.nome} - {self.referencia}'
    
class Despesa(models.Model):
    CATEGORIAS = [
        ('QUADRA', 'Quadra'),
        ('BOLA', 'Bola'),
        ('COLETE', 'Colete'),
        ('AGUA', 'Água'),
        ('OUTROS', 'Outros'),
    ]
    
    descricao = models.CharField(
        max_length=150
    )

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    data = models.DateField()

    observacao = models.TextField(
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.descricao
    
class Pelada(models.Model):
    data = models.DateField()
    horario = models.TimeField(blank=True, null=True)
    local = models.CharField(max_length=100, blank=True)
    valor_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    custo_quadra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observacao = models.TextField(blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Pelada - {self.data.strftime("%d/%m/%Y")}'
    
class PresencaPelada(models.Model):
    TIPO_LISTA_CHOICES = [
        ('GOLEIRO', 'Goleiro'),
        ('LISTA', 'Lista Principal'),
        ('RESERVA_CASA', 'Reserva de Casa'),
        ('RESERVA_VISITANTE', 'Reserva Visitante'),
    ]

    pelada = models.ForeignKey(
        Pelada,
        on_delete=models.CASCADE,
        related_name='presencas'
    )

    jogador = models.ForeignKey(
        Jogador,
        on_delete=models.CASCADE,
        related_name='presencas'
    )

    tipo_lista = models.CharField(
        max_length=20,
        choices=TIPO_LISTA_CHOICES,
        default='LISTA'
    )

    posicao_lista = models.PositiveIntegerField()

    confirmado = models.BooleanField(default=True)
    pago = models.BooleanField(default=False)

    valor_cobrado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    observacao = models.TextField(blank=True)

    class Meta:
        unique_together = (
            ('pelada', 'jogador'),
            ('pelada', 'tipo_lista', 'posicao_lista'),
        )

        ordering = [
            'pelada',
            'tipo_lista',
            'posicao_lista'
        ]

    def __str__(self):
        return f'{self.jogador.nome} - {self.get_tipo_lista_display()} {self.posicao_lista}'
    
class ConfiguracaoSistema(models.Model):
    nome_grupo = models.CharField(max_length=100, default='Galera FC')

    valor_diaria_padrao = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    limite_lista_principal = models.PositiveIntegerField(default=24)
    limite_goleiros = models.PositiveIntegerField(default=4)
    limite_reservas_casa = models.PositiveIntegerField(default=5)
    limite_reservas_visitantes = models.PositiveIntegerField(default=5)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_grupo