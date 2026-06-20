from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from datetime import date

from .forms import (JogadorForm, PeladaForm, PresencaPeladaForm, DespesaForm, PagamentoForm, ConfiguracaoSistemaForm, ImportarListaWhatsAppForm)

# Create your views here.
from .models import (Jogador, Pagamento, Despesa, Pelada, PresencaPelada, ConfiguracaoSistema, LogSistema)

@login_required
def processar_lista_whatsapp(texto):
    linhas = texto.splitlines()

    tipo_atual = None

    mapa_tipos = {
        '_GOLEIROS_': 'GOLEIRO',
        'GOLEIROS': 'GOLEIRO',

        '_LISTA_': 'LISTA',
        'LISTA': 'LISTA',

        '_RESERVAS DE CASA_': 'RESERVA_CASA',
        'RESERVAS DE CASA': 'RESERVA_CASA',

        '_RESERVAS VISITANTES_': 'RESERVA_VISITANTE',
        'RESERVAS VISITANTES': 'RESERVA_VISITANTE',
    }

    resultado = []

    for linha in linhas:

        linha = linha.strip()

        if not linha:
            continue

        linha_maiuscula = linha.upper()

        if linha_maiuscula in mapa_tipos:
            tipo_atual = mapa_tipos[linha_maiuscula]
            continue

        if '=' not in linha:
            continue

        if not tipo_atual:
            continue

        posicao_texto, nome = linha.split('=', 1)

        try:
            posicao = int(posicao_texto.strip())
        except ValueError:
            continue

        resultado.append({
            'nome': nome.strip(),
            'tipo_lista': tipo_atual,
            'posicao_lista': posicao
        })

    return resultado

@login_required
def dashboard(request):
    total_jogadores = Jogador.objects.count()

    mensalistas = Jogador.objects.filter(
        tipo='MENSALISTA'
    ).count()

    diaristas = Jogador.objects.filter(
        tipo='DIARISTA'
    ).count()

    visitantes = Jogador.objects.filter(
        tipo='VISITANTE'
    ).count()

    receita_recebida = PresencaPelada.objects.filter(
        pago=True
    ).aggregate(
        total=Sum('valor_cobrado')
    )['total'] or 0

    total_pendente = PresencaPelada.objects.filter(
        pago=False,
        valor_cobrado__gt=0
    ).aggregate(
        total=Sum('valor_cobrado')
    )['total'] or 0

    quantidade_pendencias = PresencaPelada.objects.filter(
        pago=False,
        valor_cobrado__gt=0
    ).count()

    despesas = Despesa.objects.aggregate(
        total=Sum('valor')
    )['total'] or 0

    saldo_geral = receita_recebida - despesas

    proxima_pelada = Pelada.objects.order_by('data').first()

    recebidos = PresencaPelada.objects.filter(
        pago=True
    ).count()

    pendentes = PresencaPelada.objects.filter(
        pago=False,
        valor_cobrado__gt=0
    ).count()
    
    return render(
        request,
        'financeiro/dashboard.html',
        {
            'total_jogadores': total_jogadores,
            'mensalistas': mensalistas,
            'diaristas': diaristas,
            'visitantes': visitantes,
            'receita_recebida': receita_recebida,
            'total_pendente': total_pendente,
            'quantidade_pendencias': quantidade_pendencias,
            'despesas': despesas,
            'saldo_geral': saldo_geral,
            'proxima_pelada': proxima_pelada,
            'recebidos': recebidos,
            'pendentes': pendentes,
        }
    )

@login_required
def jogador_lista(request):

    jogadores = Jogador.objects.all().order_by('nome')

    return render(
        request,
        'financeiro/jogador_lista.html',
        {
            'jogadores': jogadores
        }
    )

@login_required
def jogador_novo(request):

    if request.method == 'POST':

        form = JogadorForm(request.POST)

        if form.is_valid():

            jogador = form.save()
            
            registrar_log(
                request,
                'Adição',
                f'{jogador.nome} foi adicionado como novo jogador na pelada.'
            )

            return redirect(
                'financeiro:jogador_lista'
            )

    else:

        form = JogadorForm()

    return render(
        request,
        'financeiro/jogador_form.html',
        {
            'form': form
        }
    )

