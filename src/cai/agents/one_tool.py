"""
CTF Agent with one tool
"""

from cai.sdk.agents import Agent, OpenAIChatCompletionsModel
from cai.tools.reconnaissance.enumeration import enum_network_surface
from cai.tools.reconnaissance.generic_linux_command import generic_linux_command  # noqa
from cai.tools.reconnaissance.nmap import nmap_scan
from openai import AsyncOpenAI
from cai.util import create_system_prompt_renderer, load_prompt_template
from cai.config import get_config
from cai.agents.guardrails import get_security_guardrails
from cai.util.llm_api_base import resolve_llm_openai_compatible_api_key
from cai.tools.web.http_probe import http_probe

_cfg = get_config()
model_name = _cfg.model

# NOTE: This is needed when using LiteLLM Proxy Server
#
# # Create OpenAI client for the agent
# openai_client = AsyncOpenAI(
#     base_url = os.getenv('LITELLM_BASE_URL', 'http://localhost:4000'),
#     api_key=os.getenv('LITELLM_API_KEY', 'key')
# )

# # Check if we're using a Qwen model
# is_qwen = "qwen" in model_name.lower()

ctf_agent_system_prompt = load_prompt_template("prompts/system_ctf_agent.md")

api_key = resolve_llm_openai_compatible_api_key(
    model_name,
    allow_placeholder=True,
)

# Get security guardrails for this high-risk agent
input_guardrails, output_guardrails = get_security_guardrails()

one_tool_agent = Agent(
    name="CTF agent",
    description="""Agent focused on conquering security challenges using generic linux commands
                   Expert in cybersecurity and exploitation.""",
    instructions=create_system_prompt_renderer(
        ctf_agent_system_prompt,
        cyber_micro_profile_key="ctf",
    ),
    tools=[
        generic_linux_command,
        nmap_scan,
        http_probe,
        enum_network_surface,
    ],
    input_guardrails=input_guardrails,
    output_guardrails=output_guardrails,
    model=OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=AsyncOpenAI(api_key=api_key),
    ),
)


def transfer_to_one_tool_agent(**kwargs):  # pylint: disable=W0613
    """Transfer to ctf agent.
    Accepts any keyword arguments but ignores them."""
    return one_tool_agent
