import re
import ast
import logging
from dotenv import load_dotenv
from langchain_community.tools import YouTubeSearchTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from youtube_transcript_api import YouTubeTranscriptApi

from entities.prompts import SUMMARIZER_PROMPT, META_SUMMARIZER_PROMPT

from langchain_openai.chat_models import ChatOpenAI

load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

class VideoSummarizer:
    def __init__(self, query: str=None) -> None:
        self.query = query

    @staticmethod
    def _get_summarizer_chain(prompt=SUMMARIZER_PROMPT) -> Runnable:
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
        template = ChatPromptTemplate.from_messages(
            ("system", prompt)
        )
        return template | llm

    @staticmethod
    def extract_video_ids(urls) -> list[str]:
        pattern = r'v=([^"]+?)&pp='
        return [re.search(pattern, url).group(1) for url in urls if re.search(pattern, url)]

    def summarize_video(self, video_id=None) -> str:
        if video_id:
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id=video_id)
            data = [transcript for transcript in transcripts]
            transcription = ' '.join([part.get('text') for part in data[0].fetch()])
            summary = self._get_summarizer_chain().invoke({
                "transcription": transcription
            })
            return summary.content
        else:
            raw_urls = YouTubeSearchTool().run(self.query)
            video_ids = self.extract_video_ids(ast.literal_eval(raw_urls))
            summaries_list = [self.summarize_video(video_id) for video_id in video_ids]
            summaries = '\n\n####### Resumo ####### \n'.join(summaries_list)
            summary = self._get_summarizer_chain(META_SUMMARIZER_PROMPT).invoke({
                "summaries": summaries
            })
            return summary.content


if __name__ == '__main__':
    vs = VideoSummarizer('langchain')
    print(vs.summarize_video())