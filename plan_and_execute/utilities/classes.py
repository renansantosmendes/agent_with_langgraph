from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi

from entities.prompts import SUMMARIZER_PROMPT

from langchain_openai.chat_models import ChatOpenAI

load_dotenv()


class VideoSummarizer:
    def __init__(self, query):
        self.query = query
        self.prompt = SUMMARIZER_PROMPT
        self.llm =  ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
        self.template = ChatPromptTemplate.from_messages(
            ("system", self.prompt)
        )
        self.chain = self.template | self.llm

    def summarize_video(self, video_id=None) -> str:
        if video_id:
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id=video_id)
            data = [transcript for transcript in transcripts]
            print(data)
            transcription = ' '.join([part.get('text') for part in data[0].fetch()])
            summary = self.chain.invoke({
                "transcription": transcription
            })
            print(summary)
            return summary
        else:
            return ""


if __name__ == '__main__':
    vs = VideoSummarizer('DeepSeek')
    print(vs.summarize_video('3MRR4UNiKwE'))