@login_required
def jogador_editar(request, pk):

    jogador = get_object_or_404(
        Jogador,
        pk=pk
    )

    form = JogadorForm(
        request.POST or None,
        instance=jogador
    )

    if request.method == 'POST':

        if form.is_valid():

            form.save()

            return redirect(
                'financeiro:jogador_lista'
            )
            
    registrar_log(
        request,
        'Edição',
        f'{jogador.nome} foi editado no sistema.'
    )

    return render(
        request,
        'financeiro/jogador_form.html',
        {
            'form': form
        }
    )

@login_required
def jogador_excluir(request, pk):

    jogador = get_object_or_404(
        Jogador,
        pk=pk
    )
    
    nome_jogador = jogador.nome

    jogador.delete()
    
    registrar_log(
    request,
    'Exclusão',
    f'{nome_jogador} foi foi excluido da pelada.'
)

    return redirect(
        'financeiro:jogador_lista'
    )

@login_required    
def pelada_lista(request):

    peladas = Pelada.objects.all().order_by('-data')

    return render(
        request,
        'financeiro/pelada_lista.html',
        {
            'peladas': peladas
        }
    )

@login_required
def pelada_nova(request):

    if request.method == 'POST':

        form = PeladaForm(request.POST)

        if form.is_valid():

            pelada = form.save()
            
            registrar_log(
                request,
                'Cadastro de pelada',
                f'Nova pelada criada para o dia {pelada.data}.'
            )

            return redirect(
                'financeiro:pelada_lista'
            )

    else:
        configuracao = ConfiguracaoSistema.objects.first()

        if configuracao:
            form = PeladaForm(
                initial={
                    'valor_diaria': configuracao.valor_diaria_padrao
                }
            )
        else:
            form = PeladaForm()

    return render(
        request,
        'financeiro/pelada_form.html',
        {
            'form': form
        }
    )

@login_required    
def pelada_detalhe(request, pk):
    pelada = get_object_or_404(
        Pelada,
        pk=pk
    )

    goleiros = pelada.presencas.filter(
        tipo_lista='GOLEIRO'
    ).order_by('posicao_lista')

    lista_principal = pelada.presencas.filter(
        tipo_lista='LISTA'
    ).order_by('posicao_lista')

    reservas_casa = pelada.presencas.filter(
        tipo_lista='RESERVA_CASA'
    ).order_by('posicao_lista')

    reservas_visitantes = pelada.presencas.filter(
        tipo_lista='RESERVA_VISITANTE'
    ).order_by('posicao_lista')
    
    todas_presencas = pelada.presencas.all()
    total_isentos = todas_presencas.filter(
        isento=True
    ).count()
    
    total_pagantes = todas_presencas.filter(
        isento=False,
        valor_cobrado__gt=0
    ).count()
    
    receita_prevista = sum(item.valor_cobrado for item in todas_presencas if not item.isento)
    
    receita_recebida = sum(item.valor_cobrado for item in todas_presencas if item.pago and not item.isento)
    
    pendencias = receita_prevista - receita_recebida
    
    saldo_pelada = receita_recebida - pelada.custo_quadra
    
    total_goleiros = goleiros.count()

    total_lista = lista_principal.count()

    total_reservas_casa = reservas_casa.count()

    total_reservas_visitantes = reservas_visitantes.count()

    return render(
        request,
        'financeiro/pelada_detalhe.html',
        {
            'pelada': pelada,
            'goleiros': goleiros,
            'lista_principal': lista_principal,
            'reservas_casa': reservas_casa,
            'reservas_visitantes': reservas_visitantes,
            
            'total_goleiros': total_goleiros,
            'total_lista': total_lista,
            'total_reservas_casa': total_reservas_casa,
            'total_reservas_visitantes': total_reservas_visitantes,
            'total_isentos': total_isentos,
            'total_pagantes': total_pagantes,
            
            'receita_prevista': receita_prevista,
            'receita_recebida': receita_recebida,
            'pendencias': pendencias,
            'saldo_pelada': saldo_pelada,
        }
    )

@login_required
def pelada_editar(request, pk):

    pelada = get_object_or_404(
        Pelada,
        pk=pk
    )

    form = PeladaForm(
        request.POST or None,
        instance=pelada
    )

    if request.method == 'POST':

        if form.is_valid():

            form.save()

            return redirect(
                'financeiro:pelada_lista'
            )

    return render(
        request,
        'financeiro/pelada_form.html',
        {
            'form': form
        }
    )

@login_required
def pelada_excluir(request, pk):
    pelada = get_object_or_404(
        Pelada,
        pk=pk
    )

    if pelada.presencas.exists():
        messages.error(
            request,
            'Esta pelada possui jogadores cadastrados e não pode ser excluída.'
        )

        return redirect(
            'financeiro:pelada_lista'
        )

    pelada.delete()

    messages.success(
        request,
        'Pelada excluída com sucesso!'
    )

    return redirect(
        'financeiro:pelada_lista'
    )

