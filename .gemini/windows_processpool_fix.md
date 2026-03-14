# Windows ProcessPoolExecutor Fix

## Problem
On Windows, `ProcessPoolExecutor` uses the `spawn` method to create new processes (instead of `fork` on Unix). This means the child process re-imports the main module, which would re-execute all module-level code.

## Error Message
```
RuntimeError:
    An attempt has been made to start a new process before the
    current process has finished its bootstrapping phase.
    
    This probably means that you are not using fork to start your
    child processes and you have forgotten to use the proper idiom
    in the main module:
    
        if __name__ == '__main__':
            freeze_support()
            ...
```

## Solution
Wrap all execution code in `if __name__ == '__main__':` block.

### Before (Broken on Windows):
```python
from agents.questionPaperGeneratorAgent.questionPaperGenerator import QuestionPaperGenerator

text = """..."""

# ❌ This runs when module is imported by child processes
qpgen = QuestionPaperGenerator(collectionName="test_aids_collection_v1")
output = qpgen.demoQuestionpaperGenerator(text=text, filePath="")
```

### After (Works on Windows):
```python
from agents.questionPaperGeneratorAgent.questionPaperGenerator import QuestionPaperGenerator

# ✅ Module-level constants are OK
text = """..."""

# ✅ This only runs in the main process
if __name__ == '__main__':
    qpgen = QuestionPaperGenerator(collectionName="test_aids_collection_v1")
    output = qpgen.demoQuestionpaperGenerator(text=text, filePath="")
```

## Why This Happens

1. **Windows Process Creation:**
   - Windows doesn't support `fork()` system call
   - Uses `spawn` instead, which starts a fresh Python interpreter
   - The new interpreter re-imports the main module

2. **Without `if __name__ == '__main__':`:**
   - Main process starts
   - Creates ProcessPoolExecutor
   - Worker process starts
   - Worker re-imports `test.py`
   - Worker tries to create another ProcessPoolExecutor
   - **Infinite loop / crash**

3. **With `if __name__ == '__main__':`:**
   - Main process: `__name__` is `'__main__'` → code runs
   - Worker process: `__name__` is `'test'` → code skipped
   - **Works correctly**

## Files Fixed

1. **`test.py`** - Wrapped main execution in `if __name__ == '__main__':`

## Status

✅ **ProcessPoolExecutor now works correctly on Windows!**

The script is running successfully with true parallel processing across 4 worker processes.
