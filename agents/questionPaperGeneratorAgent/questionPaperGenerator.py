from langchain_text_splitters import RecursiveCharacterTextSplitter
from tools.webSearcher.scrapers import *
import pdfplumber
from services.prompt.promptProcessor import dataProcessor
from ragSystems.ragProcessor import HybridRagProcessor
import concurrent.futures
import logging
import os
from collections import defaultdict
from threading import Lock
from data.events import emit
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor,as_completed
from itertools import repeat

try:
    from keybert import KeyBERT
except ImportError:
    KeyBERT = None

load_dotenv()

# Global model cache
_kw_model = None


# event_store = defaultdict(list)
# lock = Lock()

# def emit(task_id: str, msg: str):
#     with lock:
#         event_store[task_id].append({
#             "msg": msg
#         })

# ============================================================================
# STANDALONE WORKER FUNCTIONS FOR PROCESSPOOL EXECUTOR
# These functions are defined at module level so they can be pickled
# ============================================================================

def _worker_content_extractor(element_data):
    """
    Standalone worker function for ProcessPoolExecutor.
    Extracts content for a single element using web scrapers.
    
    Args:
        element_data: Tuple of (element, collection_name, data_processor_config)
    
    Returns:
        Updated element with scraped content
    """
    element, collection_name = element_data
    
    # Import here to avoid pickling issues
    from services.prompt.promptProcessor import dataProcessor
    from ragSystems.ragProcessor import HybridRagProcessor
    
    # Create fresh instances for this process
    data_processor = dataProcessor()
    rag_system = HybridRagProcessor(collection_name)
    
    # Scraper mapping
    scraper_map = {
        "NCERTScraper": NCERTScraper,
        "CBSEScraper": CBSEScraper,
        "DIKSHAScraper": DIKSHAScraper,
        "NROERScraper": NROERScraper,
        "OfficialDocsScraper": OfficialDocsScraper,
        "WikipediaScraper": WikipediaScraper,
        "W3SchoolsScraper": W3SchoolsScraper,
        "GeeksForGeeksScraper": GeeksForGeeksScraper,
        "NPTELScraper": NPTELScraper,
        "MITOCWScraper": MITOCWScraper,
        "OpenStaxScraper": OpenStaxScraper,
        "UniversityEDUScraper": UniversityEDUScraper
    }
    
    # Get tool selection plans for each topic
    plans_list = []
    for topic in element.get("topics", []):
        tool_selector = data_processor.webSearchSelector(f"{element['co']} {element['po']}", topic)
        # Ensure tool_selector is a dictionary before accessing with .get()
        if isinstance(tool_selector, dict):
            print(tool_selector)
            plans = tool_selector.get("plans", tool_selector.get("plan", []))
            if plans:
                plans_list.extend(plans)
        else:
            # Log unexpected response type for debugging
            print(f"Warning: tool_selector returned non-dict type: {type(tool_selector)}, value: {tool_selector}")
    
    extracted_content = ""
    seen_content = set()
    element["scraped_data"] = []
    
    # Execute each plan
    for plan in plans_list:
        tool_name = plan.get("tool")
        query = plan.get("query")
        
        if tool_name in scraper_map:
            scraper_class = scraper_map[tool_name]
            scraper = scraper_class()
            
            try:
                result = scraper.fetch(query)
                scraped_text = result.get('content', '')
                
                if scraped_text and scraped_text not in seen_content:
                    seen_content.add(scraped_text)
                    extracted_content += f"Content:\n{scraped_text}\n"
                    
                    # Extract topics
                    raw_topic = result.get('topic', [])
                    if isinstance(raw_topic, str):
                        raw_topic = [raw_topic]
                    
                    # Add KeyBERT topics
                    raw_topic.extend(scraper._extract_additional_topics(scraped_text))
                    
                    # Filter topics
                    topics_list = data_processor.extractTopics(raw_topic, f"{element['co']+element['po']}")
                    
                    if isinstance(topics_list, list):
                        element["scraped_data"].extend(topics_list)
                    elif topics_list:
                        element["scraped_data"].append(str(topics_list))
                        
            except Exception as e:
                pass  # Silent fail for individual scrapers
    
    # Deduplicate topics
    if element["scraped_data"]:
        element["scraped_data"] = list(set(element["scraped_data"]))
        element["topics"].extend(element["scraped_data"])
        del element["scraped_data"]
    
    # Store content in RAG system
    if extracted_content:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_text(extracted_content)
        
        metadata_list = []
        for chunk in chunks:
            metadata_list.append({"CO": element["co"], "text": chunk})
        
        rag_system.process_and_store(chunks=chunks, metadata=metadata_list)
    
    return element


