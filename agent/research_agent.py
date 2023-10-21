import asyncio
import json
import hashlib
import os
from actions.web_search import web_search
from actions.web_scrape import async_browse
from processing.text import \
    write_to_file, \
    create_message, \
    create_chat_completion, \
    read_txt_files, \
    write_md_to_pdf
from config import Config
from agent import prompts
from actions.web_search import web_search
from actions.web_scrape import async_browse
from processing.text import write_to_file, create_message, create_chat_completion, read_txt_files, write_md_to_pdf
from config import Config
from agent import prompts

CFG = Config()

class ResearchAgent:
    def __init__(self, question, agent, agent_role_prompt, websocket=None, use_web=True):
        self.question = question
        self.agent = agent
        self.agent_role_prompt = agent_role_prompt if agent_role_prompt else prompts.generate_agent_role_prompt(agent)
        self.visited_urls = set()
        self.research_summary = ""
        self.dir_path = f"./outputs/{hashlib.sha1(question.encode()).hexdigest()}"
        self.websocket = websocket
        self.use_web = use_web

    async def stream_output(self, output):
        if not self.websocket:
            return print(output)
        await self.websocket.send_json({"type": "logs", "output": output})

    async def summarize(self, text, topic):
        messages = [create_message(text, topic)]
        await self.stream_output(f"📝 Summarizing text for query: {text}")

        return create_chat_completion(
            model=CFG.fast_llm_model,
            messages=messages,
        )

    async def get_new_urls(self, url_set_input):
        new_urls = []
        for url in url_set_input:
            if url not in self.visited_urls:
                await self.stream_output(f"✅ Adding source url to research: {url}\\n")
                self.visited_urls.add(url)
                new_urls.append(url)

        return new_urls

    async def call_agent(self, action, stream=False, websocket=None):
        messages = [{
            "role": "system",
            "content": self.agent_role_prompt
        }, {
            "role": "user",
            "content": action,
        }]
        answer = create_chat_completion(
            model=CFG.smart_llm_model,
            messages=messages,
            stream=stream,
            websocket=websocket,
        )
        return answer

    async def create_search_queries(self):
        result = await self.call_agent(prompts.generate_search_queries_prompt(self.question))
        await self.stream_output(f"🧠 I will conduct my research based on the following queries: {result}...")
        return json.loads(result)

    async def async_search(self, query):
        if self.use_web:
            search_results = json.loads(web_search(query))
            new_search_urls = self.get_new_urls([url.get("href") for url in search_results])

            await self.stream_output(f"🌐 Browsing the following sites for relevant information: {new_search_urls}...")

            tasks = [async_browse(url, query, self.websocket) for url in await new_search_urls]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            return responses
        else:
            return [scrape_uploaded_pdf(query)]

    async def run_search_summary(self, query):
        await self.stream_output(f"🔎 Running research for '{query}'...")

        responses = await self.async_search(query)
        result = "\\n".join(responses)
        os.makedirs(os.path.dirname(f"{self.dir_path}/research-{query}.txt"), exist_ok=True)
        write_to_file(f"{self.dir_path}/research-{query}.txt", result)
        return result

    async def conduct_research(self):
        self.research_summary = read_txt_files(self.dir_path) if os.path.isdir(self.dir_path) else ""

        if not self.research_summary:
            search_queries = await self.create_search_queries()
            for query in search_queries:
                research_result = await self.run_search_summary(query)
                self.research_summary += f"{research_result}\\n\\n"

        await self.stream_output(f"Total research words: {len(self.research_summary.split(' '))}")

        return self.research_summary

    async def create_concepts(self):
        result = self.call_agent(prompts.generate_concepts_prompt(self.question, self.research_summary))

        await self.stream_output(f"I will research based on the following concepts: {result}\\n")
        return json.loads(result)

    async def write_report(self, report_type, websocket=None):
        report_type_func = prompts.get_report_by_type(report_type)
        await self.stream_output(f"✍️ Writing {report_type} for research task: {self.question}...")

        answer = await self.call_agent(report_type_func(self.question, self.research_summary),
                                       stream=websocket is not None, websocket=websocket)
        final_report = await answer if websocket else answer

        path = await write_md_to_pdf(report_type, self.dir_path, final_report)

        return answer, path

    async def write_lessons(self):
        concepts = await self.create_concepts()
        for concept in concepts:
            answer = await self.call_agent(prompts.generate_lesson_prompt(concept), stream=True)
            await write_md_to_pdf("Lesson", self.dir_path, answer)
