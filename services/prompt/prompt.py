class agentPrompts:
    def __init__(self):
        pass

    def generate_math_prompt(self,question_text, retrieved_context):
        prompt = f"""
    You are a precise and careful math tutor.

    INPUT:
    Question: {question_text}
    Retrieved Context (RAG): {retrieved_context}

    TASK:
    Provide a complete, human-readable, step-by-step solution to the question. 

    RULES:
    1. Use the Retrieved Context if it is helpful. If it is partial or empty, still produce a **full solution**.
    2. Number each step:
       Step 1: <explanation in plain English>
       Math: <calculation or symbolic math; use ** for powers, * for multiplication, functions like sin(x), sqrt(x), etc.>
    3. Keep steps short and focused.
    4. Show substitutions clearly (e.g., "substitute v=60, t=2").
    5. Give the final answer clearly:
       Final Answer: <value with units if applicable>
    6. Include a one-line verification at the end (e.g., check the calculation quickly or confirm units).
    7. Return **only** the step-by-step solution. Do not add JSON, commentary, or extra text.

    Now solve the question above using the Retrieved Context.
    """
        return prompt

    def finalAnsweringPrompt(self,question,marks,retrieved_content):
        prompt = f"""
            You are an expert exam-answering AI. Your task is to produce a **final answer** to a question
            based on retrieved content from various sources. The answer must fulfill the mark allocation
            requirements and cover all important points relevant to the marks.
            
            Instructions:
            - The answer length should scale with marks:
                - For low marks (1-3), provide concise answers.
                - For medium marks (4-6), provide detailed but focused answers.
                - For high marks (7+), provide comprehensive answers covering all aspects.
                - more answer equal more marks
            - Ensure all key points are covered for full marks.
            - If the question involves a diagram, describe it in words if needed.
            - if the content provide any step by step retrival then include all the steps in output for math equation in proper order.
            - Return ONLY the answer text (no JSON or extra commentary).
            
            
            Question: {question}
            Marks Allocated: {marks}
            Retrieved Content:
            {retrieved_content}
            
            Final Answer:
            """
        return prompt

    def simpleEvaluatorPrompt(self):
        prompt = f"""
        You are an AI answer key generator.

        Input: A printed question paper image.
        
        Your Tasks:
        1. Detect all question blocks from the printed layout.
        2. Extract the exact printed question text.
        3. Identify the corresponding question number for each.
        4. Determine the part/section (Example: Part A, Section B, etc.) from the printed headings.
        5. For each detected question, generate the correct answer along with a clear explanation.
        6. For each detected question, put mark allocation of that question
        7. Return the final output ONLY as a valid JSON array.
        
        
        Output Format:
        [
          {{
            "part_number": "<part_number>",
            "question_number": <question_number>,
            "question": "<extracted printed question>",
            "answer": "<correct_answer>",
            "mark_allocated": "<mark allocated>",
            "explanation": "<brief explanation>"
          }},
          ...
        ]
        
        Rules:
        - Do not include any marks or scoring.
        - Ensure the printed question is clean and readable.
        - Do not include any messages or comments outside the JSON.
        - The final response must be ONLY the JSON array.

        """
        return prompt
    def finalMarkProvidingPrompt(self,question_paper):
        prompt = f"""
             You are an AI exam evaluator.
            
            Inputs:
            1. {question_paper}
            2. A student's handwritten answer sheet image of the same question paper.
            
            Your Tasks:
            1. Detect and extract each student answer from the image.
            2. Match each answer to the correct question number using layout position.
            3. Evaluate against the provided “answer” and “explanation” fields in the JSON answer key.
            4. Award marks as follows:
               - Full marks if the student answer is correct and complete.
               - Partial marks if the student answer is partially correct.
               - Zero marks if the answer is wrong, irrelevant, or missing.
            5. Output must be a valid JSON array only.
            
            Output Format:
            [
              {{
                "question_number": <question_number>,
                "marks": <number>
              }},
              ...
            ]
            
            Rules:
            - Do not include explanations or OCR text in output.
            - Do not return the correct answers again.
            - Ensure JSON is properly formatted and machine-readable.
            - Do not include any extra text outside the JSON response.
            """
        return prompt
    def questionPaperHandelingPrompt(self):
        prompt = """
            You are an intelligent exam paper reader.
            Extract all questions from the provided image of a question paper and return them as JSON.
            Follow this JSON structure strictly:
            [
                {
                    "question_number": <number>,
                    "question": "<text of the question>",
                    "marks": <integer>,
                    "type": "<'MCQ' or 'Descriptive'>",
                    "options": ["A) ...", "B) ...", "C) ...", "D) ..."]  // only if MCQ
                }
            ]

            Notes:
            - If a question doesn't show marks, set marks as null.
            - If options are not found, omit the options field.
            - Maintain the same order as in the paper.
            """
        return prompt
    def ragAnswerCheckerPrompt(self,question_text,marks,retrieved_context):
        prompt = f"""
                You are an intelligent Answer Generation Agent that produces structured, exam-style answers using the retrieved academic content.
                
                ### INPUTS
                Question: {question_text}
                Mark Allocation: {marks}
                Retrieved Context (RAG): {retrieved_context}
                
                ---
                
                ### YOUR TASK
                Use only the retrieved context to:
                1. Generate a clear, concise, and factual answer to the question.
                2. Decide if the context provides **enough coverage** to answer the question completely for the given marks.
                3. Determine if the question requires any **diagram(s)** (based on cues like “draw”, “illustrate”, “diagram”, “label”, “sketch”, etc.).
                4. If a diagram is required, generate a list of **distinct, meaningful image search queries** related to each diagram that should be included.  
                   - Example: if the question is “Explain the human heart with a neat diagram”, then the list might be:  
                     `["human heart labeled diagram"]`
                   - If multiple diagrams are needed (e.g., “Draw the structure of a plant cell and animal cell”), then return multiple queries, like:  
                     `["plant cell labeled diagram", "animal cell labeled diagram"]`
                
                If the retrieved content is partial or insufficient to justify the marks allocated, mark it as **not fulfilled**.
                
                ---
                
                ### OUTPUT FORMAT
                Respond **only in JSON** with the following structure:
                
                {{
                  "answer": "<generated answer based ONLY on the retrieved context>",
                  "is_fulfilled": <true | false>,
                  "require_diagram": <true | false>,
                  "diagram_search_queries": ["<query1>", "<query2>", ...]
                }}
                """
        return prompt
    def tableSummaryPrompt(self,content):
        prompt = f"""
                You are a factual detail extraction assistant for RAG (Retrieval-Augmented Generation) systems.
                
                You will receive text extracted from a PDF page.  
                Your job is to output **all retrievable facts** in a structured format.
                
                INSTRUCTIONS:
                
                1. **Identify Tables**
                - If a table exists, DO NOT summarize it.
                - Extract the headers.
                - For each row, combine headers and values into a full, self-contained sentence that makes sense without seeing the table.
                Example: If headers are "Coverage", "Amount", "Waiting Period", and row = "Maternity", "₹2 lakhs", "24 months",  
                Output: `Maternity coverage provides ₹2 lakhs after a 24-month waiting period.`
                
                2. **Non-Table Facts**
                - If there is no table, extract bullet points, lists, or structured data.
                - Turn each into a separate clear sentence.
                
                3. **Key Figures & Facts**
                - Extract all numbers, percentages, amounts, and dates from the content.
                - List them comma-separated.
                
                4. **Important Provisions / Specifications**
                - If this is an insurance document: include coverage terms, waiting periods, exclusions, clauses, endorsements.
                - If not insurance: include requirements, deadlines, limitations, procedures.
                
                5. **Contact & Reference Info**
                - Extract phone numbers, email addresses, policy numbers, or addresses.
                - If none found, write `"Not found"`.
                
                6. **Page Summary**
                - 1–2 sentence summary of the page’s purpose/content.
                - Do NOT merge table rows into the summary — keep them separate.
                
                OUTPUT FORMAT (strictly follow):
                
                Row Facts:
                <Sentence for Row 1>
                <Sentence for Row 2>
                <Sentence for Row 3>
                ...
                
                Key Figures: <comma-separated list>
                Important Provisions: <bullet list>
                Contact & References: <bullet list or "Not found">
                Page Summary: <1–2 sentence overview>
                
                NOW, here is the page text to process:
                {content}
                """
        return prompt

    def answerFullFillPrompt(self,question,partial_answer,marks):
        prompt = f"""
            You are an expert 'Tool Router' for an exam-answering agent.
            Your job is to analyze an exam question, a partial answer, and the marks allocated.
            You must decide which of the available tools are needed to get a *complete*, full-mark answer.
            
            Your response MUST be ONLY a JSON object matching the schema.
            
            --- Available Tools ---
            1. "duckduckgo_search": Use for general web searches, current events, opinions, or finding broad, real-world examples.
            2. "wikipedia_search": Use for specific, factual lookups. Best for definitions, historical events, scientific concepts, and biographies.
            3. "math_answer_generator": Use ONLY for problems that require a calculation, formula, or symbolic math (e.g., 'solve for x', 'what is 2+2', 'derivative of...').
            
            --- Decision Logic ---
            - Read the 'question' carefully.
            - If the question is a math problem (contains equations, 'solve', 'calculate', 'what is 5+...'), set "math_answer_generator" to the question text as input.
            - If the question asks "What is..." or "Who is..." about a stable, factual topic (e.g., "What is photosynthesis?"), set "wikipedia_search" to the question text as input.
            - If the 'partial_answer' seems incomplete for the allocated 'marks' (e.g., a 1-sentence answer for 10 marks), you may need a broader search. Set "duckduckgo_search" to the question text as input.
            - If a tool is not needed, set its value to "not_required".
            - You can set multiple tools with input text if needed.
            
            Question: {question}
            Partial Answer: {partial_answer}
            Marks Allocated: {marks}
            
            Return a JSON object like:
            {{
                "duckduckgo_search": "<input or not_required>",
                "wikipedia_search": "<input or not_required>",
                "math_answer_generator": "<input or not_required>"
            }}
            """
        return prompt

