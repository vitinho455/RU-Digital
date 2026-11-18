% rebase('app/views/html/base', titulo='Meu painel', ativo='painel', sessao=sessao, flash=flash)
<h1>Olá, {{aluno.nome.split()[0]}}</h1>
<div class="grade">
    <div class="coluna">
        <div class="ficha" role="group" aria-label="Saldo do cartão do RU">
            <div class="ficha-corpo">
                <p class="ficha-rotulo">Saldo no cartão do RU</p>
                <p class="ficha-valor">{{brl(carteira.saldo_atual)}}</p>
            </div>
            <p class="ficha-anterior">Saldo anterior: {{brl(carteira.saldo_anterior)}}</p>
        </div>

        <form class="formulario recarga" method="post" action="/recarga">
            <input type="hidden" name="csrf" value="{{sessao['csrf']}}">
            <h2>Recarregar saldo</h2>
            <p class="nota">Simulação: nenhum pagamento real é feito, o valor entra direto no saldo. Recarga mínima: {{brl(minimo)}}.</p>
            <label for="valor">Valor da recarga</label>
            <input id="valor" name="valor" value="{{valor}}" inputmode="decimal" autocomplete="off" placeholder="R$ 20,00" data-dinheiro required>
            <label for="pagamento">Forma de pagamento</label>
            <select id="pagamento" name="pagamento">
                <option value="pix" {{'selected' if pagamento in ('', 'pix') else ''}}>PIX</option>
                % for c in cartoes:
                <option value="cartao:{{c.id}}" {{'selected' if pagamento == 'cartao:%d' % c.id else ''}} {{'disabled' if c.vencido() else ''}}>{{c.rotulo}}{{' (vencido)' if c.vencido() else ''}}</option>
                % end
                <option value="novo">+ Novo cartão de crédito…</option>
            </select>
            <button type="submit" class="primario">Recarregar</button>
        </form>
    </div>

    <div class="coluna">
        <section class="perfil" aria-labelledby="titulo-dados">
            % if aluno.foto_url:
            <img class="foto" src="{{aluno.foto_url}}" alt="Foto de {{aluno.nome}}">
            % else:
            <span class="foto iniciais" aria-hidden="true">{{iniciais(aluno.nome)}}</span>
            % end
            <div>
                <h2 id="titulo-dados">{{aluno.nome}}</h2>
                <dl>
                    <dt>Código RU</dt><dd>{{aluno.matricula}}</dd>
                    <dt>E-mail</dt><dd>{{aluno.email}}</dd>
                </dl>
                <a class="editar-perfil" href="/perfil">Editar perfil</a>
            </div>
        </section>

        <section aria-labelledby="titulo-historico">
            <h2 id="titulo-historico">Últimas movimentações</h2>
            % if carteira.historico_transacoes:
            <div class="rolagem">
                <table>
                    <thead><tr><th scope="col">Data</th><th scope="col">Descrição</th><th scope="col" class="num">Valor</th><th scope="col" class="num">Saldo</th></tr></thead>
                    <tbody>
                    % for t in carteira.historico_transacoes:
                        <tr>
                            <td>{{data_br(t['criado_em'])}}</td>
                            <td>{{t['descricao']}}</td>
                            % if t['tipo'] == 'recarga':
                            <td class="num entrada-valor">+ {{brl(t['valor'])}}</td>
                            % else:
                            <td class="num saida-valor">- {{brl(t['valor'])}}</td>
                            % end
                            <td class="num">{{brl(t['saldo_apos'])}}</td>
                        </tr>
                    % end
                    </tbody>
                </table>
            </div>
            % else:
            <p class="vazio">Você ainda não tem movimentações. Faça sua primeira recarga ao lado.</p>
            % end
        </section>
    </div>
</div>

% include('app/views/html/cartao_dialogo', sessao=sessao, origem='painel')