@login_required
def adicionar_presenca(request, pk):
    pelada = get_object_or_404(
        Pelada,
        pk=pk
    )

    configuracao = ConfiguracaoSistema.objects.first()

    if request.method == 'POST':
        form = PresencaPeladaForm(request.POST)

        if form.is_valid():
            presenca = form.save(commit=False)
            presenca.pelada = pelada

            if configuracao:
                limites = {
                    'GOLEIRO': configuracao.limite_goleiros,
                    'LISTA': configuracao.limite_lista_principal,
                    'RESERVA_CASA': configuracao.limite_reservas_casa,
                    'RESERVA_VISITANTE': configuracao.limite_reservas_visitantes,
                }

                limite = limites.get(presenca.tipo_lista)

                total_na_lista = PresencaPelada.objects.filter(
                    pelada=pelada,
                    tipo_lista=presenca.tipo_lista
                ).count()

                if limite and total_na_lista >= limite:
                    messages.error(
                        request,
                        f'Limite atingido para {presenca.get_tipo_lista_display()}.'
                    )

                    return redirect(
                        'financeiro:pelada_detalhe',
                        pk=pelada.id
                    )

                if presenca.posicao_lista > limite:
                    messages.error(
                        request,
                        f'A posição informada ultrapassa o limite de {limite} vagas.'
                    )

                    return redirect(
                        'financeiro:pelada_detalhe',
                        pk=pelada.id
                    )

            presenca.save()

            return redirect(
                'financeiro:pelada_detalhe',
                pk=pelada.pk
            )
    else:
        form = PresencaPeladaForm()

    return render(
        request,
        'financeiro/presenca_form.html',
        {
            'form': form,
            'pelada': pelada
        }
    )