def _worker_rag_retrieval(questions_data):
    """
    Standalone worker function for RAG-based question enhancement.
    Logs all search queries and results to a file for debugging.
    
    Args:
        questions_data: Tuple of (questions, element, collection_name)
    
    Returns:
        Dictionary with enhanced questions
    """
    import os
    from datetime import datetime
    from threading import Lock
    
    questions, element, collection_name = questions_data
    
    # FIX: Ensure questions is always a list to prevent character iteration
    if isinstance(questions, str):
        # If questions is a string, wrap it in a list
        questions = [questions]
    elif not isinstance(questions, list):
        # If it's neither string nor list, convert to list
        questions = list(questions) if questions else []
    
    # Import here to avoid pickling issues
    from services.prompt.promptProcessor import dataProcessor
    from ragSystems.ragProcessor import HybridRagProcessor
    
    data_processor = dataProcessor()
    rag_system = HybridRagProcessor(collection_name)
    
    questions_dict = {
        "CO": element["co"],
        "PO": element["po"],
        "topics": element["topics"],
        "questions": []
    }
    
    # Create logs directory if it doesn't exist
    log_dir = "rag_search_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"rag_queries_{timestamp}.txt")
    
    # Thread-safe file writing lock (shared across threads in this process)
    file_lock = Lock()
    
    def log_search_query(question, retrieval_result, enhanced_questions):
        """Thread-safe logging of search queries and results"""
        try:
            with file_lock:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"CO: {questions_dict['CO']}\n")
                    f.write(f"PO: {questions_dict['PO']}\n")
                    f.write(f"SEARCH QUERY: {question}\n")
                    f.write("-" * 80 + "\n")
                    
                    if retrieval_result:
                        f.write(f"RETRIEVED RESULTS ({len(retrieval_result)} items):\n")
                        for idx, data in enumerate(retrieval_result, 1):
                            f.write(f"\n  Result {idx}:\n")
                            f.write(f"    Text: {data.get('text', 'N/A')[:200]}...\n")
                            if 'score' in data:
                                f.write(f"    Score: {data['score']}\n")
                    else:
                        f.write("RETRIEVED RESULTS: None (no content found)\n")
                    
                    f.write("-" * 80 + "\n")
                    f.write(f"ENHANCED QUESTIONS:\n")
                    if isinstance(enhanced_questions, list):
                        for idx, q in enumerate(enhanced_questions, 1):
                            f.write(f"  {idx}. {q}\n")
                    elif isinstance(enhanced_questions, str):
                        f.write(f"  1. {enhanced_questions}\n")
                    else:
                        f.write(f"  Type: {type(enhanced_questions)}, Value: {enhanced_questions}\n")
                    
                    f.write("=" * 80 + "\n\n")
        except Exception as e:
            print(f"Warning: Failed to log search query: {e}")
    
    def multiThreadedRetriever(question):
        """Process a single question with RAG retrieval and enhancement"""
        try:
            # Perform RAG search
            retrieval_result = rag_system.search(query=question)
            input_text = [data["text"] for data in retrieval_result]
            
            # Fallback if no content found
            if not input_text:
                input_text = [
                    question, 
                    "no content found create question on your own but dont add irrelavent questions"
                ]
            
            # Enhance questions using retrieved content
            enhanced_questions = data_processor.questionEnhancer(
                input_text,
                reference=f"{questions_dict['CO']}+ {questions_dict['PO']} + {question}"
            )
            
            # Log the search query and results
            log_search_query(question, retrieval_result, enhanced_questions)
            
            # Normalize output to list
            result_questions = []
            if isinstance(enhanced_questions, str):
                result_questions.append(enhanced_questions)
            elif isinstance(enhanced_questions, list):
                result_questions.extend(enhanced_questions)
            
            return result_questions
            
        except Exception as e:
            print(f"Error processing question '{question}': {e}")
            # Log the error
            try:
                with file_lock:
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"ERROR: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Question: {question}\n")
                        f.write(f"Error: {str(e)}\n\n")
            except:
                pass
            return []
    
    # Process all questions in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=15) as executor:
        finalQuestions = list(executor.map(multiThreadedRetriever, questions))
    
    # Flatten the list of lists
    questions_dict["questions"] = [q for subList in finalQuestions for q in subList]
    
    # Write summary to log file
    try:
        with file_lock:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write("SUMMARY\n")
                f.write("=" * 80 + "\n")
                f.write(f"Total base questions processed: {len(questions)}\n")
                f.write(f"Total enhanced questions generated: {len(questions_dict['questions'])}\n")
                f.write(f"CO: {questions_dict['CO']}\n")
                f.write(f"PO: {questions_dict['PO']}\n")
                f.write("=" * 80 + "\n\n")
    except Exception as e:
        print(f"Warning: Failed to write summary: {e}")
    
    return questions_dict


def get_kw_model():
    global _kw_model
    if _kw_model is None and KeyBERT is not None:
        try:
             # Use a smaller model for speed
            _kw_model = KeyBERT('all-MiniLM-L6-v2')
        except Exception as e:
            pass
    return _kw_model
