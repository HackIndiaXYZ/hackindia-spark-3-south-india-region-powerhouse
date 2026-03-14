import sys
import os
from dotenv import load_dotenv
import time

# Ensure the parent's parent folder is in path so we can import 'models'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from langchain_core.tools import tool
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate

# Try different import approaches for create_react_agent
try:
    from langchain.agents import AgentExecutor, create_react_agent
    USING_LANGGRAPH = False
except ImportError:
    try:
        from langchain_community.agents import AgentExecutor, create_react_agent
        USING_LANGGRAPH = False
    except ImportError:
        try:
            # Import the newer LangGraph version
            from langgraph.prebuilt import create_react_agent
            USING_LANGGRAPH = True
        except ImportError:
            raise ImportError("Could not import create_react_agent from any available package")

# Load environment variables (e.g., GOOGLE_GEMINI_API_KEY, MONGO_URI)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# Import connection utilities
try:
    from utils.connection_utils import retry_on_connection_error, is_windows_connection_error
except ImportError:
    # Fallback if utils not available
    def retry_on_connection_error(max_retries=3, delay=1.0, backoff=2.0):
        def decorator(func):
            return func
        return decorator
    
    def is_windows_connection_error(error):
        return "10054" in str(error) or "forcibly closed" in str(error)

# Import the database query functions from our student model
from models.student_model import get_all_students_with_marks, get_student_by_id, get_student_by_email
from agents.answerKeyAgent.answerKeyAgent import answerKeyAgent
from agents.questionPaperGeneratorAgent.questionPaperGenerator import QuestionPaperGenerator

# ==========================================
# 1. Define Tools
# ==========================================
@tool
@retry_on_connection_error(max_retries=3, delay=2.0, backoff=2.0)
def generate_question_paper(content: str):
    """
    Generates a question paper based on the given content or topic.
    This tool may take 30-60 seconds to complete. Please be patient.
    
    Args:
        content: The topic or subject for which to generate questions (e.g., "machine learning ensemble learning")
    
    Returns:
        A list of questions in JSON format with question_number, question, marks, type, and options (for MCQs)
    """
    print("\n⏳ Generating question paper... This may take a minute.")
    try:
        questionPaperGenerator = QuestionPaperGenerator()
        result = questionPaperGenerator.demoQuestionpaperGenerator(content, None)
        print("✅ Question paper generated successfully!")
        return result
    except Exception as e:
        if is_windows_connection_error(e):
            error_msg = f"Windows connection error during question paper generation: {str(e)}"
            print(f"❌ {error_msg}")
            raise ConnectionError("Question paper generation failed due to connection issues. Please try again.")
        else:
            error_msg = f"Error generating question paper: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

@tool
@retry_on_connection_error(max_retries=3, delay=2.0, backoff=2.0)
def direct_answer_key(questionPaper: list):
    """
    Generates an answer key for the provided list of questions in the question paper.
    This tool may take 30-60 seconds to complete. Please be patient.
    
    Args:
        questionPaper: A list of question dictionaries with structure:
            [{"question_number": int, "question": str, "marks": int, "type": str, "options": list}]
    
    Returns:
        An answer key with solutions for each question
    """
    print("\n⏳ Generating answer key... This may take a minute.")
    try:
        answer_key_agent = answerKeyAgent()
        result = answer_key_agent.directAnswerKey(questionPaper)
        print("✅ Answer key generated successfully!")
        return result
    except Exception as e:
        if is_windows_connection_error(e):
            error_msg = f"Windows connection error during answer key generation: {str(e)}"
            print(f"❌ {error_msg}")
            raise ConnectionError("Answer key generation failed due to connection issues. Please try again.")
        else:
            error_msg = f"Error generating answer key: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

# @tool
# def fetch_all_students_with_marks() -> list:
#     """Fetches all students and joins them with their corresponding marks."""
#     return get_all_students_with_marks()

# @tool
# def fetch_student_by_id(student_id: str) -> dict:
#     """Fetches a single student by their ObjectId and includes their marks."""
#     return get_student_by_id(student_id)

# @tool
# def fetch_student_by_email(email: str) -> dict:
#     """Fetches a single student by their email address and includes their marks."""
#     return get_student_by_email(email)

# List of tools available to the agent. Add more tools to this list later as needed.
tools = [generate_question_paper, direct_answer_key]

# ==========================================
# 2. Initialize LLM
# ==========================================

# Using NVIDIA Llama 3.3 70B - better for tool calling and reasoning
nvidia_api_key = os.getenv("nvidiaKey1") or os.getenv("nvidiakey1")
if not nvidia_api_key:
    raise ValueError("❌ NVIDIA API key not found. Please set 'nvidiaKey1' in your .env file.")

os.environ["NVIDIA_API_KEY"] = nvidia_api_key

# Using Llama 3.3 70B for better tool support and reliability
llm = ChatNVIDIA(
    model="meta/llama-3.3-70b-instruct",
    temperature=0.7,
    max_completion_tokens=4096,  # Updated parameter name
    timeout=120  # This will go to model_kwargs automatically
)


# ==========================================
# 3. Create Agent
# ==========================================

# Check if we're using LangGraph or traditional LangChain
if USING_LANGGRAPH:
    # LangGraph approach - simplified for v1.0+
    # LangGraph v1.0+ may not support system messages in create_react_agent
    agent_executor = create_react_agent(llm, tools)
    