@login_required    
def editar_presenca(request, pk):
    presenca = get_object_or_404(
        PresencaPelada,
        pk=pk
    )

    form = PresencaPeladaForm(
        request.POST or None,
        instance=presenca
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()

            return redirect(
                'financeiro:pelada_detalhe',
                pk=presenca.pelada.id
            )

    return render(
        request,
        'financeiro/presenca_form.html',
        {
            'form': form,
            'pelada': presenca.pelada
        }
    )

@login_required    
def remover_presenca(request, pk):

    presenca = get_object_or_404(
        PresencaPelada,
        pk=pk
    )

    pelada_id = presenca.pelada.id

    presenca.delete()

    return redirect(
        'financeiro:pelada_detalhe',
        pk=pelada_id
    )
    
@login_required
def marcar_isento(request, pk):
    presenca = get_object_or_404(
        PresencaPelada,
        pk=pk
    )
    
    presenca.isento = True
    presenca.pago = False
    presenca.valor_cobrado = 0
    presenca.save()
    
    registrar_log(
        request,
        'Isenção',
        f'{presenca.jogador.nome} foi marcado como isento na pelada {presenca.pelada.data}.'
    )
    
    return redirect(
        'financeiro:pelada_detalhe',
        pk=presenca.pelada.id
    )

@login_required
def remover_isencao(request, pk):
    presenca = get_object_or_404(
        PresencaPelada,
        pk=pk
    )
    
    presenca.isento = False
    presenca.save()
    
    registrar_log(
        request,
        'remover isenção',
        f'{presenca.jogador.nome} foi removido como isento na pelada {presenca.pelada.data}.'
    )
    
    return redirect(
        'financeiro:pelada_detalhe',
        pk=presenca.pelada.id
    )

@login_required    
def marcar_presenca_paga(request, pk):

    presenca = get_object_or_404(
        PresencaPelada,
        pk=pk
    )

    presenca.pago = True
    presenca.save()

    return redirect(
        'financeiro:pelada_detalhe',
        pk=presenca.pelada.id
    )

@login_required    
def marcar_presenca_pendente(request, pk):
    presenca = get_object_or_404(
        PresencaPelada,
        pk=pk
    )

    presenca.pago = False
    presenca.save()

    return redirect(
        'financeiro:pelada_detalhe',
        pk=presenca.pelada.id
    )

@login_required    
def pendencias(request):
    pendencias = PresencaPelada.objects.select_related(
        'pelada',
        'jogador'
    ).filter(
        pago=False,
        isento=False,
        valor_cobrado__gt=0
    ).order_by(
        'pelada__data',
        'jogador__nome'
    )

    total_pendente = sum(
        item.valor_cobrado
        for item in pendencias
    )

    return render(
        request,
        'financeiro/pendencias.html',
        {
            'pendencias': pendencias,
            'total_pendente': total_pendente,
        }
    )

@login_required    
def ranking_participacao(request):

    ranking = Jogador.objects.annotate(
        total_presencas=Count('presencas')
    ).order_by(
        '-total_presencas',
        'nome'
    )

    return render(
        request,
        'financeiro/ranking.html',
        {
            'ranking': ranking
        }
    )

@login_required    
def relatorio_mensal(request):
    hoje = date.today()

    mes = int(request.GET.get('mes', hoje.month))
    ano = int(request.GET.get('ano', hoje.year))

    presencas = PresencaPelada.objects.select_related(
        'pelada',
        'jogador'
    ).filter(
        pelada__data__month=mes,
        pelada__data__year=ano
    )

    receitas = presencas.filter(
        pago=True
    ).aggregate(
        total=Sum('valor_cobrado')
    )['total'] or 0

    pendencias = presencas.filter(
        pago=False,
        valor_cobrado__gt=0
    ).aggregate(
        total=Sum('valor_cobrado')
    )['total'] or 0

    despesas = Despesa.objects.filter(
        data__month=mes,
        data__year=ano
    ).aggregate(
        total=Sum('valor')
    )['total'] or 0

    saldo = receitas - despesas

    peladas_realizadas = Pelada.objects.filter(
        data__month=mes,
        data__year=ano
    ).count()

    jogadores_participantes = presencas.values(
        'jogador'
    ).distinct().count()

    return render(
        request,
        'financeiro/relatorio_mensal.html',
        {
            'mes': mes,
            'ano': ano,
            'receitas': receitas,
            'pendencias': pendencias,
            'despesas': despesas,
            'saldo': saldo,
            'peladas_realizadas': peladas_realizadas,
            'jogadores_participantes': jogadores_participantes,
            'presencas': presencas,
        }
    )

@login_required    
def despesa_lista(request):
    despesas = Despesa.objects.all().order_by('-data')

    return render(
        request,
        'financeiro/despesa_lista.html',
        {'despesas': despesas}
    )

@login_required
def despesa_nova(request):
    if request.method == 'POST':
        form = DespesaForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('financeiro:despesa_lista')
    else:
        form = DespesaForm()

    return render(
        request,
        'financeiro/despesa_form.html',
        {'form': form}
    )

@login_required
def despesa_editar(request, pk):
    despesa = get_object_or_404(Despesa, pk=pk)

    form = DespesaForm(
        request.POST or None,
        instance=despesa
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('financeiro:despesa_lista')

    return render(
        request,
        'financeiro/despesa_form.html',
        {'form': form}
    )

@login_required
def despesa_excluir(request, pk):
    despesa = get_object_or_404(Despesa, pk=pk)
    despesa.delete()

    return redirect('financeiro:despesa_lista')

@login_required
def pagamento_lista(request):

    pagamentos = Pagamento.objects.select_related(
        'jogador'
    )

    jogador = request.GET.get('jogador')
    forma = request.GET.get('forma')

    if jogador:
        pagamentos = pagamentos.filter(
            jogador__nome__icontains=jogador
        )

    if forma:
        pagamentos = pagamentos.filter(
            forma_pagamento=forma
        )

    pagamentos = pagamentos.order_by(
        '-data_pagamento',
        '-criado_em'
    )

    total_recebido = sum(
        pagamento.valor
        for pagamento in pagamentos
    )

    total_pix = sum(
        pagamento.valor
        for pagamento in pagamentos
        if pagamento.forma_pagamento == 'PIX'
    )

    total_dinheiro = sum(
        pagamento.valor
        for pagamento in pagamentos
        if pagamento.forma_pagamento == 'DINHEIRO'
    )

    total_cartao = sum(
        pagamento.valor
        for pagamento in pagamentos
        if pagamento.forma_pagamento == 'CARTAO'
    )

    return render(
        request,
        'financeiro/pagamento_lista.html',
        {
            'pagamentos': pagamentos,

            'total_recebido': total_recebido,
            'total_pix': total_pix,
            'total_dinheiro': total_dinheiro,
            'total_cartao': total_cartao,
        }
    )

@login_required
def registrar_pagamento(request, pk):

    presenca = get_object_or_404(
        PresencaPelada,
        pk=pk
    )

    if request.method == 'POST':

        form = PagamentoForm(request.POST)

        if form.is_valid():

            pagamento = form.save(commit=False)

            pagamento.jogador = presenca.jogador
            pagamento.presenca = presenca

            pagamento.referencia = (
                f'Pelada {presenca.pelada.data.strftime("%d/%m/%Y")}'
            )

            pagamento.valor = presenca.valor_cobrado

            pagamento.status = 'PAGO'

            pagamento.save()

            presenca.pago = True
            presenca.save()

            return redirect(
                'financeiro:pelada_detalhe',
                pk=presenca.pelada.id
            )

    else:

        form = PagamentoForm(
            initial={
                'data_pagamento': date.today()
            }
        )

    return render(
        request,
        'financeiro/pagamento_form.html',
        {
            'form': form,
            'presenca': presenca
        }
    )
    
@login_required
def configuracoes(request):
    configuracao = ConfiguracaoSistema.objects.first()

    if not configuracao:
        configuracao = ConfiguracaoSistema.objects.create()

    form = ConfiguracaoSistemaForm(
        request.POST or None,
        instance=configuracao
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('financeiro:configuracoes')

    return render(
        request,
        'financeiro/configuracoes.html',
        {
            'form': form
        }
    )
    
@login_required
def importar_lista_whatsapp(request, pk):
    pelada = get_object_or_404(Pelada, pk=pk)

    if request.method == 'POST':
        form = ImportarListaWhatsAppForm(request.POST)

        if form.is_valid():
            texto = form.cleaned_data['texto']
            linhas = texto.splitlines()

            tipo_atual = None
            criados = 0
            nao_encontrados = []

            mapa_tipos = {
                '_GOLEIROS_': 'GOLEIRO',
                'GOLEIROS': 'GOLEIRO',

                '_LISTA_': 'LISTA',
                'LISTA': 'LISTA',

                '_RESERVAS DE CASA_': 'RESERVA_CASA',
                'RESERVAS DE CASA': 'RESERVA_CASA',

                '_RESERVAS VISITANTES_': 'RESERVA_VISITANTE',
                'RESERVAS VISITANTES': 'RESERVA_VISITANTE',
            }

            for linha in linhas:
                linha = linha.strip()

                if not linha:
                    continue

                linha_maiuscula = linha.upper()

                if linha_maiuscula in mapa_tipos:
                    tipo_atual = mapa_tipos[linha_maiuscula]
                    continue

                if '=' not in linha or not tipo_atual:
                    continue

                posicao_texto, nome = linha.split('=', 1)

                posicao_texto = posicao_texto.strip()
                nome = nome.strip()

                if not posicao_texto or not nome:
                    continue

                try:
                    posicao = int(posicao_texto)
                except ValueError:
                    continue

                jogador = Jogador.objects.filter(
                    nome__iexact=nome
                ).first()

                if not jogador:
                    jogador = Jogador.objects.create(
                        nome=nome,
                        tipo='DIARISTA',
                        valor_mensal=0,
                        desconto_percentual=0,
                        ativo=True
                    )

                ja_existe = PresencaPelada.objects.filter(
                    pelada=pelada,
                    jogador=jogador
                ).exists()

                if ja_existe:
                    continue

                PresencaPelada.objects.create(
                    pelada=pelada,
                    jogador=jogador,
                    tipo_lista=tipo_atual,
                    posicao_lista=posicao,
                    confirmado=True,
                    pago=False,
                    valor_cobrado=pelada.valor_diaria
                )

                criados += 1

            if criados:
                messages.success(
                    request,
                    f'{criados} jogadores importados com sucesso.'
                )

            if nao_encontrados:
                messages.error(
                    request,
                    'Jogadores não encontrados: ' + ', '.join(nao_encontrados)
                )

            return redirect(
                'financeiro:pelada_detalhe',
                pk=pelada.id
            )

    else:
        form = ImportarListaWhatsAppForm()

    return render(
        request,
        'financeiro/importar_lista_whatsapp.html',
        {
            'form': form,
            'pelada': pelada
        }
    )

@login_required    
def registrar_log(request, acao, descricao):
    LogSistema.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        acao=acao,
        descricao=descricao
    )
    
@login_required
def log_sistema(request):
    logs = LogSistema.objects.select_related(
        'usuario'
    ).order_by('-criado_em')[:200]

    return render(
        request,
        'financeiro/log_sistema.html',
        {
            'logs': logs
        }
    )