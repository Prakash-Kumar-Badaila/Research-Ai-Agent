# -*- coding: utf-8 -*-
"""
Converted from IPYNB to PY
"""

# %% [code] Cell 1
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.types import Send
from typing import TypedDict, Annotated, Literal, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.types import Send
import operator
from pathlib import Path
from langgraph.graph import StateGraph, START, END
import requests
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from bs4 import BeautifulSoup
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

# %% [code] Cell 2
load_dotenv()

# %% [code] Cell 3
class ResearchStructure(BaseModel):
    research_needed : bool = Field(default= False, description= "Tell internet research is need or not, False if model can generate answer on its own by parametric knowlege true if model needs to do some research")
    queries : list[str] = Field(default= None, description="If model needs to do some research, list of all queries that needs to be sent to a search engine to get the knowledege required  for an LLM to write blog")

# %% [code] Cell 4
class Evidence(BaseModel):
    id : int
    title : str
    url : str = Field(description="Url from where you got the information")
    content : str = Field(description= "Actual content of the research")
    published_date :Optional[str] = Field(description= "Date of contain")
    

# %% [code] Cell 5
class EvidencePack(BaseModel):
    evidences : list[Evidence]

# %% [code] Cell 6
class Task(BaseModel):
    id : int
    section_head : str = Field(description="Name of the section")
    section_desc : str = Field(description= "Description of what to include in that section ")

# %% [code] Cell 7
class Plan(BaseModel):
    plans : list[Task]

# %% [code] Cell 8
class BlogState(TypedDict):
    topic : str
    research_needed  : bool
    research_queries : list[str]
    plans : Plan
    sections : Annotated[list[str],operator.add]
    final : str
    evidences : EvidencePack

# %% [code] Cell 9
model = ChatOllama(model = 'qwen2.5:7b')
resarch_check_model = model.with_structured_output(ResearchStructure)
evidence_model = model.with_structured_output(EvidencePack)
planner_model = model.with_structured_output(Plan)

# %% [code] Cell 10
search_tool = TavilySearchResults(max_results= 8)

# %% [code] Cell 11
@tool
def deep_research(query):
    """
    Use this tool when you don't know any topic or know very little about that topic and want to do a deep research about that
    """
    outputs = []
    out = search_tool.invoke(query)

 
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}

    for item in out:
        content  = requests.get(item['url'], headers= headers)
        soup = BeautifulSoup(content.text, "html.parser")

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
            tag.decompose()

        # Extract clean text
        text = soup.get_text(separator="\n", strip=True)

        outputs.append(text)

    return outputs


    

# %% [code] Cell 12
writer_model = model


# %% [code] Cell 13
def research_checker(state : BlogState):

    output = resarch_check_model.invoke([SystemMessage(content= "A same LLM like you is going to write a blog, You are a research check model , You check whether the LLM can write blog on its own or it needs some research from the internet. If the topic is not latest enough or already availabe in LLM paramteric knowledge you return False, but if that knowledge is not available in LLM parametric knowledge you return True and also return a set of search queries that LLM can search in a search engine to know a lot of knowledge to write a good blog, You return best queries that LLM can use to generate answer"), HumanMessage(content = f"Your topic is {state['topic']} check whether you need to do resarch or not if yes also list of best queries , Note: Only say research is needed if that information is not stored in your parametric knowledge") ])

    return {
        'research_needed' : output.research_needed,
        'research_queries' : output.queries,
    }

# %% [code] Cell 14
def router(state : BlogState):
    return 'internet_searcher' if state['research_needed'] else 'planner'

# %% [code] Cell 15
def internet_searcher(state : BlogState):
    items  = []
    for item in state['research_queries']:
        items.append(search_tool.invoke(item))

    print(items)

    SYSTEM_PROMPT = "You are an AI model which converts unstructured Internet research to structured_format with same content"

    result =  evidence_model.invoke([SystemMessage(content = SYSTEM_PROMPT), HumanMessage(content = f"Convert this unstructued content to structured, make sure that there is no information Loss  {items}")])
    return {
        'evidences' : result
    }

# %% [code] Cell 16
def planner(state: BlogState):
    SYSTEM_PROMPT = """
    You are an AI model that generates blog sections.
    Consider any available research evidence.
    """

    evidences = state.get("evidences", "not available")

    result = planner_model.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"""
Generate plans for topic:
{state['topic']}

Research:
{evidences}
"""
        )
    ])

    return {"plans": result}

# %% [code] Cell 17
# result = research_checker({
#     'topic' : "New advancements in ai in 2026"
# })

# %% [code] Cell 18
# result

