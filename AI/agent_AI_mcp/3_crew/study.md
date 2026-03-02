# venv 실행
python3 -m venv venv

source venv/bin/activate  

# venv 강제 실행
.\venv\Scripts\Activate.ps1

# creai 설치
pip install crewai

# 기본 파일 생성
❯ crewai create crew debate

Creating folder debate...
Cache expired or not found. Fetching provider data from the web...
Select a provider to set up:

   1. openai
   2. anthropic
   3. gemini
   4. nvidia_nim
   5. groq
   6. huggingface
   7. ollama
   8. watson
   9. bedrock
   10. azure
   11. cerebras
   12. sambanova
   13. other
       q. Quit
       Enter the number of your choice or 'q' to quit: 1

       Select a model to use for Openai:
   1. gpt-4
   2. gpt-4.1
   3. gpt-4.1-mini-2025-04-14
   4. gpt-4.1-nano-2025-04-14
   5. gpt-4o
   6. gpt-4o-mini
   7. o1-mini
   8. o1-preview
      q. Quit

      Enter the number of your choice or 'q' to quit: 3

      Enter your OPENAI API key (press Enter to skip):
      API keys and model saved to .env file
      Selected model: gpt-4.1-mini-2025-04-14
      - Created debate\.gitignore
      - Created debate\pyproject.toml
      - Created debate\README.md
      - Created debate\knowledge\user_preference.txt
      - Created debate\src\debate\__init__.py
      - Created debate\src\debate\main.py
      - Created debate\src\debate\crew.py
      - Created debate\src\debate\tools\custom_tool.py
      - Created debate\src\debate\tools\__init__.py
      - Created debate\src\debate\config\agents.yaml
      - Created debate\src\debate\config\tasks.yaml
        Crew debate created successfully!

# 실행

crewai run