else:
    # Traditional LangChain approach
    system_prompt_template = """You are an intelligent teaching assistant designed to help teachers with their daily tasks.

Your primary capabilities:
1. Generate question papers on any topic or subject
2. Create answer keys for question papers
3. Provide helpful educational assistance

Important guidelines:
- When teachers request question papers or answer keys, use the appropriate tools
- These tools may take 30-60 seconds to complete - inform the user and be patient
- Always display the complete tool output to the user in a clear, readable format
- If a tool returns JSON data, present it in a well-formatted way
- Be friendly, professional, and supportive
- If an error occurs, explain it clearly and suggest alternatives

When using the `direct_answer_key` tool, ensure the input `questionPaper` is a list formatted like:
[
    {{
        "question_number": <number>,
        "question": "<text of the question>",
        "marks": <integer>,
        "type": "<'MCQ' or 'Descriptive'>",
        "options": ["A) ...", "B) ...", "C) ...", "D) ..."]  // only if MCQ
    }}
]

Always present tool results clearly to help teachers use them effectively.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

    prompt = PromptTemplate.from_template(system_prompt_template)
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# ==========================================
# 4. Chat Interface
# ==========================================

def format_output(content):
    """Format tool outputs for better readability"""
    import json
    
    if isinstance(content, str):
        # Try to parse as JSON for better formatting
        try:
            data = json.loads(content)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except:
            return content
    elif isinstance(content, (list, dict)):
        return json.dumps(content, indent=2, ensure_ascii=False)
    return str(content)

def chat_interface():
    print("\n" + "="*70)
    print("🎓 Teacher Assistant Chatbot")
    print("="*70)
    print("\nI'm here to help you with:")
    print("  • Generating question papers on any topic")
    print("  • Creating answer keys for your questions")
    print("  • General educational assistance")
    print("\nNote: Question paper and answer key generation may take 30-60 seconds.")
    print("\nType 'quit' or 'exit' to stop.")
    print("-" * 70)
    
    while True:
        try:
            user_input = input("\n👨‍🏫 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Have a great day teaching!")
                break
                
            if not user_input:
                continue
            
            # Prepare inputs for the agent
            if USING_LANGGRAPH:
                # LangGraph expects messages format
                # Add system message as the first message
                system_msg = ("system", """You are an intelligent teaching assistant designed to help teachers with their daily tasks.

Your primary capabilities:
1. Generate question papers on any topic or subject
2. Create answer keys for question papers
3. Provide helpful educational assistance

Important guidelines:
- When teachers request question papers or answer keys, use the appropriate tools
- These tools may take 30-60 seconds to complete - inform the user and be patient
- Always display the complete tool output to the user in a clear, readable format
- If a tool returns JSON data, present it in a well-formatted way
- Be friendly, professional, and supportive
- If an error occurs, explain it clearly and suggest alternatives

When using the `direct_answer_key` tool, ensure the input `questionPaper` is a list formatted like:
[
    {
        "question_number": <number>,
        "question": "<text of the question>",
        "marks": <integer>,
        "type": "<'MCQ' or 'Descriptive'>",
        "options": ["A) ...", "B) ...", "C) ...", "D) ..."]  // only if MCQ
    }
]

Always present tool results clearly to help teachers use them effectively.""")
                
                inputs = {"messages": [system_msg, ("user", user_input)]}
            else:
                # Traditional LangChain expects input format
                inputs = {"input": user_input}
            
            print("\n🤔 Processing your request...")
            
            # Invoke the agent with retry logic for connection errors
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    response = agent_executor.invoke(inputs)
                    break
                except Exception as e:
                    error_str = str(e)
                    if "Connection" in error_str or "10054" in error_str or "aborted" in error_str:
                        if attempt < max_retries - 1:
                            print(f"\n⚠️  Connection issue detected. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            raise Exception("Connection failed after multiple retries. Please check your internet connection and try again.")
                    else:
                        raise
            
            # Extract the final AI response
            if USING_LANGGRAPH:
                # LangGraph returns messages
                final_message = response["messages"][-1].content if response.get("messages") else "No response generated"
            else:
                # Traditional LangChain returns output
                final_message = response.get("output", "No response generated")
            
            # Display the response
            print("\n" + "="*70)
            print("🤖 Assistant:")
            print("-" * 70)
            
            # Format if it looks like structured data
            formatted_content = format_output(final_message)
            print(formatted_content)
            
            print("="*70)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Have a great day teaching!")
            break
            
        except Exception as e:
            error_msg = str(e)
            print("\n" + "="*70)
            print("❌ Error occurred:")
            print("-" * 70)
            
            if "Connection" in error_msg or "10054" in error_msg:
                print("Connection error: The remote server closed the connection.")
                print("\nPossible solutions:")
                print("  1. Check your internet connection")
                print("  2. Verify your NVIDIA API key is valid")
                print("  3. Try again in a few moments")
                print("  4. Check if there are firewall/proxy restrictions")
            elif "rate limit" in error_msg.lower():
                print("Rate limit reached. Please wait a moment before trying again.")
            elif "timeout" in error_msg.lower():
                print("Request timed out. The operation took too long.")
                print("This can happen with complex requests. Try simplifying your request.")
            else:
                print(f"{error_msg}")
                print("\nIf the problem persists, please check your configuration.")
            
            print("="*70)
            
            # Don't add failed messages to history
            pass

if __name__ == "__main__":
    try:
        chat_interface()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("Please check your .env file and ensure all required API keys are set.")
