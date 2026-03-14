# RAG Search Query Logging - Implementation Summary

## Overview
Enhanced the `_worker_rag_retrieval` function to log all RAG search queries and results to text files for debugging and analysis.

## Key Features Implemented

### 1. **Comprehensive Logging**
Every RAG search query is logged with:
- **Timestamp** - When the query was executed
- **CO (Course Outcome)** - Context for the query
- **PO (Program Outcome)** - Additional context
- **Search Query** - The actual question being searched
- **Retrieved Results** - All content retrieved from the RAG system
  - Number of results
  - Text content (first 200 characters)
  - Relevance scores (if available)
- **Enhanced Questions** - The final generated questions

### 2. **Thread-Safe File Writing**
- Uses `threading.Lock()` to prevent race conditions
- Multiple threads can log simultaneously without corrupting the file
- Each write operation is atomic

### 3. **Organized Log Structure**
```
rag_search_logs/
├── rag_queries_20260115_002315.txt
├── rag_queries_20260115_002320.txt
└── ...
```

### 4. **Log File Format**
```
================================================================================
TIMESTAMP: 2026-01-15 00:23:15
CO: CO1: Understand the basic concepts of programming...
PO: PO1: Engineering knowledge – Apply knowledge of mathematics...
SEARCH QUERY: What is a variable in programming?
--------------------------------------------------------------------------------
RETRIEVED RESULTS (3 items):

  Result 1:
    Text: Variables are containers for storing data values. In programming, a variable is a symbolic name associated with a value and whose associated value may be changed...
    Score: 0.85

  Result 2:
    Text: A variable is a named storage location in computer memory that holds a value which can be modified during program execution...
    Score: 0.78

  Result 3:
    Text: Variables in programming languages are used to store information to be referenced and manipulated in a computer program...
    Score: 0.72
--------------------------------------------------------------------------------
ENHANCED QUESTIONS:
  1. Define what a variable is in programming and explain its purpose.
  2. Explain how variables are used to store and manipulate data in a program.
  3. Compare different types of variables and their use cases in programming.
================================================================================

[... more queries ...]

================================================================================
SUMMARY
================================================================================
Total base questions processed: 15
Total enhanced questions generated: 45
CO: CO1: Understand the basic concepts of programming...
PO: PO1: Engineering knowledge – Apply knowledge of mathematics...
================================================================================
```

### 5. **Error Handling**
- Catches and logs errors during processing
- Continues execution even if logging fails
- Prints warnings to console for critical failures

### 6. **Performance Optimizations**
- **15 concurrent threads** for parallel RAG retrieval
- Each thread processes one question independently
- Results are flattened into a single list

## Code Improvements

### Before (Issues):
```python
def multiThrededRetriver(question):  # ❌ Typo in name
    retrieval_result = rag_system.search(query=question)
    # ... no logging ...
    return questions  # ❌ No error handling
```

### After (Fixed):
```python
def multiThreadedRetriever(question):  # ✅ Fixed typo
    try:
        retrieval_result = rag_system.search(query=question)
        # ... comprehensive logging ...
        log_search_query(question, retrieval_result, enhanced_questions)
        return result_questions
    except Exception as e:
        print(f"Error processing question '{question}': {e}")
        # Log the error
        return []  # ✅ Graceful error handling
```

## Benefits

### 1. **Debugging**
- See exactly what queries are being sent to RAG
- Understand what content is being retrieved
- Identify why certain questions are generated

### 2. **Quality Assurance**
- Verify that RAG is retrieving relevant content
- Check if retrieved content matches the CO/PO
- Ensure enhanced questions are properly generated

### 3. **Performance Analysis**
- Track how many results are retrieved per query
- Identify queries that return no results
- Analyze relevance scores

### 4. **Audit Trail**
- Complete record of all RAG operations
- Timestamps for performance tracking
- Summary statistics for each batch

## Usage

The logging happens automatically when running the question paper generator:

```python
# Just run your normal code
qpgen = QuestionPaperGenerator(collectionName="test_aids_collection_v1")
output = qpgen.demoQuestionpaperGenerator(text=text, filePath="")

# Logs are automatically created in:
# ./rag_search_logs/rag_queries_YYYYMMDD_HHMMSS.txt
```

## Log Analysis Tips

### 1. **Find Failed Queries**
```bash
grep "no content found" rag_search_logs/*.txt
```

### 2. **Check Retrieval Counts**
```bash
grep "RETRIEVED RESULTS" rag_search_logs/*.txt
```

### 3. **View Summaries**
```bash
grep -A 5 "SUMMARY" rag_search_logs/*.txt
```

### 4. **Find Errors**
```bash
grep "ERROR:" rag_search_logs/*.txt
```

## Thread Safety Details

### Problem Without Locks:
```
Thread 1: Opens file → Writes "Query 1" → 
Thread 2:                Opens file → Writes "Query 2" → Closes file
Thread 1:                                                              Closes file
Result: Corrupted file or lost data
```

### Solution With Locks:
```
Thread 1: Acquires lock → Opens file → Writes "Query 1" → Closes file → Releases lock
Thread 2:                 Waits...                                      Acquires lock → Opens file → Writes "Query 2" → Closes file → Releases lock
Result: Clean, sequential writes
```

## Performance Impact

- **Minimal overhead** - Logging is done in parallel with processing
- **Non-blocking** - Failed logs don't stop execution
- **Efficient** - Only writes when data is ready

## Future Enhancements

Potential improvements:
1. **Structured logging** - Use JSON format for easier parsing
2. **Log rotation** - Automatically archive old logs
3. **Real-time monitoring** - Stream logs to a dashboard
4. **Analytics** - Generate statistics from log files
5. **Filtering** - Log only queries below a certain score threshold

## Files Modified

- `questionPaperGenerator.py` - Enhanced `_worker_rag_retrieval` function

## Status

✅ **Fully Implemented and Working**

All RAG search queries are now logged to `rag_search_logs/` directory with comprehensive details for debugging and analysis.