def _extract_additional_topics(self, content: str) -> list:
        """Extracts keywords/topics from content using KeyBERT with safe chunking and multi-threading."""
        return []
        # kw_model = get_kw_model()
        # if not kw_model or not content:
        #     return []

        # try:
        #     # -------- Chunk into ~400-word blocks --------
        #     words = content.split()
        #     chunk_size = 400
        #     chunks = [
        #         " ".join(words[i:i + chunk_size])
        #         for i in range(0, len(words), chunk_size)
        #     ]

        #     all_keywords = []

        #     def process_chunk(chunk):
        #         try:
        #             keywords = kw_model.extract_keywords(
        #                 chunk,
        #                 keyphrase_ngram_range=(1, 2),  # 1–2 word topics
        #                 stop_words='english',
        #                 top_n=5                         # topics per chunk
        #             )
        #             return [kw[0] for kw in keywords]
        #         except Exception:
        #             return []

        #     # Use ThreadPoolExecutor for parallel processing
        #     # Using threads because KeyBERT/PyTorch might release GIL for heavy ops
        #     max_workers = os.cpu_count() or 4
        #     with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        #         results = list(executor.map(process_chunk, chunks))
            
        #     for res in results:
        #         all_keywords.extend(res)

        #     # -------- Deduplicate while keeping order --------
        #     seen = set()
        #     unique_topics = []
        #     for kw in all_keywords:
        #         kw_lower = kw.lower()
        #         if kw_lower not in seen:
        #             seen.add(kw_lower)
        #             unique_topics.append(kw)

        #     return unique_topics

        # except Exception as e:
        #     # print(f"KeyBERT extraction failed: {e}") # Keeping clean logs
        #     return []


