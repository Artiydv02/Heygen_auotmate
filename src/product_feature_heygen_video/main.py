import os
import sys
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from textwrap import dedent

# Apni .env file se saari keys load karna
load_dotenv()

class VideoCrew:
    def __init__(self, video_path, bucket_name):
        self.video_path = video_path
        self.bucket_name = bucket_name
        # Apne tools aur agents ke liye LLM define karna
        try:
            self.llm = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
                api_key=os.getenv("OPENAI_API_KEY")
            )
        except Exception as e:
            print(f"Error initializing OpenAI: {e}")
            print("Please make sure OPENAI_API_KEY is set in your environment or .env file")
            raise

    def run(self):
        # Validate video path
        if not os.path.exists(self.video_path):
            print(f"Error: Video file not found at path: {self.video_path}")
            print("Please provide a valid video file path")
            return "Error: Video file not found"
            
        # Tools ko import karna
        try:
            from product_feature_heygen_video.tools.gcs_tool import GCStorageTool
            from product_feature_heygen_video.tools.heygen_tools import HeyGenVideoTool
            gcs_tool = GCStorageTool()
            heygen_tool = HeyGenVideoTool()
        except Exception as e:
            print(f"Error loading tools: {e}")
            return f"Error loading tools: {e}"

        # Agents ko define karna
        cloud_manager = Agent(
            role='Cloud Operations Specialist',
            goal='Ek local video file ko Google Cloud Storage par surakshit tareeke se upload karna aur uska public URL haasil karna.',
            backstory=dedent("Aap cloud infrastructure ke ek maahir expert hain."),
            tools=[gcs_tool],
            llm=self.llm,
            verbose=True
        )

        vision_analyst = Agent(
            role='Senior Video Scriptwriter',
            goal='Screen recording ke public URL ko "dekhkar" ek engaging script banana jisme visual changes ke hisaab se scene breaks ([NEXT] markers) hon.',
            backstory=dedent("Aap ek anubhavi content strategist hain."),
            llm=self.llm,
            verbose=True
        )

        heygen_producer = Agent(
            role='AI Video Production Specialist',
            goal='Script aur public video URL ka istemal karke HeyGen par ek high-quality portrait video banana. Avatar ko neeche dayein kone mein circular frame mein rakho.',
            backstory=dedent("Aap ek technical video producer hain jise HeyGen API ki gehri samajh hai."),
            tools=[heygen_tool],
            llm=self.llm,
            verbose=True
        )

        # Tasks ko define karna
        upload_task = Task(
            description=f"Local video file jo is path par hai: {self.video_path}, use GCStorageTool ka istemal karke is Google Cloud Storage bucket mein upload karo: {self.bucket_name}.",
            expected_output="Ek string jisme upload ki gayi video ka public URL ho.",
            agent=cloud_manager
        )

        scripting_task = Task(
            description="upload_task se mile public video URL ko analyze karo. Is video mein ho rahe har action ko describe karte hue ek engaging, bolchaal wali Hindi (Romanized) script banao. Jahan bhi video mein ek mahatvapoorna visual change ya naya action ho, wahan ek `[NEXT]` marker lagao.",
            expected_output="Ek poora text (string) jisme script ho aur syncing ke liye `[NEXT]` markers lage hon.",
            context=[upload_task],
            agent=vision_analyst
        )
        
        video_production_task = Task(
            description=f"scripting_task se mili script ka istemal karo. upload_task se mile public video URL ko background ke roop mein istemal karo. Is Avatar ID ('avatar_id_placeholder') aur Voice ID ('voice_id_placeholder') ka istemal karke HeyGenVideoTool ka istemal karke 1080x1920 (Portrait) resolution mein ek final video generate karo.",
            expected_output="Ek safal sandesh jisme HeyGen par host ki gayi final video ka URL ho.",
            context=[scripting_task, upload_task],
            agent=heygen_producer
        )

        # Crew ko assemble karke kaam shuru karna
        try:
            crew = Crew(
                agents=[cloud_manager, vision_analyst, heygen_producer],
                tasks=[upload_task, scripting_task, video_production_task],
                process=Process.sequential,
                verbose=True
            )

            result = crew.kickoff()
            return result
        except Exception as e:
            error_msg = f"An error occurred while running the crew: {str(e)}"
            print(error_msg)
            return error_msg

def run():
    print("## Aapki Fully Automated AI Video Crew Taiyar Hai! ##")
    print('----------------------------------------------------')
    
    try:
        local_video_file_path = input("Apni screen recording video file ka poora local path yahan paste karein: ")
        # Validate video path
        if not os.path.exists(local_video_file_path):
            print(f"Error: Video file not found at path: {local_video_file_path}")
            print("Please provide a valid video file path")
            return
            
        gcs_bucket_name = input("Apne Google Cloud Storage bucket ka naam yahan paste karein: ")
        
        video_crew = VideoCrew(local_video_file_path, gcs_bucket_name)
        crew_result = video_crew.run()
        
        print("\n\n########################")
        print("## Crew ka kaam poora hua! ##")
        print("########################\n")
        print("Final Result:")
        print(crew_result)
        return crew_result
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    run()
