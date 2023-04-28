from manyhats.agents.base import AgentMachine


class FantasySportsAgent(AgentMachine):
    name = ("Sports Handicapper",)
    description = (
        """You are a professional sports handicapper and commentator that talks many sports television networks.
You are an expert in the field and have access to any dataset you need to answer any sports and fantasy sports related questions.
You only answer questions related to sports and sports-betting.""",
    )
    goal = ("""Accurately answer questions related to sports and sports-betting.""",)
    task_type = ("question_answering",)
    actions = (
        {
            "data_retrieval": None,
            "calculation": None,
        },
    )  # could also add in memory and context retrieval actions
    # api_stats=[
    #     APIStat(
    #         name="OpenAI",
    #         count=0,
    #         time=0,
    #         sent=0,
    #         received=0,
    #         units="tokens",
    #         cost=0,
    #     ),
    #     APIStat(
    #         name="SERPAPI",
    #         count=0,
    #         time=0,
    #         sent=0,
    #         received=0,
    #         units="kb",
    #         cost=0,
    #     ),
    # ],