# %% [code] Cell 19
# result = internet_searcher({
#     'research_queries': ['New advancements in AI in 2026',
#   'AI breakthroughs and trends for 2026',
#   'Future developments in artificial intelligence 2026',
#   'Predictions for AI technology in 2026',
#   'Upcoming innovations in AI by 2026']
# })

# %% [code] Cell 20
# result

# %% [code] Cell 21
# result = planner({
#     'topic' : "New advancements in ai in 2026",
#     'evidences' : result
# })

# %% [code] Cell 22
# result['plans'].plans

# %% [code] Cell 23
def fanout(state: BlogState):
    return ([Send("worker", {'task' : task, 'topic' : state['topic'], 'plans' : state['plans']})
             for task in state['plans'].plans])

# %% [code] Cell 24
# def fanout(state: BlogState):
#     # return ([Send("worker", {'task' : task, 'topic' : state['topic'], 'plan' : state['plans']})
#              for task in state['plans'].task])

# %% [code] Cell 25
def worker(payload : dict):
    task = payload['task']
    topic = payload['topic']
    plan = payload['plans']


    result = model.invoke([SystemMessage(content= "Write one clean markdown section for each topic"),
                           HumanMessage(content= 
                                        f"topic : {topic}"
                                        f"task {task.section_head}" 
                                        f"descroption = {task.section_desc}"
                                        f"Full plan : {plan}"
                                        "Write just one markdown section for the task"
                                        )
                           
                           ])
    

    return {"sections" : [result.content]}

# %% [code] Cell 26
# each_result = worker({
#     'task' : Task(id=1, section_head='Introduction to Key Predictions in 2026', section_desc='Provide a brief introduction to the main predictions and trends for AI in 2026, citing key evidence sources. This section will set the stage for further detailed discussion.'),
#     'topic' : " New advancements in ai in 2026",
#     'plans' :result
    

# })

# %% [code] Cell 27
def reducer(state : BlogState):
        title = state['topic']
        body = '\n\n'.join(state['sections']).strip()
        body  = model.invoke(f"Refine this markdown and make it look professional, structure this content and make sure that it looks like it is written by a proffesional\n {body}").content
        final_md  = f"#{title} \n\n{body}\n"

        file_name = title.lower().replace(" ", "_") + ".md"
        output_path = Path(file_name)
        output_path.write_text(final_md, encoding= 'utf-8')
        return {'final' : final_md}
        
        

# %% [code] Cell 28
graph = StateGraph(BlogState)
graph.add_node('research_checker', research_checker)
graph.add_node('researcher', internet_searcher)
graph.add_node('planner', planner)
graph.add_node('worker', worker)
graph.add_node('reducer', reducer)


# %% [code] Cell 29

graph.add_edge(START, 'research_checker')
graph.add_conditional_edges('research_checker', router, {'internet_searcher': 'researcher', 'planner' : 'planner'})
graph.add_edge('researcher', 'planner')
graph.add_conditional_edges('planner', fanout, ['worker'])
graph.add_edge('worker', 'reducer')

graph.add_edge('reducer',END )

# %% [code] Cell 30
app = graph.compile()

# %% [code] Cell 31
# app

# %% [code] Cell 32
@tool
def researcher(topic):
    """
        Give research topic and it generates blog in markdown file on your folder

    """
    app.invoke({'topic' : topic})

# %% [code] Cell 33
class BaseState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]

# %% [code] Cell 35
all_tools = [deep_research, researcher]
base_model = model.bind_tools(all_tools)


# %% [code] Cell 36
def chat_model(state):
    response = base_model.invoke(state['messages'])
    return {'messages' : [response]}

# %% [code] Cell 37
base_graph = StateGraph(BaseState)

# %% [code] Cell 38
base_graph.add_node('chat_model', chat_model)

# %% [code] Cell 39
base_graph.add_node('tools', ToolNode(all_tools))

# %% [code] Cell 40
base_graph.add_edge(START, 'chat_model')
base_graph.add_conditional_edges('chat_model', tools_condition)
base_graph.add_edge('tools', 'chat_model')
base_graph.add_edge('chat_model', END)

# %% [code] Cell 41
checkpointer = InMemorySaver()
config = {'configurable' : {'thread_id' : "1"}}

# %% [code] Cell 42
final_model = base_graph.compile(checkpointer=checkpointer)

# %% [code] Cell 43
# final_model

# %% [code] Cell 44

def generate_response(query):
    for message, metadata in final_model.stream(
        {'messages': [HumanMessage(content=query)]},
        stream_mode='messages',
        config=config
    ):
        if message.content:
            yield message.content