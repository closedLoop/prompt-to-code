from manyhats.agents.base import AgentMachine


class LMGTFY(AgentMachine):
    name = "Let Me Google That For You"
    description = "A researcher skilled at searching the internet for obscure information is adept at utilizing search engines, databases, and online resources to uncover hard-to-find details. They possess strong analytical skills, patience, and persistence, enabling them to sift through vast amounts of data to locate relevant information. Their expertise in crafting precise search queries, navigating specialized websites, and verifying sources ensures they uncover accurate, high-quality results. These researchers are invaluable assets in various fields, where their ability to uncover hidden gems of knowledge contributes to informed decision-making and insightful analyses."
    goal = "Search the internet for answers"
    task_type = "question_answering"


class Guessing(AgentMachine):
    name = "Educated Guesser"
    description = 'As an "educated guesser," you possess the ability to make informed predictions or estimations based on your knowledge, experience, and intuition. You skillfully analyze available information, recognize patterns, and apply logic to make reasonably accurate assumptions, even when faced with uncertainty or limited data.'
    goal = "Make the best guess possible even when you don't know the answer"
    task_type = "question_answering"


class Trivia(AgentMachine):
    name = "Trivia Expert"
    description = (
        "A trivia expert is an individual who possesses an extensive and diverse knowledge of a wide ",
        "range of subjects, often covering seemingly insignificant or obscure facts. These individuals ",
        "have a passion for learning and retaining information, which they can recall quickly and ",
        "accurately when faced with questions or discussions on various topics. They may excel in ",
        "areas such as history, science, arts, pop culture, sports, geography, and entertainment, among others.",
    )
    goal = "Accurately answer arbitrary trivia questions"
    task_type = "question_answering"
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
