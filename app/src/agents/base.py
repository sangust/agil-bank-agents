"""Motor de um turno de agente: loop LLM <-> ferramentas, com efeitos no estado."""
from __future__ import annotations

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage

from src.agents.common import Handler
from src.core.constants import MAX_ITERACOES_TURNO, MSG_INSTABILIDADE
from src.core.logging import get_logger
from src.providers.llm import get_chat_model

logger = get_logger(__name__)

INSTRUCAO_RESPOSTA_FINAL = SystemMessage(
    content=(
        "Escreva AGORA a resposta final ao cliente, em português do Brasil, com suas "
        "próprias palavras: curta (1 a 3 frases), cordial e direta. Baseie-se no resultado "
        "das ferramentas acima. Não chame ferramentas e não copie textos internos."
    )
)


def _tem_texto(mensagens: list) -> bool:
    return any(isinstance(msg, AIMessage) and msg.content for msg in mensagens)


def _redigir_resposta(modelo: BaseChatModel, convo: list, agente: str) -> AIMessage | None:
    """Pede ao modelo (sem ferramentas) que escreva a resposta final ao cliente."""
    try:
        resposta = modelo.invoke([*convo, INSTRUCAO_RESPOSTA_FINAL])
    except Exception as exc:
        logger.error("Falha ao redigir resposta final no agente %s: %s", agente, exc)
        return None
    return resposta if isinstance(resposta, AIMessage) and resposta.content else None


def run_agent_turn(
    state: dict,
    agent_name: str,
    system_prompt: str,
    tools: list,
    handlers: dict[str, Handler],
) -> dict:
    """Executa um turno do agente e retorna as atualizações de estado."""
    modelo = get_chat_model()
    modelo_com_tools = modelo.bind_tools(tools) if tools else modelo

    convo = [SystemMessage(content=system_prompt), *state["messages"]]
    novas_mensagens: list = []
    updates: dict = {"current_agent": agent_name, "_goto": None}
    houve_handoff = False

    for _ in range(MAX_ITERACOES_TURNO):
        try:
            resposta: AIMessage = modelo_com_tools.invoke(convo)
        except Exception as exc:  # LLM indisponível mesmo com fallback
            logger.error("Falha ao invocar LLM no agente %s: %s", agent_name, exc)
            novas_mensagens.append(AIMessage(content=MSG_INSTABILIDADE))
            break

        convo.append(resposta)
        novas_mensagens.append(resposta)
        if not resposta.tool_calls:
            break

        for chamada in resposta.tool_calls:
            handler = handlers.get(chamada["name"])
            if handler is None:
                conteudo, efeitos = (
                    f"Ferramenta não disponível para este agente: {chamada['name']}.", {}
                )
            else:
                conteudo, efeitos = handler(chamada.get("args") or {}, {**state, **updates})

            mensagem = ToolMessage(
                content=conteudo, tool_call_id=chamada["id"], name=chamada["name"]
            )
            convo.append(mensagem)
            novas_mensagens.append(mensagem)

            updates.update(efeitos)
            houve_handoff = houve_handoff or bool(efeitos.get("_goto"))

        # Handoff interrompe o turno: quem fala com o cliente é o agente de destino.
        # (finished NÃO interrompe: o modelo se despede antes de encerrar.)
        if houve_handoff:
            break

    # Rede de segurança: modelos menores às vezes encerram o turno após uma tool call sem
    # produzir texto. Sem isso, o cliente ficaria sem resposta.
    if not houve_handoff and not _tem_texto(novas_mensagens):
        redigida = _redigir_resposta(modelo, convo, agent_name)
        if redigida is not None:
            novas_mensagens.append(redigida)

    updates["messages"] = novas_mensagens
    return updates