class QuestionPaperGenerator():
    def __init__(self,collectionName="default_collection"):
        # Store collection name for emit calls
        self.collectionName = collectionName
        
        # Setup logging
        logging.basicConfig(
            filename='agent.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing QuestionPaperGenerator Agent...")
        
        emit(task_id=collectionName, msg="🚀 Initializing Question Paper Generator...")

        self.currentQuestionPaper = []
        self.currentContent = []
        
        # Thread lock for thread-safe operations
        self.data_lock = Lock()
        
        emit(task_id=collectionName, msg="📊 Loading data processor...")
        self.dataProcessor = dataProcessor()
        
        emit(task_id=collectionName, msg="🔍 Initializing RAG system...")
        self.ragSystem = HybridRagProcessor(collectionName)
        
        emit(task_id=collectionName, msg="✅ Question Paper Generator initialized successfully!")
        
        self.mainMemory = {
            "toolMemory" : [],
            "questionMemory" : set(),
            "stepReasoning" : []
        }
        self.chatMemory = []
        return

    def hierarchicalDataCreator(self,text,filePath):
        emit(task_id=self.collectionName, msg="📝 Creating hierarchical structure from input text...")
        
        hierarchyJson = self.dataProcessor.hierarchicalDataCreator(text)
        emit(task_id=self.collectionName, msg="✅ Hierarchical structure created successfully!")
        print("hierarchyJson",hierarchyJson)

        if(filePath):

            fileContent = self._pdfProcessor(filePath)
            for i, chunk in enumerate(fileContent):

                hierarchyJson = self.dataProcessor.topicEnhansingPrompt(content=hierarchyJson,chunk=chunk)

        self.logger.info(f"Initial hierarchy created: {hierarchyJson}")

        emit(task_id=self.collectionName, msg=f"Initial hierarchy created: {hierarchyJson}")

        return hierarchyJson

    def __threadedToolSelector(self,element):
        def toolSelector(element,topic):
            
            toolSelector = self.dataProcessor.webSearchSelector(f"{element['co']} {element['po']}", topic)
            emit(task_id=self.collectionName, msg=f"Tool Selection Plan: {toolSelector}")
            # Check for "plans" (plural) as defined in prompt, or "plan" (singular) as fallback
            # Ensure toolSelector is a dictionary before accessing with .get()
            if isinstance(toolSelector, dict):
                plans = toolSelector.get("plans", toolSelector.get("plan", []))
                self.logger.info(f"Tool Selection Plan: {plans}")
                print("tool selector",toolSelector)
                print("plans",plans)
                return plans
            else:
                # Log unexpected response type for debugging
                print(f"Warning: toolSelector returned non-dict type: {type(toolSelector)}, value: {toolSelector}")
                return []

        

        with ThreadPoolExecutor(max_workers=16) as executor:    
            results = list(executor.map(toolSelector,repeat(element), element["topics"]))

        return results
    def __multiProcessContentExtractor(self, element):
        extractedToolContent = ""
        finalContent = []

        # with ThreadPoolExecutor(max_workers=16) as executor:    
        # for topic in element["topics"]:
        #     # implement one threader here
        
        plansList = self.__threadedToolSelector(element)
        
        def planExecutor(element,plans):
            # Mapping tool names to scraper classes
            scraper_map = {
            # Indian Educational Content (Priority for 12th grade)
            "NCERTScraper": NCERTScraper,
            "CBSEScraper": CBSEScraper,
            "DIKSHAScraper": DIKSHAScraper,
            "NROERScraper": NROERScraper,
            
            # Official Documentation
            "OfficialDocsScraper": OfficialDocsScraper,
            "WikipediaScraper": WikipediaScraper,
            
            # Existing scrapers
            "W3SchoolsScraper": W3SchoolsScraper,
            "GeeksForGeeksScraper": GeeksForGeeksScraper,
            "NPTELScraper": NPTELScraper,
            "MITOCWScraper": MITOCWScraper,
            "OpenStaxScraper": OpenStaxScraper,
            "UniversityEDUScraper": UniversityEDUScraper
        }
            mySet = set()
            if plans:
                for plan in plans:
                    # implement one threader here

                    tool_name = plan.get("tool")
                    query = plan.get("query")
                    emit(task_id=self.collectionName, msg=f"Tools selected: {tool_name}, Query: {query}")
                    
                    if tool_name in scraper_map:
                        scraper_class = scraper_map[tool_name]
                        scraper = scraper_class()
                        
                        try:
                            # Fetch content using the scraper
                            print("content search query",query)
                            result = scraper.fetch(query)
                            scraped_text = result.get('content', '')
                            print("scraped text",scraped_text[:100])
                            print("scraped text length",len(scraped_text))
                            emit(task_id=self.collectionName, msg=f"Scraped content: {scraped_text}")
                            if scraped_text not in mySet:

                                extractedToolContent += f"Content:\n{scraped_text}\n"

                                # Process topics
                                raw_topic = result.get('topic')
                                emit(task_id=self.collectionName, msg=f"Raw topic: {raw_topic}")
                                raw_topic .extend(scraper._extract_additional_topics(scraped_text))
                                print("first step to extract topics",raw_topic)
                                raw_topic = self.dataProcessor.extractTopics(raw_topic,f"{element['co']+element['po']}")
                                print("second step to extract topics",raw_topic)
                                topics_list = []
                                emit(task_id=self.collectionName, msg=f"Topics list: {topics_list}")
                                if raw_topic and isinstance(raw_topic, list) and len(raw_topic) > 0:
                                    print("-------- raw topic working")
                                    topics_list.extend(raw_topic)
                                    print("topics_list",topics_list)
                                    emit(task_id=self.collectionName, msg=f"Topics list: {topics_list}")

                                    
                                elif raw_topic and isinstance(raw_topic, str) and len(raw_topic.strip()) > 0:
                                    # Backward compatibility
                                    topics_list = [raw_topic]
                                    topics_list = self.dataProcessor.extractTopics(scraped_text[:2000])
                                    print("raw topics is a string")
                                    print("topics_list",topics_list)
                                    emit(task_id=self.collectionName, msg=f"Topics list: {topics_list}")
                                else:
                                    # Fallback: Extract from content
                                    try:
                                        print("fallback working for topics extraction")
                                        topics_list = self.dataProcessor.extractTopics(scraped_text[:2000]) # Limit context
                                        print("topics_list",topics_list)
                                    except Exception as e:
                                        emit(task_id=self.collectionName, msg=f"Error extracting topics: {e}")
                                        topics_list = ["Unknown Topic"]

                                # Thread-safe update of scraped_data
                                with self.data_lock:
                                    if "scraped_data" not in element:
                                        element["scraped_data"] = []
                                    
                                    # Store as a flat list of topics or list of lists? 
                                    # User said "returned as list of topics [t1,t2]"
                                    # Let's extend the main list
                                    if isinstance(topics_list, list):
                                        self.logger.info(f"Extending topics: {element}")
                                        element["scraped_data"].extend(topics_list)
                                    else:
                                        self.logger.info(f"Appending topic: {element}")
                                        element["scraped_data"].append(str(topics_list))
                            
                            else:
                                mySet.add(scraped_text)
                                continue
                                                
                        except Exception as e:
                            pass
                    else:
                        pass

            # Clean up and deduplicate extracted topics
            if "scraped_data" in element and isinstance(element["scraped_data"], list):
                element["scraped_data"] = list(set(element["scraped_data"]))
                print("scraped topics")
                print(element["scraped_data"])
                element["topics"].extend(element["scraped_data"])
                print("final topics",element["topics"])
                del element["scraped_data"]

            # Upsert code moved outside the inner loop to chunk all gathered content for this element
            if extractedToolContent:
                # self.logger.info(f"scraped content from tools: {extractedToolContent}")
                chunks = self._recursiveChunker(extractedToolContent)
                emit(task_id=self.collectionName, msg=f"Chunks content: {chunks}")

                # self.logger.info(f"Chunks content: {chunks}") # Optional: Uncomment to log full chunks if needed
                
                # metadata must be a list of dicts, one for each chunk
                base_metadata = {"CO": element["co"]}
                # Add text content to metadata as well, as HybridRagProcessor methods usually expect 
                # payload to contain text or store it differently. 
                # Checking ragProcessor.py:44 call -> qdrantManager.upsert_integrated_hybrid
                # QdrantManager usually stores metadata as payload.
                # Just ensuring 'text' key is present if required, but chunks are passed separately.
                # However, usually payload needs the text content to be retrieved later.
                # Let's check ragProcessor.py again... 
                # It does: `qdrantManager.upsert_integrated_hybrid(dense_vecs, sparse_vecs, metadata)`
                # It does NOT verify if 'text' is in metadata.
                # So I should probably add the text chunk to the metadata for each chunk.
                
                metadata_list = []
                for chunk in chunks:
                    meta = base_metadata.copy()
                    meta["text"] = chunk
                    metadata_list.append(meta)
                
                self.ragSystem.process_and_store(chunks=chunks, metadata=metadata_list)
            
            return element    
        
        with ThreadPoolExecutor(max_workers=16) as executor:    
            results = list(executor.map(planExecutor,repeat(element), plansList))
        
        # Collect unique topics from all results
        all_topics = set()
        for result in results:
            # result["topics"] is a list, so we need to iterate through it
            if "topics" in result and isinstance(result["topics"], list):
                for topic in result["topics"]:
                    all_topics.add(topic)
        
        element["topics"].extend(list(all_topics))
        return element

        
    def ContentExtractor(self, content):
        """
        Extracts content using ProcessPoolExecutor for true parallelism.
        Uses standalone worker function to avoid pickling issues.
        """
        print("ContentExtractor")

        # Prepare data for worker processes
        worker_data = [(element, self.collectionName) for element in content]
        
        # Use ProcessPoolExecutor for CPU-bound content extraction
        with ProcessPoolExecutor(max_workers=3) as executor:
            finalContent = list(executor.map(_worker_content_extractor, worker_data))
        
        return finalContent

    def baseQuestionpaperGenerator(self,content):
        """
        Generates base questions and enhances them using RAG retrieval.
        Uses ProcessPoolExecutor for parallel processing.
        """
        # Step 1: Generate base questions using ThreadPoolExecutor (I/O bound - API calls)
        def baseQuestions(element):
            questions = self.dataProcessor.baseQuestionCreator(f"{element}")
            return questions
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            finalQuestions = list(executor.map(baseQuestions, content))
        output_filename = f"extracted_questions.json"
    
        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(finalQuestions, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Output saved to: {output_filename}")
        except Exception as e:
            # If output is not JSON serializable, save as text
            output_filename = f"extracted_questions.txt"
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(str(finalQuestions))
        # Step 2: Enhance questions with RAG using ProcessPoolExecutor (CPU bound)
        if len(content) == len(finalQuestions):
            # Prepare data for worker processes
            worker_data = [
                (questions, element, self.collectionName) 
                for questions, element in zip(finalQuestions, content)
            ]
            
            # Use ProcessPoolExecutor for parallel RAG retrieval
            with ProcessPoolExecutor(max_workers=3) as executor:
                finalQuestions = list(executor.map(_worker_rag_retrieval, worker_data))
                print(finalQuestions)
        
        return content, finalQuestions

    def demoQuestionpaperGenerator(self,text,filePath):
        emit(task_id=self.collectionName, msg="📋 Starting question paper generation pipeline...")
        
        emit(task_id=self.collectionName, msg="🏗️ Step 1/4: Creating hierarchical structure...")
        hierarchyJson = self.hierarchicalDataCreator(text,filePath)
        emit(task_id=self.collectionName, msg=str(hierarchyJson))
        emit(task_id=self.collectionName, msg="🌐 Step 2/4: Extracting content from web sources...")
        content = self.ContentExtractor(hierarchyJson)
        emit(task_id=self.collectionName, msg=str(content))
        emit(task_id=self.collectionName, msg="❓ Step 3/4: Generating base questions...")
        baseQP = self.baseQuestionpaperGenerator(content)
        emit(task_id=self.collectionName, msg=str(baseQP))
        self.logger.info(f"Base Question Paper: {baseQP}")
        
        # Validate and clean questions asynchronously
        emit(task_id=self.collectionName, msg="✨ Step 4/4: Validating and enhancing questions...")
        self.logger.info("Starting async question validation...")
        content_data, finalQuestions = baseQP
        
        def validate_co_questions(co_data):
            """Validate questions for a single CO - processes entire list or in batches of 10"""
            co_index, co_dict = co_data
            questions_list = co_dict.get("questions", [])
            
            if not questions_list:
                return co_index, co_dict
            
            self.logger.info(f"Validating {len(questions_list)} questions for CO: {co_dict.get('CO', 'Unknown')[:50]}...")
            
            # Call validator with batching for token efficiency
            try:
                # If questions list is large (>10), process in batches of 10
                batch_size = 10
                all_cleaned_questions = []
                
                if len(questions_list) <= batch_size:
                    # Process all questions in one call (token efficient)
                    cleaned_questions = self.dataProcessor.questionValidator(questions_list)
                    emit(task_id=self.collectionName, msg=str(cleaned_questions))
                    if isinstance(cleaned_questions, list):
                        all_cleaned_questions = cleaned_questions
                    else:
                        self.logger.warning(f"Validator returned non-list: {type(cleaned_questions)}")
                        all_cleaned_questions = questions_list
                else:
                    # Process in batches of 10 for very large lists
                    emit(task_id=self.collectionName, msg=f"Processing {len(questions_list)} questions in batches of {batch_size}")
                    
                    for i in range(0, len(questions_list), batch_size):
                        batch = questions_list[i:i + batch_size]
                        emit(task_id=self.collectionName, msg=f"Validating batch {i//batch_size + 1} ({len(batch)} questions)")
                        
                        cleaned_batch = self.dataProcessor.questionValidator(batch)
                        emit(task_id=self.collectionName, msg=str(cleaned_batch))
                        if isinstance(cleaned_batch, list):
                            all_cleaned_questions.extend(cleaned_batch)
                        else:
                            all_cleaned_questions.extend(batch)  # Keep original batch
                
                co_dict["questions"] = all_cleaned_questions
                self.logger.info(f"✅ Successfully validated {len(all_cleaned_questions)} questions for CO")
                    
            except Exception as e:
                self.logger.error(f"❌ Validation failed for CO: {e}")
                co_dict["questions"] = questions_list  # Keep original on error
            
            return co_index, co_dict
        
        # Use ThreadPoolExecutor for async validation
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all CO validations
            future_to_co = {
                executor.submit(validate_co_questions, (i, co_dict)): i 
                for i, co_dict in enumerate(finalQuestions)
            }
            
            # Collect results
            for future in concurrent.futures.as_completed(future_to_co):
                co_index, validated_co = future.result()
                finalQuestions[co_index] = validated_co
                emit(task_id=self.collectionName, msg=f"Question validation complete for CO: {validated_co['CO']}") 
        
        emit(task_id=self.collectionName, msg="Question validation complete")
        print("done processing questions")
            
        return content_data, finalQuestions

        
    # def mainEvaluatorLoop(self,verdict):
    #     for i,content in enumerate(self.currentContent):
    #         generatedQuestions = self.currentQuestionPaper[i]["questions"]

    def mainQuestionPaperEvaluator(self,content,generatedQuestions,verdict):
    
        while (True):
            if len(self.mainMemory["stepReasoning"]) > 6:
                summary = self.dataProcessor.stepReasoningGenerator(self.mainMemory["stepReasoning"]) 
                self.mainMemory["stepReasoning"] = []
                self.mainMemory["stepReasoning"].append(summary)
               
            mainLoop = self.dataProcessor.questionEvaluatorMainLoop(content,generatedQuestions,verdict,self.mainMemory)
            
            # Debug: Check if mainLoop is a dictionary
            if not isinstance(mainLoop, dict):
                print(f"ERROR: mainLoop is not a dictionary. Type: {type(mainLoop)}")
                print(f"mainLoop value: {mainLoop}")
                # Return original questions if parsing failed
                return content, generatedQuestions
            
            if "tool" in mainLoop and mainLoop["tool"] == "ragAgent":
                print("inside the tool caller")
                #call rag agent
                callDetails = {"tool":"ragAgent","prompt":mainLoop["prompt"]}
                self.mainMemory["toolMemory"].append(callDetails)
                ragOutput = self.__ragAgent(content,mainLoop["prompt"])
                if "questions" in ragOutput:
                    self.mainMemory["questionMemory"].update(ragOutput["questions"])
                if "stepReasoning" in mainLoop:
                    self.mainMemory["stepReasoning"].extend(mainLoop["stepSummary"])

            elif "questions" in mainLoop and mainLoop.get("taskOver") == False:
                print("question analysis state")
                self.mainMemory["questionMemory"].update(mainLoop["questions"])
                if "stepReasoning" in mainLoop:
                    self.mainMemory["stepReasoning"].extend(mainLoop["stepSummary"])

            else:
                print("final out put")
                self.mainMemory =  {
                    "toolMemory" : [],
                    "questionMemory" : set(),
                    "stepReasoning" : []
                }

                return content,mainLoop["questions"]

                
    def chatAgent(self,input,questionPaperSummarizer = None,currentQuestionPaper=None,sessionHistory=None):
        if not questionPaperSummarizer:
            print("no question summary given")
            print("inside the question paper summarizer")
            questionPaperSummarizer = self.multiThreadedQuestionsSummarizer(currentQuestionPaper)
        self.currentQuestionPaper.extend(currentQuestionPaper)

        print(input)
        print(sessionHistory)
        
        plannerAgentInput ={"content": [],"chat_history":sessionHistory}
        for co in questionPaperSummarizer:
            topics = set()
            baseConcepts = set()
            for q in co["questions_summary"]:
                topics.add(q["topic"])
                baseConcepts.add(q["base_concept"])
            co["topics"] = list(topics)
            plannerAgentInput["content"].append({"co":co["CO"],"po":co["PO"],"topics":co["topics"],"baseConcepts":list(baseConcepts)})

        supervisorAgent = self.dataProcessor.chatPlanner(input=input,content=plannerAgentInput)
        memoryoutput = {"direct":supervisorAgent.get("direct"),"question_summary":questionPaperSummarizer,"answer":None}
        if supervisorAgent.get("direct"):
            memoryoutput["answer"] = supervisorAgent["answer"]
            return memoryoutput

        if supervisorAgent.get("direct")==False:
            agentOutputs = []
            for p in supervisorAgent["plan"]:
                stepInput = p["step"]
                for part in p["co"]:
                    CONumber = int(part[2:])-1
                    agentOutputs.append({
                        "co": CONumber,
                        "output": self.chatAgentProcessor(
                            questionsSummary=questionPaperSummarizer[CONumber]["questions_summary"],
                            instruction=stepInput,
                            CONumber=CONumber
                        )
                    })

            # Validate and clean agent outputs
            print("\n🔍 Validating and deduplicating agent outputs...")
            validatedOutputs = self.dataProcessor.chatAgentOutputValidator(agentOutputs)
            print(f"✅ Validation complete. Returning {len(validatedOutputs)} validated outputs.\n")
            for v in validatedOutputs:
                # Handle both flattened and nested structures for robustness
                output_data = v.get("output", v)
                
                if "action" not in output_data:
                    print(f"Skipping invalid output: {v}")
                    continue
                
                action = output_data.get("action")
                questions = output_data.get("questions", [])
                co_index = v.get("co")
                
                if co_index is None:
                    print(f"Skipping output with missing CO index: {v}")
                    continue

                if action == "ADD":
                    self.currentQuestionPaper[co_index]["questions"].extend(questions)
                elif action == "UPDATE":
                    # For UPDATE, questions is a dict {q_id: new_text}
                    if isinstance(questions, dict):
                        for q_id, new_text in questions.items():
                            try:
                                q_idx = int(q_id) - 1
                                if 0 <= q_idx < len(self.currentQuestionPaper[co_index]["questions"]):
                                    self.currentQuestionPaper[co_index]["questions"][q_idx] = new_text
                            except (ValueError, IndexError):
                                print(f"Error updating question {q_id} in CO {co_index}")
                elif action == "REMOVE":
                    # For REMOVE, questions is a list of q_ids
                    # We need to remove carefully to avoid index shifting issues if removing by index
                    # But wait, questions list contains strings? The logic in the original code was:
                    # for q in v["output"]["questions"]:
                    #   self.currentQuestionPaper[v["co"]]["questions"].remove(q)
                    # This implies 'questions' was a list of question STRINGS (the actual objects), not IDs.
                    # BUT the prompt says REMOVE returns list of IDs.
                    # "3. REMOVE → Delete questions ... {"action": "REMOVE", "questions": ["q_id1", "q_id2"]}"
                    # The original code tries to remove(q), which works if q is the item itself. 
                    # If q is an ID, it will crash.
                    
                    # Let's check prompt again:
                    # "REMOVE → Delete questions ... {"action": "REMOVE", "questions": ["1", "3", "7"]}"
                    # "questions": ["1", "3", "7"] -> These are IDs (strings).
                    
                    # So original code:
                    # for q in v["output"]["questions"]:
                    #   self.currentQuestionPaper[v["co"]]["questions"].remove(q)
                    # This would try to remove the STRING "1" from the list of questions. 
                    # But self.currentQuestionPaper[...]["questions"] matches line 404:
                    # "questions": [ "Understand the basic...", ... ] (List of strings)
                    
                    # So "1" is not in that list. The number 1 is an index (1-based).
                    # So we need to remove by index.
                    
                    # Let's fix the REMOVE logic too.
                    # Convert IDs to indices, sort descending, and pop.
                    
                    indices_to_remove = []
                    for q_id in questions:
                        try:
                            indices_to_remove.append(int(q_id) - 1)
                        except ValueError:
                            pass
                    
                    # Remove from end to start to preserve indices
                    for idx in sorted(indices_to_remove, reverse=True):
                         if 0 <= idx < len(self.currentQuestionPaper[co_index]["questions"]):
                             self.currentQuestionPaper[co_index]["questions"].pop(idx)
            if "answer" in supervisorAgent:
                memoryoutput["answer"] = supervisorAgent["answer"]
                memoryoutput["question_summary"] = self.currentQuestionPaper
                return memoryoutput
            memoryoutput["answer"] = None
            memoryoutput["question_summary"] = self.currentQuestionPaper
            return memoryoutput

     

        
    def chatAgentProcessor(self,questionsSummary,instruction,CONumber):

        while (True):
            chatProcessor = self.dataProcessor.chatAgent(questionsSummary=questionsSummary,input=instruction,memory=self.chatMemory)
            
            # Validate that chatProcessor is a dictionary
            if not isinstance(chatProcessor, dict):
                print(f"⚠️ Warning: chatAgent returned non-dict type: {type(chatProcessor)}")
                print(f"   Value: {str(chatProcessor)[:200]}...")
                return {
                    "error": "Failed to parse agent response",
                    "raw_response": str(chatProcessor)
                }
            
            print(f"\n📋 Chat Processor Response: {chatProcessor.keys()}")
            
            if "needActualQuestion" in chatProcessor:
                print("🔍 Agent needs actual question text...")
                actualQuestions = []
                for idx in chatProcessor["needActualQuestion"]:
                    try:
                        question_idx = int(idx)
                        actualQuestions.append(self.currentQuestionPaper[CONumber]["questions"][question_idx])
                    except (ValueError, IndexError, KeyError) as e:
                        print(f"   ⚠️ Error getting question {idx}: {e}")
                
                self.chatMemory.append({"called tool": "needActualQuestion", "tool output": actualQuestions})
                print(f"   ✅ Retrieved {len(actualQuestions)} questions")
           
            elif "tool" in chatProcessor and chatProcessor["tool"] == "ragAgent":
                print("🔧 Calling RAG Agent...")
                print(f"   Search Query: {chatProcessor.get('searchQuery', 'N/A')}")
                
                ragOutput = self.__ragAgent(
                    str(self.currentQuestionPaper[CONumber]["CO"]) + str(self.currentQuestionPaper[CONumber]["PO"]),
                    chatProcessor["searchQuery"]
                )
                self.chatMemory.append({"called tool": "ragAgent", "tool output": ragOutput})
                print(f"   ✅ RAG Agent completed")
           
            elif "action" in chatProcessor:
                print(f"✅ Final action received: {chatProcessor['action']}")
                return chatProcessor

            else:
                print("⚠️ No recognized response pattern. Agent thinking...")
                print(f"   Response keys: {list(chatProcessor.keys())}")
                # Continue loop to let agent think more
                # Add a safety counter to prevent infinite loops
                if not hasattr(self, '_thinking_counter'):
                    self._thinking_counter = 0
                self._thinking_counter += 1
                
                if self._thinking_counter > 5:
                    print("❌ Agent exceeded thinking limit. Returning current state.")
                    self._thinking_counter = 0
                    return {
                        "error": "Agent exceeded thinking iterations",
                        "last_response": chatProcessor
                    }
                


        
       
       
            

        
    def __ragAgent(self,content,prompt):
        ragQueryResponse = self.dataProcessor.ragQueryGenerator(content,prompt)
        
        # Extract queries from the response
        # ragQueryGenerator returns {"queries": [...]} format
        if isinstance(ragQueryResponse, dict):
            ragQuery = ragQueryResponse.get("queries", [])
            print(f"📋 Extracted {len(ragQuery)} queries from response")
        elif isinstance(ragQueryResponse, list):
            ragQuery = ragQueryResponse
        else:
            # Fallback: treat as single query
            ragQuery = [str(ragQueryResponse)] if ragQueryResponse else []
        
        # Debug: Log the generated queries
        print(f"🔍 RAG Query Generator produced {len(ragQuery)} queries")
        if isinstance(ragQuery, list):
            for idx, q in enumerate(ragQuery):
                query_str = str(q) if not isinstance(q, str) else q
                print(f"   Query {idx+1}: '{query_str[:100]}...' (length: {len(query_str)})")
        else:
            query_str = str(ragQuery)
            print(f"   Single query: '{query_str[:100]}...'")
        
        retrivedContent = []
        duplicatesAnalyser = set()
        
        # Ensure ragQuery is a list
        if not isinstance(ragQuery, list):
            ragQuery = [ragQuery] if ragQuery else []
        
        for idx, query in enumerate(ragQuery):
            print(f"\n🔎 Processing query {idx+1}/{len(ragQuery)}...")
            
            # Convert to string if needed
            query_str = str(query) if not isinstance(query, str) else query
            
            # Validate query before searching (allow 2+ chars for "AI", "ML", etc.)
            if not query_str or len(query_str.strip()) < 2:
                print(f"   ⚠️ Skipping invalid/empty query: '{query_str}'")
                continue
            
            retrived = self.ragSystem.search(query=query_str)
            self.logger.info(f"Retrieved content: {retrived}")
            print(f"   ✅ Retrieved {len(retrived)} results")
            
            # Safe iteration - create a copy to avoid modification during iteration
            for data in retrived[:]:  # Use slice to create a copy
                if data.get("text") not in duplicatesAnalyser:
                    duplicatesAnalyser.add(data["text"])
                else:
                    retrived.remove(data)
            
            # Only summarize if we have retrieved content
            if retrived:
                contentSummary = self.dataProcessor.contentSummarizer(query_str, retrived)
                retrivedContent.append(contentSummary)
            else:
                print(f"   ⚠️ No content retrieved for query: '{query_str[:50]}...'")

        if not retrivedContent:
            print("⚠️ Warning: No content was retrieved from any RAG queries")
            return {"questions": []}  # Return empty result structure
        
        finalContent = self.dataProcessor.ragFinalizer(requirement_prompt=prompt, content_summary=retrivedContent)
        return finalContent

    def multiThreadedQuestionsSummarizer(self,content):
        finalInput = content.copy()
     
        def summarizer(element):
            """
            Process questions in batches of 25 and summarize each batch.
            Assigns correct question IDs based on position in original list.
            """
            questionSummary = []
            
            # Process questions in chunks of 25
            for chunk_start in range(0, len(element), 25):  
                # Build input string for this chunk
                summarizerInput = ""
                chunk = element[chunk_start:chunk_start + 25]
                
                # Enumerate questions in this chunk (0-24 for display)
                for idx, question in enumerate(chunk):
                    summarizerInput += str(idx + 1) + ". " + question + "\n"
                
                # Get summaries from the LLM
                chunks = self.dataProcessor.currentQPSummarizer(summarizerInput)
                
                # Assign correct question IDs based on original position
                for idx, summary in enumerate(chunks):
                    # question_id should be the actual position in the full list
                    summary["question_id"] = str(chunk_start + idx)
                
                questionSummary.extend(chunks)
            
            return questionSummary
            

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(summarizer, element["questions"]) for element in finalInput]
            for i, future in enumerate(futures): 
                finalInput[i]["questions_summary"] = future.result()

        return finalInput
                
    def _pdfProcessor(self, pdf_path, chunk_size=500, chunk_overlap=50):
        """
        Extracts text from a PDF and splits it into token-efficient chunks.
        """
        text_content = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text_content += (page.extract_text() or "") + "\n"
        except Exception as e:
            self.logger.error(f"Error reading PDF: {e}")
            return []

        # Fix: call self._recursiveChunker and pass args
        chunks = self._recursiveChunker(text_content, chunk_size, chunk_overlap)
        return chunks

    def _recursiveChunker(self, textContent, chunk_size=500, chunk_overlap=50):
        if not textContent.strip():
            return []
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        chunks = splitter.split_text(textContent)
        return chunks

    # def questionPaperGeneratorAgent(self):

        return