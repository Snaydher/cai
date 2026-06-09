"""
CTF Flag Discriminator Agent with test
"""

import os
from cai.sdk.agents import Agent, OpenAIChatCompletionsModel, handoff
from openai import AsyncOpenAI
from cai.agents.one_tool import one_tool_agent
from cai.util import create_system_prompt_renderer, load_prompt_template
from cai.util.llm_api_base import resolve_llm_openai_compatible_api_key

model = os.getenv("CAI_MODEL", "alias1")
effective_model = "alias1" if os.getenv("CAI_MODEL") == "o3-mini" else model
api_key = resolve_llm_openai_compatible_api_key(
    effective_model,
    allow_placeholder=True,
)

_flag_discriminator_prompt = load_prompt_template("prompts/system_flag_discriminator.md")

flag_discriminator = Agent(
    name="Flag discriminator",
    description="Agent focused on extracting the flag from the output",
    instructions=create_system_prompt_renderer(
        _flag_discriminator_prompt,
        cyber_micro_profile_key="flag",
    ),
    model=OpenAIChatCompletionsModel(
        model=effective_model,
        openai_client=AsyncOpenAI(api_key=api_key),
    ),
    handoffs=[
        handoff(
            agent=one_tool_agent,
            tool_name_override="ctf_agent",
            tool_description_override="Call the CTF agent to continue investigating if no flag is found",
        )
    ],
)


# Transfer Function
def transfer_to_flag_discriminator(**kwargs):  # pylint: disable=W0613
    """Transfer flag discriminator.
    Accepts any keyword arguments but ignores them."""
    return flag_discriminator