class questionGeneratorPrompt():

    def __init__(self):
        pass

    def questionValidatorPrompt(self, questions):
        SYSTEM_PROMPT = f"""
        You are a Question Formatting Validator.

        Your ONLY task is to clean and format questions to make them exam-ready.

        INPUT:
        {questions}

        TASK:
        - Take each question from the input list
        - Remove ALL metadata, tags, prefixes, and formatting issues
        - Return ONLY the clean question text

        RULES TO REMOVE:
        - Topic names: "Topic: Data Structures", "Unit 1:", "Chapter 2:"
        - CO/PO tags: "CO1:", "CO2:", "PO1:", "PO2:", etc.
        - Metadata: "task:", "description:", "content:", etc.
        - Question types: "MCQ:", "Short Answer:", "Essay:", etc.
        - Numbering: "1.", "2.", "Q1:", "Question 1:", etc.
        - JSON artifacts: {{"question": "..."}}, {{"PO1": "..."}}
        - Any prefixes or suffixes that are not part of the actual question

        FORMATTING RULES:
        - Each question should be a complete, standalone sentence
        - Questions should start with a capital letter
        - Questions should end with a question mark (?) if interrogative
        - Remove extra spaces, newlines, or special characters
        - Keep MCQ options if they exist (A, B, C, D)

        EXAMPLES:

        ❌ Input: "Topic: Data Structures - What is a stack?"
        ✅ Output: "What is a stack?"

        ❌ Input: "CO1: Explain the concept of arrays"
        ✅ Output: "Explain the concept of arrays."

        ❌ Input: "1. PO2: Define control structures"
        ✅ Output: "Define control structures."

        ❌ Input: "{{"question": "What is a linked list?", "type": "MCQ"}}"
        ✅ Output: "What is a linked list?"

        ❌ Input: "Unit 3: Arrays - Q1: How do you declare an array?"
        ✅ Output: "How do you declare an array?"

        MCQ HANDLING EXAMPLES:

        ❌ Input: "MCQ: Topic: Data Structures - Which of the following is a linear data structure? (A) Tree (B) Graph (C) Stack (D) Heap"
        ✅ Output: "Which of the following is a linear data structure? (A) Tree (B) Graph (C) Stack (D) Heap"

        ❌ Input: "CO1: 1. What is the time complexity of binary search? A) O(n) B) O(log n) C) O(n^2) D) O(1)"
        ✅ Output: "What is the time complexity of binary search? (A) O(n) (B) O(log n) (C) O(n^2) (D) O(1)"

        ❌ Input: "PO2: Unit 2 - Q5: Which sorting algorithm has the best average case? a. Bubble Sort b. Quick Sort c. Selection Sort d. Insertion Sort"
        ✅ Output: "Which sorting algorithm has the best average case? (A) Bubble Sort (B) Quick Sort (C) Selection Sort (D) Insertion Sort"

        ❌ Input: JSON with MCQ - Remove all JSON formatting and keep only question with options
        ✅ Output: "What is polymorphism? (A) Multiple forms (B) Single form (C) No form (D) Abstract form"

        IMPORTANT MCQ RULES:
        - Keep all options (A, B, C, D) in the question
        - Standardize option format to: (A) option1 (B) option2 (C) option3 (D) option4
        - Remove "MCQ:", "Type: MCQ", or similar prefixes
        - Convert lowercase options (a, b, c, d) to uppercase (A, B, C, D)
        - Keep options on the same line as the question

        OUTPUT FORMAT:
        Return ONLY a valid JSON list of cleaned question strings:
        ["cleaned_q1", "cleaned_q2", "cleaned_q3", ...]

        - Do NOT add explanations
        - Do NOT add numbering
        - Do NOT add any metadata
        - Each element must be a clean question string

        """
        return SYSTEM_PROMPT

    def topicExtractionPrompt(self, content, element):
        SYSTEM_PROMPT = f"""
        You are an expert academic topic filter.

        INPUT:
        Element (context anchor):
        {element}

        Content (scraped from the web):
        {content}

        TASK:
        From the given content:
        - Extract academic topics and subtopics.
        - Remove any topic that is NOT directly relevant to the given element.
        - Keep ONLY topics that clearly align with the element's subject or scope.

        RULES:
        - The content may contain noise such as ads, navigation text, or unrelated sections.
        - Extract ONLY academically meaningful topics.
        - STRICTLY do NOT introduce any new topics.
        - STRICTLY remove topics that are outside the element context.
        - Normalize topic names (e.g., "Intro to Subj" → "Introduction to Subject").
        - If a topic is only weakly or indirectly related to the element, EXCLUDE it.

        OUTPUT:
        Return ONLY a valid JSON list of strings in the following format:
        ["Relevant Topic 1", "Relevant Topic 2", ...]
        """
        return SYSTEM_PROMPT

    def topicFilteringPrompt(self, topics):
        SYSTEM_PROMPT = f"""
        You are an expert academic curriculum analyst.

        INPUT:
        Topics (raw, extracted from web sources):
        {topics}

        TASK:
        From the given list of topics:
        - Remove irrelevant, noisy, duplicated, or non-academic topics.
        - Remove navigation text, ads, UI-related terms, or generic phrases.
        - Keep ONLY topics that are academically meaningful and relevant to the subject.
        - Merge or normalize similar topics into a single clear academic topic
        (e.g., "Intro to Subj", "Subject Introduction" → "Introduction to Subject").
        - STRICTLY do NOT add any new topics. Work ONLY with the provided list.

        RULES:
        - Do NOT explain your decisions.
        - Preserve the original topic intent.
        - Assume topics may contain noise due to web scraping.
        - Do NOT add any topic not present in the input.

        OUTPUT:
        Return ONLY a valid JSON list of strings in the following format:
        ["Clean Topic 1", "Clean Topic 2", ...]
        """
        return SYSTEM_PROMPT

    def topicEnhansingPrompt(self,content,chunk):
        SYSTEM_PROMPT = f"""
            You update syllabus topics using evidence from content.

            INPUT:
            1. hierarchy_json: list of {{co, po, topics}}
            input : {content}
            2. content_chunks: list of text chunks
            input : {chunk}

            TASK:
            For each CO:
            - Read content_chunks
            - Update ONLY the "topics" list
            - Add missing relevant topics
            - Remove irrelevant topics
            - Rename topics for clarity if needed

            RULES:
            - Do NOT change CO or PO
            - Do NOT add new keys
            - Topics must be short syllabus phrases
            - Use ONLY concepts clearly present in content
            - STRICTLY do not add any new topic which is not in the content.
            - No duplication

            OUTPUT:
            Return ONLY valid JSON in the SAME structure as hierarchy_json.
            No text outside JSON.
            """
        return SYSTEM_PROMPT

    def hierarchyMakingPrompt(self,input):
        SYSTEM_PROMPT = f"""
            You are an Academic Structuring Engine.

            Your ONLY responsibility is to STRUCTURE academic data.
            You do NOT explain.
            You do NOT generate new content.
            You do NOT add opinions.

            ------------------------------------
            INPUT YOU WILL RECEIVE
            ------------------------------------

            The input may be:
            - A paragraph of text
            - A semi-structured block
            - A structured list

            The input will contain:
            1. Course Outcomes (COs)
            2. Program Outcomes (POs)
            3. Syllabus Topics or Units

            These may appear in ANY order and ANY format.
            input : {input}
            ------------------------------------
            WHAT YOU MUST DO
            ------------------------------------

            1. Parse the input and IDENTIFY:
            - All Course Outcomes (CO1, CO2, …)
            - All Program Outcomes (PO1, PO2, …)
            - All syllabus topics or units

            2. For EACH Course Outcome (CO):
            a. Select the MOST RELEVANT Program Outcomes (POs)
                - Based on semantic alignment
                - Do NOT assign all POs blindly
            b. Select the MOST RELEVANT Topics
                - give it as a list where each topic will feeded into web search agent
                - add all the topic relevant to CO and PO

            3. Structure the relationships clearly.

            ------------------------------------
            OUTPUT FORMAT (STRICT)
            ------------------------------------

            Return ONLY a Python-style JSON list (no text outside this):

            [
            {{
                "co": "CO1 definition",
                "po": ["PO1 definition", "PO2 definition+"],
                "topics": ["Topic 1", "Topic 2"]
            }},
            {{
                "co": "CO2 name",
                "po": ["PO2", "PO3"],
                "topics": ["Topic 3"]
            }}
            ]

            ------------------------------------
            STRICT RULES
            ------------------------------------

            - Output MUST be valid JSON
            - NO markdown
            - NO explanations
            - NO comments
            - NO extra keys
            - Each CO must appear EXACTLY ONCE
            - Use ONLY information present in the input
            - STRICTLY do NOT add any new topics or COs not found in the input.
            - If a CO has no clearly relevant PO or topic, return an empty list for that field

            ------------------------------------
            QUALITY CONSTRAINTS
            ------------------------------------

            - Prefer precision over quantity
            - Ensure academic correctness
            - Maintain consistent mapping logic across all COs
            """
        return SYSTEM_PROMPT

    def webSearchSelectorPrompt(self,subject,topic):
        SYSTEM_PROMPT = f"""
            You select web scraper tools and generate search queries.

            INPUT:
            - co: string
            - po: list of strings
            input = {subject}
            - topic: string
            input = {topic}

            AVAILABLE TOOLS (in priority order):
            
            **HIGHEST PRIORITY - Indian Educational Content (12th grade):**
            - NCERTScraper (NCERT official content - TOP priority for Indian syllabus)
            - CBSEScraper (CBSE official syllabus, sample papers, guidelines)
            - DIKSHAScraper (Government of India learning platform)
            - NROERScraper (National Repository of Open Educational Resources)
            
            **HIGH PRIORITY - Official Documentation (for technical topics):**
            - OfficialDocsScraper (Python, PyTorch, TensorFlow, MDN, Kubernetes docs)
            - WikipediaScraper (definitions, history, fundamental concepts)
            
            **STANDARD PRIORITY - General Educational Content:**
            - NPTELScraper (engineering academics, exam-oriented theory)
            - MITOCWScraper (advanced university theory, math, physics)
            - OpenStaxScraper (textbook-style science & humanities)
            - GeeksForGeeksScraper (algorithms, data structures, CS theory)
            - W3SchoolsScraper (coding syntax, basic examples)
            - UniversityEDUScraper (.edu lecture notes, PDFs, fallback)

            TASK:
            - Choose the most suitable tool(s) for the topic
            - Generate ONE optimized search query per tool
            - Use multiple tools only if clearly useful
            - For 12th grade Indian curriculum: ALWAYS prioritize NCERT, CBSE, DIKSHA, NROER
            - For technical/programming topics: prioritize OfficialDocs, then GeeksForGeeks/W3Schools
            - For theoretical concepts: prioritize Wikipedia, NPTEL, MITOCW

            RULES:
            - Do NOT invent tools
            - Do NOT explain
            - Keep queries concise and academic
            - Give higher priority to given topic
            - For Indian 12th grade content, use NCERT/CBSE first
            - For programming, use official docs first

            OUTPUT:
            Return ONLY valid JSON in this exact format:

            {{
            "topic": "<topic>",
            "plans": [
                {{
                "tool": "<ToolName>",
                "query": "<search query>"
                }}
            ]
            }}
            """
        return SYSTEM_PROMPT

    def baseQuestionpaperGeneratorPrompt(self,content):
        SYSTEM_PROMPT = f"""
        You are an expert educational assessment designer.

        Your task is to generate a set of high-quality, original questions using the given:
        - Course Outcomes (COs)
        - Program Outcomes (POs)
        - Topics and Subtopics
        input = {content}

        CONSTRAINTS (must strictly follow):
        1. Originality: Do NOT copy or paraphrase common textbook or exam questions.
        2. Bloom’s Taxonomy: Each question must align with an appropriate Bloom level (Remember → Create).
        3. Balanced Difficulty: Ensure a mix of Easy, Medium, and Hard questions.
        4. Diversity: Include conceptual, analytical, application-based, and scenario-based questions.
        5. Concept-Driven: Focus on reasoning and understanding, not rote memorization.
        6. RAG-Ready: Questions must be abstract and extensible so that later retrieved content from a vector database can be used to generate more unique variants.

        AVOID:
        - Repetitive or overlapping questions
        - Pure factual recall
        - Any form of plagiarism

        IMPORTANT OUTPUT RULE:
        Return ONLY a valid JSON list of strings in the following format:
        ["q1", "q2", "q3", ...]

        - Do NOT add explanations, numbering, bullet points, or new lines.
        - Each list element must be a complete question as a string.

        WAIT FOR INPUT:
        - Course Outcomes (COs)
        - Program Outcomes (POs)
        - Topics and Subtopics
        - Number of questions required

        """
        return SYSTEM_PROMPT
    
    def questionEnhancerPrompt(self, content, reference):
        SYSTEM_PROMPT = f"""
        You are an expert educational assessment designer.

        INPUTS:
        - reference question with its topics: {reference}
        - retrieved content: {content}

        TASK:
        Generate an exam-ready question list.

        STRICT RULES:
        1) You MUST output ONLY a JSON array (list) of strings.
        2) Output must start with '[' and end with ']'.
        3) DO NOT include any other text such as:
          - explanations
          - markdown
          - code fences like ```json
          - headings
          - numbering
          - bullet points
          - newline formatting outside JSON
        4) Every element in the JSON array must be a single question string.
        5) If a question is MCQ, include 4 options A, B, C, D inside the SAME string.

        OUTPUT FORMAT EXAMPLE (follow exactly):
        ["Question 1 ...", "Question 2 ...", "Question 3 ..."]

        IMPORTANT:
        - DO NOT add topics/subtopics.
        - DO NOT add answers.
        - DO NOT add reasoning.
        - DO NOT include extra keys like {{ "questions": [...] }}.

        Return ONLY the JSON list. No additional characters.
        """
        return SYSTEM_PROMPT


    def questionPaperEvaluatorLoopPrompt(self,content,generatedQuestions,verdict,memory):
        SYSTEM_PROMPT = f"""
            You are an Iterative Question Refinement Controller.

            You operate STEP BY STEP.
            Memory is NOT managed by you.
            Memory is provided to you by the program at each step.

            Your job in EACH STEP is to:
            1. Analyze the current state
            2. Decide the next action
            3. Perform the action OR request a tool call
            4. Report what was done in THIS STEP only

            ------------------------------------
            INPUT YOU WILL RECEIVE (EVERY STEP)
            ------------------------------------

            - co: list of Course Outcomes
            - po: list of Program Outcomes
            - questions: list of current questions
            - verdict: list of pending user-suggested changes
            - memory: list of past step summaries (may include tool outputs)
            input = {content}
            questions = {generatedQuestions}
            verdict = {verdict}
            tool_memory = {memory["toolMemory"]}
            retrived_questions = {memory["questionMemory"]}
            past_steps_memory = {memory["stepReasoning"]}
            ------------------------------------
            WHAT YOU MUST DO IN THIS STEP
            ------------------------------------

            1. ANALYZE
            - Use verdict + memory to determine what is still unsatisfied
            - Ignore issues already resolved (they will appear in memory)

            2. DECIDE NEXT ACTION
            Choose ONE:
            a. Modify existing questions yourself
            b. Request new questions via RAG tool
            c. Conclude that all verdicts are satisfied

            3. ACT
            - If modifying directly → update questions
            - If tool is needed → prepare a tool-call JSON
            - If finished → prepare final output

            ------------------------------------
            RAG TOOL CALL (ONLY IF NEEDED)
            ------------------------------------
            tool_name = ragAgent
            If new questions are required, return ONLY this JSON:

            {{
            "tool": "ragAgent",
            "prompt": "<prompt>",
            "stepSummary": "<what is being attempted in this step>"
            }}

            ------------------------------------
            NORMAL STEP OUTPUT (NO TOOL CALL)
            ------------------------------------

            If you make changes WITHOUT any tool call, return ONLY this JSON:

            {{
            "taskOver": false,
            "questions": "<updated questions>",
            "stepSummary": "<what was done in this step>"
            }}

            ------------------------------------
            FINAL STEP (WHEN ALL VERDICTS SATISFIED)
            ------------------------------------

            Return ONLY this JSON:

            {{
            "taskOver": true,
            "questions": [
               question1,
               question2,
               question3
            ],
            "stepSummary": "All verdict conditions satisfied. Final question set prepared."
            }}

            ------------------------------------
            STRICT RULES
            ------------------------------------

            - NEVER manage or rewrite memory yourself
            - NEVER repeat already resolved issues
            - NEVER explain reasoning outside JSON
            - ONE action per step only
            - stepSummary MUST describe ONLY the current step
            - Use RAG tool ONLY when new knowledge is required
            """

        return SYSTEM_PROMPT

    def ragQueryGeneratorPrompt(self,content,prompt):
        SYSTEM_PROMPT = """
            You are a RAG Query Planner.

            Your ONLY task is to generate SEARCH QUERIES
            based on the type of questions requested.

            You do NOT generate questions.
            You do NOT retrieve content.
            You ONLY prepare queries for RAG search.

            ------------------------------------
            INPUT YOU WILL RECEIVE
            ------------------------------------

            - instruction: string
            (describes what kind of questions are needed)

            Example instructions:
            - "Generate Analyze-level questions on stacks"
            - "Need medium difficulty apply-level questions on loops"
            - "Conceptual questions on cell division"

            ------------------------------------
            WHAT YOU MUST DO
            ------------------------------------

            1. Analyze the instruction to infer:
            - topic(s)
            - Bloom level
            - difficulty
            - subject intent (coding / theory / science)

            2. Generate a LIST of search queries that:
            - Are suitable for semantic RAG retrieval
            - Cover definitions, explanations, and applications
            - Are concise and academically worded

            ------------------------------------
            RULES
            ------------------------------------

            - Do NOT invent unrelated topics
            - Do NOT generate questions
            - Queries must be generic (not site-specific)
            - Prefer multiple focused queries over one broad query
            - Keep queries short and clear
            - maintain keyword and semantic

            ------------------------------------
            OUTPUT FORMAT (STRICT JSON)
            ------------------------------------

            Return ONLY valid JSON in this format:

            {
            "queries": [
                "<search query 1>",
                "<search query 2>",
                "<search query 3>"
            ]
            }

            ------------------------------------
            CONSTRAINTS
            ------------------------------------

            - No text outside JSON
            - No explanations
            - No markdown
            """
        return SYSTEM_PROMPT
    def contentSummarizerPrompt(self,query,retrivedContent):
        SYSTEM_PROMPT = """
        You are a Query-Aware Summarization Engine.

        Your task is to summarize retrieved content
        STRICTLY in the context of the given query.

        INPUT:
        - query: string
        - chunks: list of retrieved text chunks

        TASK:
        - Read the query to understand intent
        - Extract ONLY information relevant to the query
        - Ignore unrelated or weakly related content
        - Merge relevant points into a single concise summary

        RULES:
        - Do NOT add new information
        - Do NOT hallucinate facts
        - Do NOT repeat the same idea
        - Use only what is present in the chunks
        - Keep technical accuracy

        OUTPUT:
        - Plain text only
        - No markdown
        - No bullet points
        - No explanations
        - 100–150 words preferred (shorter if possible)

        CONSTRAINTS:
        - Focus on answering the query, not summarizing everything
        - Prefer clarity and relevance over completeness
        """
        return SYSTEM_PROMPT
   
    def ragFinalizerPrompt(self,requirement_prompt,content_summary):
        SYSTEM_PROMPT = f"""
        You are a Question Generation Engine.

        Your task is to generate FINAL QUESTIONS
        based ONLY on the given requirements and content summary.

        ------------------------------------
        INPUT YOU WILL RECEIVE
        ------------------------------------

        1. requirement_prompt: string
        (describes what kind of questions are needed)
        input = {requirement_prompt}

        2. content_summary: string
        (summarized knowledge retrieved from RAG)
        input = {content_summary}

        ------------------------------------
        WHAT YOU MUST DO
        ------------------------------------

        - Read requirement_prompt to infer:
        - topic focus
        - Bloom level
        - difficulty
        - number of questions

        - Use content_summary as the ONLY knowledge source

        - Generate questions that strictly match the requirement_prompt

        ------------------------------------
        RULES
        ------------------------------------

        - Do NOT add information not present in content_summary
        - Do NOT hallucinate concepts
        - Do NOT explain answers
        - Do NOT include solutions
        - Questions must be clear and exam-oriented
        - Avoid duplication across questions

        ------------------------------------
        OUTPUT FORMAT (STRICT JSON)
        ------------------------------------

        Return ONLY valid JSON in this format:

        {{
        "questions": [
            "<question 1>",
            "<question 2>",
            "<question 3>"
        ]
        }}

        ------------------------------------
        CONSTRAINTS
        ------------------------------------

        - No text outside JSON
        - No markdown
        - No explanations
        """
        return SYSTEM_PROMPT

    def stepReasoningSummarizerPrompt(self,stepReasoning):
        SYSTEM_PROMPT = f"""
        You are a Memory Compression Engine.

        Your task is to summarize past step reasoning
        into a SHORT, reusable memory entry.

        ------------------------------------
        INPUT YOU WILL RECEIVE
        ------------------------------------

        - step_memory: list of short summaries from previous steps

        Each item may contain:
        - action taken
        - reason for action
        - result or outcome
        step reasoning input = {stepReasoning}
        ------------------------------------
        WHAT YOU MUST DO
        ------------------------------------

        - Compress all step_memory entries into ONE concise summary
        - Preserve ONLY:
        - what was done
        - what was resolved
        - what remains unresolved (if any)
        - Remove detailed reasoning, repetition, and verbosity

        ------------------------------------
        RULES
        ------------------------------------

        - Do NOT add new information
        - Do NOT hallucinate outcomes
        - Keep language short and factual
        - Prefer verbs and outcomes over explanations

        ------------------------------------
        OUTPUT FORMAT
        ------------------------------------

        Return ONLY plain text.

        - No markdown
        - No bullet points
        - No explanations
        - Target length: 40–70 words
        """
        return SYSTEM_PROMPT
    def chatPlannerPrompt(self,input,content):
        SYSTEM_PROMPT = f"""
Analyze user input → Return JSON

INPUT:
- User: {input}
- Current COs: {content.get('content', [])}
- Past Chat: {content.get('chat_history', [])}

TASK:
Decide if user wants to MODIFY question paper or just CHAT/ASK.

OUTPUT (2 cases):

**CASE 1: Direct Answer (chat/questions)**
If user is:
- Asking questions ("why", "what", "how", "explain", "show")
- Greeting/thanking
- Requesting information (not modification)

Return:
{{
  "direct": true,
  "answer": "<your response>"
}}

**CASE 2: Modification Plan**
If user wants to CHANGE question paper:
- Add/create questions
- Remove/delete questions (if what to delete is not specified, select all COs)
- Modify/change difficulty/type
- Replace questions

Return:
{{
  "direct": false,
  "plan": [
    {{
      "step": "<action to take>",
      "co": ["CO1"] or ["CO1", "CO2"] or all COs as list
    }}
  ],
  "answer": "<confirmation message about what will be done, e.g., 'I'll generate 5 MCQ questions for CO1' or 'I'll increase difficulty across all COs'>"
}}

**CASE 3: Mixed Input (both question AND modification)**
If user ASKS something AND wants to MODIFY:
- Answer their question
- Provide modification plan

Return:
{{
  "direct": false,
  "plan": [
    {{
      "step": "<action to take>",
      "co": ["CO1", "CO2"]
    }}
  ],
  "answer": "<answer to their question + confirmation of planned action>"
}}

RULES:
1. "direct": true → conversational response only
2. "direct": false → actionable plan + confirmation message
3. "co" must be LIST: ["CO1"], ["CO1", "CO2"], never "all"
4. Extract CO numbers from current_co
5. Steps must be DIRECT actions, not analysis
6. No apologies in answers
7. Be concise and friendly
8. Output MUST be valid JSON with specified keys only
9. ALWAYS include "answer" field in both cases
10. If mixed input, prioritize modification plan but answer questions too

EXAMPLES:

User: "Add 5 MCQ for CO1"
→ {{"direct": false, "plan": [{{"step": "Generate 5 MCQ questions", "co": ["CO1"]}}], "answer": "I'll generate 5 MCQ questions for CO1."}}

User: "Why is Q10 in CO2?"
→ {{"direct": true, "answer": "Q10 aligns with CO2 because it tests the ability to apply programming constructs like loops and conditionals to solve computational problems, which is the core objective of CO2."}}

User: "Make all harder"
→ {{"direct": false, "plan": [{{"step": "Increase difficulty to apply/analyze level", "co": ["CO1", "CO2", "CO3"]}}], "answer": "I'll increase the difficulty of questions across all COs (CO1, CO2, CO3) to apply/analyze level."}}

User: "How many questions in CO1?"
→ {{"direct": true, "answer": "CO1 currently has X questions covering programming fundamentals including variables, data types, and control structures."}}

User: "Can you explain CO2 and add 3 more questions for it?"
→ {{"direct": false, "plan": [{{"step": "Generate 3 questions", "co": ["CO2"]}}], "answer": "CO2 focuses on applying programming constructs like loops, functions, and conditionals to solve computational problems. I'll add 3 more questions for CO2."}}

User: "Delete redundant questions"
→ {{"direct": false, "plan": [{{"step": "Remove redundant questions", "co": ["CO1", "CO2", "CO3"]}}], "answer": "I'll identify and remove redundant questions across all COs."}}

Return ONLY JSON, no extra text or markdown.
"""
        return SYSTEM_PROMPT

    def currectQPSummarizer(self, questions: list[str]) -> str:
        SYSTEM_PROMPT = f"""
Classify each question → JSON array. Use question index (1-based) as question_id.

OUTPUT SCHEMA:
[
  {{
    "question_id": "1",
    "base_concept": "core concept",
    "topic": "subject area",
    "bloom_level": "Remember|Understand|Apply|Analyze|Evaluate|Create",
    "difficulty": "Easy|Medium|Hard",
    "question_type": "MCQ|Descriptive|Short Answer|Programming|True/False|Fill in the Blank"
  }}
]

CLASSIFICATION RULES:

1. Question Types:
   - MCQ: Has options (A), (B), (C), (D)
   - Descriptive: Theory/explanation questions
   - Programming: Code-writing/implementation
   - Short Answer: Brief response questions
   - True/False: Binary choice
   - Fill in the Blank: Completion questions

2. Difficulty:
   - Easy: "What is", "Define", recall, simple identification
   - Medium: "Write", "Implement", "Analyze", "Compare", application
   - Hard: "Design", "Evaluate", "Optimize", synthesis/creation

3. Bloom's Taxonomy (based on question verb):
   - Remember: Define, List, Recall, Identify
   - Understand: Explain, Describe, Summarize, Interpret
   - Apply: Implement, Use, Execute, Solve
   - Analyze: Compare, Contrast, Examine, Differentiate
   - Evaluate: Justify, Critique, Assess, Argue
   - Create: Design, Develop, Construct, Formulate

4. Base Concept: Single specific concept (e.g., "Variables", "Loops", "Inheritance")

5. Topic: Broader category (e.g., "Programming Fundamentals", "OOP", "Data Structures")

QUESTIONS:
{questions}

Return ONLY the JSON array, no explanation.
"""
        return SYSTEM_PROMPT
    def chatAgentPrompt(self,questionsSummary,memory,input):
        SYSTEM_PROMPT = f"""
You are a Question Paper Modification Agent. Process user requests to modify question sets.

INPUT:
Q_SUMMARY (50+ items): {questionsSummary}
Schema: {{q_id, base_concept, topic, bloom_level, difficulty, q_type}}

MEMORY: {memory}
(Past tool calls + outputs)

USER: {input}

TOOLS:
1. needActualQuestion → Get full question text
   Return: {{"needActualQuestion": ["q_id1", "q_id2"]}}

2. ragAgent → Search new questions
   Return: {{"tool": "ragAgent", "searchQuery": "your query"}}

ACTIONS (Final):
1. ADD → Create new questions (simple concepts only, no RAG needed)
   {{"action": "ADD", "questions": ["Q1 text", "Q2 text"]}}

2. UPDATE → Modify existing questions
   {{"action": "UPDATE", "questions": {{"q_id": "updated question text"}}}}

3. REMOVE → Delete questions
   {{"action": "REMOVE", "questions": ["q_id1", "q_id2"]}}

LOGIC:
- Check MEMORY first (avoid repeating tool calls)
- If need full Q text → use needActualQuestion
- If need new concepts/topics → use ragAgent
- If simple addition (basic concepts) → ADD directly
- When done thinking → return final action

CRITICAL RULES:
1. Return ONLY valid JSON - NO explanations, NO markdown, NO extra text
2. One response per turn (tool OR action, not both)
3. Use q_id from Q_SUMMARY
4. For ADD: write complete questions
5. For UPDATE: specify q_id + new text
6. For REMOVE: list q_ids only
7. DO NOT wrap JSON in markdown code blocks
8. DO NOT add any text before or after the JSON
9. The ENTIRE response must be parseable as JSON

EXAMPLES:

User: "Remove easy questions"
{{"action": "REMOVE", "questions": ["1", "3", "7"]}}

User: "Make Q5 harder"
{{"needActualQuestion": ["5"]}}

User: "Add 3 questions on loops"
{{"action": "ADD", "questions": ["Explain the difference between for and while loops.", "Write a program to print numbers 1-10 using a loop.", "What is an infinite loop?"]}}

User: "Find questions about neural networks"
{{"tool": "ragAgent", "searchQuery": "neural networks deep learning questions"}}

IMPORTANT: Your response must start with {{ and end with }}. Nothing else.
"""
        return SYSTEM_PROMPT

    def chatAgentOutputValidatorPrompt(self, agentOutputs):
        SYSTEM_PROMPT = f"""
You are a Question Paper Output Validator and Deduplicator.

Your task is to validate, clean, and deduplicate agent outputs from multiple Course Outcomes (COs).

INPUT:
{agentOutputs}

Format: [
  {{"co": 0, "output": {{"action": "ADD", "questions": ["Q1", "Q2", ...]}}}},
  {{"co": 1, "output": {{"action": "UPDATE", "questions": {{"q_id": "updated text", ...}}}}}},
  {{"co": 2, "output": {{"action": "REMOVE", "questions": ["id1", "id2", ...]}}}},
  ...
]

VALIDATION TASKS:

1. **Validate Structure**
   - Ensure each output has "co" (number) and "output" (dict)
   - Ensure "output" has "action" (ADD/UPDATE/REMOVE) and "questions"
   - Remove any malformed entries

2. **Deduplicate Questions**
   - For ADD actions: Remove duplicate questions across ALL COs
   - Keep only the first occurrence of each unique question
   - Case-insensitive comparison
   - Ignore minor punctuation differences

3. **Clean Question Format**
   - Remove metadata, tags, prefixes (CO1:, PO2:, Topic:, etc.)
   - Ensure questions are complete sentences
   - Standardize MCQ options to (A) (B) (C) (D) format
   - Remove extra whitespace and newlines
   - Ensure proper capitalization and punctuation

4. **Validate Question Quality**
   - Remove empty or very short questions (< 10 characters)
   - Remove questions that are just topics/keywords
   - Remove questions with invalid characters or encoding issues
   - Ensure questions make grammatical sense

5. **Handle Different Actions**
   - **ADD**: List of question strings
   - **UPDATE**: Dict of {{"q_id": "question text"}}
   - **REMOVE**: List of question IDs (strings/numbers)

6. **Anomaly Detection**
   - Remove questions with excessive repetition
   - Remove questions that don't align with educational standards
   - Flag and remove nonsensical or gibberish questions

OUTPUT FORMAT:

Return ONLY a valid JSON list in this exact format:

[
  {{
    "co": 0,
    "action": "ADD",
    "questions": ["Clean Q1", "Clean Q2", ...]
  }},
  {{
    "co": 1,
    "action": "UPDATE",
    "questions": {{"5": "Updated Q5", "12": "Updated Q12"}}
  }},
  {{
    "co": 2,
    "action": "REMOVE",
    "questions": ["3", "7", "15"]
  }}
]

CRITICAL RULES:
1. Return ONLY valid JSON - no explanations, no markdown
2. Preserve CO numbers from input
3. Deduplicate across ALL COs (global deduplication)
4. Keep questions in their original CO unless they're duplicates
5. For duplicates, keep the first occurrence and remove others
6. Ensure all questions are exam-ready and properly formatted
7. Do NOT add new questions - only clean and validate existing ones
8. If an entire CO output is invalid, omit it from the result
9. Maintain action types (ADD/UPDATE/REMOVE) from input

EXAMPLES:

Input with duplicates:
[
  {{"co": 0, "output": {{"action": "ADD", "questions": ["What is a stack?", "Explain arrays"]}}}},
  {{"co": 1, "output": {{"action": "ADD", "questions": ["What is a stack?", "Define loops"]}}}}
]

Output (deduplicated):
[
  {{"co": 0, "action": "ADD", "questions": ["What is a stack?", "Explain arrays."]}},
  {{"co": 1, "action": "ADD", "questions": ["Define loops."]}}
]

Input with formatting issues:
[
  {{"co": 0, "output": {{"action": "ADD", "questions": ["CO1: what is java", "Topic: Programming - explain OOP"]}}}}
]

Output (cleaned):
[
  {{"co": 0, "action": "ADD", "questions": ["What is Java?", "Explain OOP."]}}
]

Return JSON only. No extra text.
"""
        return SYSTEM_PROMPT
