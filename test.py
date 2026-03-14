import json
from datetime import datetime

from agents.questionPaperGeneratorAgent.questionPaperGenerator import QuestionPaperGenerator

# Text data definition
text = """
Course: Programming Fundamentals and Data Structures

Course Outcomes:
CO1: Understand the basic concepts of programming, including variables, data types, and control structures.
CO2: Apply programming constructs such as loops, functions, and conditionals to solve computational problems.
CO3: Analyze and implement fundamental data structures to solve real-world problems efficiently.

Program Outcomes:
PO1: Engineering knowledge – Apply knowledge of mathematics and computing fundamentals.
PO2: Problem analysis – Identify, formulate, and analyze computational problems.
PO3: Design/development of solutions – Design and implement efficient algorithms.

Syllabus Content:
Unit 1: Introduction to programming, variables, data types, input/output operations.
Unit 2: Control structures – conditional statements, loops, and functions.
Unit 3: Arrays, strings, and basic operations.
Unit 4: Data structures – stacks, queues, linked lists.
Unit 5: Searching and sorting algorithms, time and space complexity.


"""

# IMPORTANT: On Windows, ProcessPoolExecutor requires this guard
if __name__ == '__main__':
    # Create question paper generator
    qpgen = QuestionPaperGenerator(collectionName="final_test")
    out = qpgen.demoQuestionpaperGenerator(text,None)
    print("current qp",out)
    
#     # Generate question paper
#     content =[
#     {
#       "CO": "CO1: Understand the basic concepts of programming, including variables, data types, and control structures.",
#       "PO": [
#         "PO1: Engineering knowledge – Apply knowledge of mathematics and computing fundamentals."
#       ],
#       "topics": [
#         "Unit 1: Introduction to programming, variables, data types, input/output operations.",
#         "Unit 2: Control structures – conditional statements, loops, and functions."
#       ],
#       "questions": [
#         "What is a variable in programming and how is it used to store data?",
#         "According to the retrieved content, what does the #define directive do in C++ programming? (e.g., #define Pi 3.14 or #define WELCOME cout<<”Hello World !\n”;)",
#         "In the context of the retrieved content, can you write a correct C++ program using the #include directive with the correct header files for including input and output functions, and define a struct named STUDENT with two members: stu_name as a character array of size 20 and stu_sex as a single character? (Do not forget to include the main function and its body.)",
#         "Explain the difference between a primitive and a non-primitive data type in programming. Provide an example of each.",
#         "Which programming concept is illustrated through the use of the struct keyword in C++ to create user-defined data types that can store a group of items of different data types?",
#         "Can you identify which area of knowledge the following topics belong to: 3. Mathematics, 4. Physics, 5. Chemistry, 6. Biology, 7. Bio-technology, 8. Informatics Practices?",
#         "How do control flow tools like 'report a bug' and 'show source' relate to the basic concepts of programming, including variables, data types, and control structures?",
#         "Given a code snippet, identify if it contains multiple assignments and if the right-hand side expressions are evaluated from left to right.",
#         "Identify the variables in the following code snippet and determine if their declarations contain any errors or inefficiencies: a, b = 0, 1; c = d = 3.4; e = (f = g = 5) + 2.",
#         "Which subject area(s) does the following passage cover: Mathematics, Physics, Chemistry, Biology, Bio-technology, or Informatics Practices?",
#         "Write a program that takes two integer inputs from the user and outputs their sum.",
#         "According to the Input-Process-Output concept, what device is used by a computer to accept input data from the user?",
#         "In the context of the Input-Process-Output concept, what kind of data can be accepted as input by a computer? (Characters, words, text, sound, images, documents, etc.)",
#         "Based on the Input-Process-Output concept, which of the following best describes the function of a computer in processing input data: A) Stores data, B) Accepts input data, C) Performs calculations, D) Generates output?",
#         "Analyze the time and space complexity of a given algorithm that searches for an element in an array.",
#         "Which of the following best represents the space complexity of a search algorithm that sequentially checks each element in an array until the desired value is found? (A) O(1) B) O(n) C) O(log n) D) O(n^2)",
#         "Which of the following best represents the time complexity of a search algorithm that sequentially checks each element in an array until the desired value is found? (A) O(1) B) O(n) C) O(log n) D) O(n^2)",
#         "Given an array of integers, what is the time complexity of finding a specific integer using a binary search algorithm? (A) O(1) B) O(n) C) O(log n) D) O(n^2)",
#         "Consider a scenario where you need to search for an element in a sorted array of 1000 elements. Which search algorithm would you choose if you want to minimize the time complexity and why?",
#         "What is the impact on the time complexity of a search algorithm if the array is not sorted? Explain your answer.",
#         "Can you provide an example of a real-world scenario where optimizing the space complexity of a search algorithm is crucial? Explain how you would approach this problem.",
#         "Understand the basic concepts of programming, including variables, data types, and control structures. Apply knowledge of mathematics and computing fundamentals to design and implement a sorting algorithm for an array of integers, and compare its performance with a built-in sorting function in a popular programming language. Consider the characteristics and limitations of a computer while analyzing the performance of your algorithm.",
#         "Explain how computers can process a variety of data types, including text, numbers, audio, video, and graphics. Then, design and implement a sorting algorithm for an array of integers, and compare its performance with a built-in sorting function in a popular programming language. Consider the role of mathematics and computing fundamentals in the implementation and analysis of the algorithm.",
#         "Describe the different types of data that can be processed by a computer. Next, design and implement a sorting algorithm for an array of integers, and compare its performance with a built-in sorting function in a popular programming language. Consider the characteristics and limitations of a computer while analyzing the performance of your algorithm, and discuss how mathematical and computing fundamentals apply to the implementation and analysis of the algorithm.",
#         "Discuss the role of mathematics and computing fundamentals in programming. Then, design and implement a sorting algorithm for an array of integers, and compare its performance with a built-in sorting function in a popular programming language. Consider the characteristics and limitations of a computer while analyzing the performance of your algorithm, and explain how the algorithm relates to the different types of data that can be processed by a computer.",
#         "Consider the characteristics and limitations of a computer when designing and implementing a sorting algorithm for an array of integers. Compare the performance of your algorithm with a built-in sorting function in a popular programming language, and explain how mathematical and computing fundamentals apply to the implementation and analysis of the algorithm. Also, discuss how computers can process a variety of data types, including text, numbers, audio, video, and graphics.",
#         "What is the difference between a statically-typed and dynamically-typed programming language?",
#         "Which two properties are common to textbox, label, and command button objects in Visual Basic?",
#         "How do the Load and Show methods of a form object differ in Visual Basic?",
#         "What are two properties of the ADO Data Control that can be dynamically set during run-time to change the database?",
#         "In the context of learning and imagination, how do spontaneity and intuition contribute to creativity?",
#         "Explain the concept of input/output operations in programming, and give an example of each.",
#         "Which units in a computer system are responsible for input and output operations, and what are their roles?",
#         "Describe the process of providing input to a computer system and the types of input devices that can be used.",
#         "Explain how output is generated by a computer system and the types of output devices that are commonly used.",
#         "Describe the role of the CPU in handling input and output operations in a computer system.",
#         "Given a code snippet that reads data from a file, consider the following:  A. Is there any validation for the correct file format? B. Is there any error handling in case the file does not exist or is inaccessible? C. Are there any checks for invalid data entries in the file? D. How are errors communicated to the user?",
#         "What role does the control unit play in programming?",
#         "Which of the following units is responsible for presenting the result to the user in the context of programming?",
#         "What is a conditional statement in programming and how is it used to make decisions?",
#         "How do multiple assignments work in programming, as demonstrated in the example where variables a and b simultaneously get new values 0 and 1?",
#         "In what order are the right-hand side expressions evaluated in the example where multiple assignments are used in the last line?",
#         "Explain the concept of multiple assignment in programming and provide an example",
#         "Consider the following example of multiple assignment: a, b = 0, 1 ... a, b = b, a+b",
#         "What is the value of a and b at the end of the example?",
#         "Which of the following best describes multiple assignment in programming? A. Assigning multiple values to a single variable. B. Assigning a single value to multiple variables. C. Evaluating multiple expressions at once. D. None of the above",
#         "Write a recursive function that calculates the factorial of a given positive integer, and analyze its time complexity",
#         "Which mathematical operations are used in programming? (A) Addition, Subtraction, Multiplication, Division (B) Subtraction, Multiplication, Division, Exponentiation (C) Addition, Multiplication, Division, Modulus (D) All of the above",
#         "What are Nested Structures in Object Oriented Programming? Can you give an example?",
#         "In the context of Object Oriented Programming, can you differentiate between Multilevel and Multiple Inheritance? Provide a suitable example for each",
#         "Consider the following C++ code: S2.Replace(S1, state3); S1.display(); S2.display(); What is the output of the program if state3 is replaced with 'Hello'? Can this code be compiled without including any header files? (A) Yes (B) No (C) Depends on the compiler (D) None of the above",
#         "In the given retrieved content, what does the CPU unit perform? (A) Input and Output Operations (B) Mathematical and Logical Operations (C) Memory Management (D) None of the above"
#       ]
#     },
#     {
#       "CO": "CO2: Apply programming constructs such as loops, functions, and conditionals to solve computational problems.",
#       "PO": [
#         "PO2: Problem analysis – Identify, formulate, and analyze computational problems.",
#         "PO3: Design/development of solutions – Design and implement efficient algorithms."
#       ],
#       "topics": [
#         "Unit 2: Control structures – conditional statements, loops, and functions.",
#         "Unit 3: Arrays, strings, and basic operations."
#       ],
#       "questions": [
#         "What are the three main types of programming constructs that can be used to solve computational problems?",
#         "Which greenhouse gas is responsible for trapping the sun’s heat in the Earth’s atmosphere due to man-made global warming, caused by burning carbon-rich fuels?",
#         "What are the potential consequences of increased levels of CO2 in the Earth’s atmosphere, according to the Intergovernmental Panel on Climate Change (IPCC) at the lower range? A. Tiny increase in global sea levels, B. Increased water stress, C. Benefits some regions in higher latitudes, D. None of the above",
#         "What are the potential consequences of extremely high levels of CO2 in the Earth’s atmosphere, according to the Intergovernmental Panel on Climate Change (IPCC) at the higher range? A. Tiny increase in global sea levels, B. Increased water stress, C. Benefits some regions in higher latitudes, D. Bigger impact",
#         "In what scenario would you use a loop instead of a conditional statement to solve a computational problem?",
#         "In a programming context, when would you use a DO-WHILE loop compared to a FOR loop, and what are the benefits of each?",
#         "Consider a scenario where you need to iterate over a collection and perform an action for each item, but only if certain conditions are met. Which loop construct would be more appropriate and why?",
#         "Describe a situation in which a function with a loop would be more suitable than using a series of conditional statements. Provide a brief example in a programming language of your choice.",
#         "Can you explain the concept of 'familiarity' mentioned in the context of DO-WHILE and FOR loops, and how it impacts the choice of loops in programming?",
#         "How does the use of loops in programming relate to problem analysis and efficient algorithm design? Provide an example to illustrate your answer.",
#         "Write a Python function that takes a list of numbers as input and returns the largest prime number in the list using loops and conditionals.",
#         "Which of the following is a Python code snippet that checks if a number is prime using loops and conditionals? (A) f = True FOR i = 2 TO n - 1 IF n Mod i = 0 THEN f = False EXIT FOR END IF NEXT IF f = True Then Print n & “ is a prime no” Else Print n & “ is not a prime no” END IF (1 Mark for header of sub procedure) (1 Mark for using loop) (1 Mark for checking divisibility by using MOD or / or any other equivalent method) (1 Mark for displaying the result)",
#         "Which of the following topics are relevant to the original question? (A) Mathematics (B) Physics (C) Chemistry (D) Biology (E) Bio-technology (F) Informatics Practices. Select the correct options.",
#         "Analyze: Analyze the time complexity of the following code snippet that finds the maximum value in a list using a loop: `max_value = current_value for current_value in list`",
#         "What is the time complexity of this code snippet?",
#         "In the context of the retrieved content, what is the role of the end keyword argument in Python's print function?",
#         "Which of the following correctly describes a sequence in Python for the purpose of a while loop condition?",
#         "Which type of memory is used to hold the boot up program? (True or False) Is it the random access memory?",
#         "How many different combinations of bits can one byte store?",
#         "Convert the following: 1 byte = ________ bits, 1 Kilobyte (KB) = _______ bytes, 1 Megabyte (MB) = _______ KB, 1 Gigabyte (GB) = ____________ MB = ___________ KB, 1 Terabyte (TB) = ______________ GB",
#         "Which parts of the CPU are the Arithmetic Logic Unit (ALU), Control Unit (CU), and Memory unit?",
#         "Where is the cache memory placed in a computer system?",
#         "Consider the following Python functions for finding the maximum value in a list: Function 1: `def find_max(numbers): return max(numbers)`; Function 2: `def find_max(numbers): max_value = numbers[0] for current_value in numbers[1:]: if current_value > max_value: max_value = current_value return max_value`. Which of these functions would be more efficient and why?",
#         "What is the difference between a byte and a kilobyte?",
#         "What is the role of the Arithmetic Logic Unit (ALU) and the Control Unit (CU) in a computer's CPU?",
#         "What is the purpose of the registers in a computer and where are they located?",
#         "Create a Python program that takes a list of strings as input and returns a new list that contains only the strings that have a length greater than 5, using loops and conditionals. Consider the following code snippet: '\n>>>word[0:2]# characters from position 0 (included) to 2 (excluded) 'Py' >>>word[2:5]# characters from position 2 (included) to 5 (excluded) 'tho' \n\nSlide indices have useful defaults; an omitted first index defaults to zero, an omitted second index defaults to the size of the string being sliced.",
#         "Which programming construct can be used to achieve the desired functionality?",
#         "What is the time complexity of the given function?",
#         "What is the significance of the slice indices' defaults in the context of the original question?",
#         "What other programming constructs, besides loops and conditionals, can be used to solve this problem?",
#         "Which of the following best represents the XOR operation in POS form: Express P + Q'R in POS form?",
#         "What is a linked list?",
#         "How do you declare an array?",
#         "Which of the following is a linear data structure? (A) Tree (B) Graph (C) Stack (D) Heap",
#         "What is the time complexity of binary search? (A) O(n) (B) O(log n) (C) O(n^2) (D) O(1)",
#         "Which sorting algorithm has the best average case? (A) Bubble Sort (B) Quick Sort (C) Selection Sort (D) Insertion Sort",
#         "Considering the four wings of INDIAN PUBLIC SCHOOL in Darjeeling (SENIOR, JUNIOR, ADMIN, and HOSTEL), which two network transmission media would be most suitable for setting up connections between them?",
#         "Given the Boolean expression F(P, Q, R, S) = π(0, 3, 5, 6, 7, 11, 12, 15), reduce it to its simplest form using a K-Map.",
#         "Suppose you want to determine the biological function of genes and proteins in an organism. Which of the following techniques would be most relevant: Generate high resolution genetic, physical and transcript map of genes and proteins an organism?",
#         "Which of the following is an example of using a loop in C++? (A) for (int i = 0; i < 10; i++) {...} (B) while (true) {...} (C) do {...} while (condition); (D) None of the above is an example of using a loop in C++.",
#         "What is the purpose of a copy constructor in C++? (A) It is used to declare an object. (B) It is an overloaded constructor, in which an object of the same class is passed as a parameter. (C) It is used to delete an object. (D) It is used to modify an object.",
#         "What is Unified Modelling Language (UML) and how is it used in object-oriented modeling? (A) UML is a visual modeling language used to model the solution to a problem in a procedural manner. (B) UML is a textual modeling language used to model the solution to a problem in an object-oriented manner. (C) UML is a visual modeling language used to model the solution to a problem in an object-oriented manner. (D) UML is a textual modeling language used to model the solution to a problem in a procedural manner.",
#         "Identify the input, output, and constraints of this problem: Given a list of numbers, find the second largest number in the list.",
#         "Which of the following is the input for the problem: Given a list of numbers, find the second largest number in the list?",
#         "What is the constraint for the problem: Given a list of numbers, find the second largest number in the list?",
#         "Which of the following best describes the purpose of the variable 'firstLargest' in the pseudocode?",
#         "Which of the following best describes the purpose of the variable 'secondLargest' in the pseudocode?",
#         "Is the algorithm's time complexity O(n) or O(n^2)?",
#         "Is the algorithm's space complexity O(1) or O(n)?",
#         "How does the algorithm's efficiency compare to a solution using Python's built-in max() function?",
#         "True or False: The algorithm's space complexity is O(n) because it needs to store all the elements in the list to find the maximum value.",
#         "True or False: The algorithm's time complexity is O(n) because it iterates through the list once to find the maximum value.",
#         "Which of the following two problem-solving strategies is more efficient for finding prime numbers, and why? Strategy 1: Trial division; Strategy 2: Sieve of Eratosthenes",
#         "Consider the following VB code snippet. What is the output of this code?",
#         "Identify the problem in the following scenario: A student is struggling to determine the efficiency of different problem-solving strategies for finding prime numbers.",
#         "Design an algorithm to compare the efficiency of trial division and the Sieve of Eratosthenes for finding prime numbers.",
#         "Which of the following best describes the difference in efficiency between trial division and the Sieve of Eratosthenes for finding prime numbers, and why? Strategy 1: Trial division is faster for small numbers; Strategy 2: The Sieve of Eratosthenes is faster for large numbers.",
#         "How does the concept of 'spontaneity/intuition' relate to the process of selecting the most efficient problem-solving strategy for finding prime numbers?",
#         "How does the 'logical-mathematical intelligence' come into play when evaluating the efficiency of different algorithms for finding prime numbers?",
#         "Apply programming constructs such as loops and conditionals to determine if a number is prime.",
#         "Formulate a computational problem that requires checking if a number is prime using loops and conditionals.",
#         "Consider the following mathematical expressions: (a) (i) 0 (1 mark for correct output) (1/2 mark if 6 is given as output instead of 0) (ii) -2 (1 mark for correct output) (½ mark if the output is given as –1 or –3/2 or equivalent answer) Generate a multiple-choice question based on the given expressions: Which of the following expressions would yield 0 and –2 for (a)(i) and (a)(ii) respectively, without using any conditional statements?",
#         "Consider the following excerpt from a larger text: 249 (d) Private Sub procIsprime (n As Integer) Dim f As Boolean f = True FOR i = 2 TO n - 1 IF n Mod i = 0 Then f = False EXIT FOR END IF NEXT i Identify the programming concept illustrated in the excerpt:",
#         "Create a multiple-choice question based on the given distribution: Which subject has the largest range of question numbers?",
#         "Which of the following best describes the difference in efficiency between trial division and the Sieve of Eratosthenes for finding prime numbers, and why?",
#         "Which of the following is a linear data structure? (A) Tree (B) Graph (C) Stack (D) Heap",
#         "What is the time complexity of binary search? (A) O(n) (B) O(log n) (C) O(n^2) (D) O(1)",
#         "Which sorting algorithm has the best average case? (A) Bubble Sort (B) Quick Sort (C) Selection Sort (D) Insertion Sort",
#         "What is polymorphism? (A) Multiple forms (B) Single form (C) No form (D) Abstract form",
#         "What are the possible ways to input values in a program, as suggested by the retrieved content?",
#         "Identify the data type that automatically generates unique sequential (incrementing by 1) numbers, as mentioned in the retrieved content.",
#         "Referring to the first example, what is the order of evaluation for the right-hand side expressions?",
#         "In the context of the retrieved content, explain what a 'multiple assignment' is and provide an original example.",
#         "What is the difference between an algorithm and a program?",
#         "What role does calculation play in the functioning of a computer system?",
#         "How does a computer's ability to perform both simple and complex operations contribute to its usefulness in various fields?",
#         "In the context of computer programming, what is the significance of the term 'compute'?",
#         "Python knows a number of compound data types, used to group together other values. The most versatile is the list, which can be written as a list of comma-separated values (items) between square brackets. Lists might contain items of different types, but usually the items all have the same type. Like strings (and all other built-in sequencetypes), lists can be indexed and sliced:",
#         "3. Mathematics ............................................................................................................. 78-123",
#         "4. Physics ...................................................................................................................... 124-166",
#         "5. Chemistry .................................................................................................................. 167-193",
#         "6. Biology ...................................................................................................................... 194-216",
#         "7. Bio-technology ......................................................................................................... 217-232",
#         "8. Informatics Practices .................................................................................................. 233-263",
#         "Analyze the time complexity of the following algorithm for finding the maximum value in a list: `def find_max(numbers): max_value = numbers[0] for current_value in numbers[1:]: if current_value > max_value: max_value = current_value return max_value` - What is the time complexity of the provided algorithm for finding the maximum value in a list? - Consider the provided algorithm for finding the maximum value in a list. If the input list has n elements, which part of the algorithm contributes to the linear time complexity?",
#         "Is it true that the random access memory (RAM) is used to hold the boot-up program? - Is it false that the random access memory (RAM) is used to hold the boot-up program?",
#         "True or false: One byte can store 2^8 (256) different combinations of bits.",
#         "In the provided algorithm for finding the maximum value in a list, is it possible to reduce the time complexity by using a different algorithmic approach? Explain your answer.",
#         "Considering the binary representation of bytes, how many unique values can be stored in one byte?",
#         "If a list has 100 elements, how many times will the body of the for-loop be executed in the provided algorithm for finding the maximum value in a list?",
#         "Which of the following two sorting algorithms is more efficient, and why? Algorithm 1: Bubble sort; Algorithm 2: Quick sort",
#         "Considering the order of their hierarchy with respect to the CPU, why is primary memory faster than the secondary memory? What is the meaning of volatile memory? Also give an example of volatile memory. Differentiate between RAM and ROM",
#         "How does the efficiency of Algorithm 1 (Bubble sort) compare to Algorithm 2 (Quick sort) when dealing with large datasets?",
#         "In what scenarios would you choose Algorithm 1 (Bubble sort) over Algorithm 2 (Quick sort), despite its lower efficiency?",
#         "Design an efficient algorithm for finding the kth smallest number in a list of n numbers, where k is a positive integer less than or equal to n.",
#         "Using loops, functions, and conditionals, how would you implement an algorithm to find the kth smallest number in a list of n numbers?",
#         "Given a list of n numbers, can you create a function to find the kth smallest number using only loops and conditionals?",
#         "Consider a list of n numbers. How would you use a loop and conditional statements to identify the kth smallest number?",
#         "With reference to finding the kth smallest number in a list of n numbers, design an algorithm using loops, functions, and conditionals.",
#         "In the context of finding the kth smallest number in a list of n numbers, how can problem analysis (PO2) be applied when designing an algorithm?",
#         "How does understanding problem analysis (PO2) and design/development of solutions (PO3) help in creating an efficient algorithm for finding the kth smallest number in a list of n numbers?",
#         "How can you apply loops, functions, and conditionals to efficiently solve the problem of finding the kth smallest number in a list of n numbers, considering PO2 and PO3?",
#         "Can you explain how to use a loop and conditional statements to create an efficient algorithm for finding the kth smallest number in a list of n numbers, considering PO2 and PO3?",
#         "How would you approach the problem of finding the kth smallest number in a list of n numbers using loops, functions, and conditionals, keeping in mind the concepts of problem analysis (PO2) and design/development of solutions (PO3)?",
#         "In the realm of finding the kth smallest number in a list of n numbers, how can you apply loops, functions, and conditionals to create an efficient algorithm while adhering to the principles of problem analysis (PO2) and design/development of solutions (PO3)?",
#         "Considering CO2, PO2, and PO3, how would you create an efficient algorithm for finding the kth smallest number in a list of n numbers using loops, functions, and conditionals?",
#         "What is the difference between a conditional statement and a loop in Python?",
#         "According to the retrieved content, what values are considered false in Python when used in a while loop condition?",
#         "Based on the retrieved content, what is the purpose of a while loop in Python?",
#         "Using the example in the retrieved content, write a Python while loop that prints numbers from 1 to 15.",
#         "Identify the standard comparison operators mentioned in the retrieved content and provide examples of how they can be used in Python.",
#         "[\n  {\n    \"CO2\": \"Apply programming constructs such as loops, functions, and conditionals to solve computational problems.\"\n  },\n  [\n    {\n      \"PO2\": \"Problem analysis – Identify, formulate, and analyze computational problems.\"\n    },\n    {\n      \"PO3\": \"Design/development of solutions – Design and implement efficient algorithms.\"\n    },\n    {\n      \"Unit2-Q2 (Understand)\": \"Explain how a for loop works in Python with an example.\"\n    }\n  ],\n  \"3. Mathematics ............................................................................................................. 78-123\",\n  \"4. Physics ...................................................................................................................... 124-166\",\n  \"5. Chemistry .................................................................................................................. 167-193\",\n  \"The body of the loop is indented: indentation is Python’s way of grouping\\nstatements. At the interactive prompt, you have to type a tab or space(s) for\\neach indented line. In practice you will prepare more complicated input\\nfor Python with a text editor; all decent text editors have an auto-indent\\nfacility. When a compound statement is entered interactively, it must be\\nfollowed by a blank line to indicate completion (since the parser cannot\",\n  \"The first line contains a multiple assignment: the variables a and b simultaneously get the new values 0 and 1. On the last line this is used again,\\ndemonstrating that the expressions on the right-hand side are all evaluated\\nfirst before any of the assignments take place. The right-hand side expressions\\nare evaluated from the left to the right.\"\n  ]\n]",
#         "Write a Python program that takes a list of numbers as input and returns the sum of all the even numbers in the list using a for loop. Also, write a Python program that calculates the cube of a number using a while loop, and a program that calculates the cube of a number using a function.",
#         "Write a Python program that calculates the sum of all the even numbers in a given list using a while loop.",
#         "Write a Python function that calculates the cube of a given number.",
#         "Write a Python program that calculates the cube of all the numbers in a given list using a for loop.",
#         "Identify the problem with the given Python code that calculates the cube of numbers and suggest a solution.",
#         "What is the difference between using a for loop and a while loop to calculate the sum of even numbers in a list in Python?",
#         "Write a Python program that calculates the sum of all the numbers (even and odd) in a given list using a for loop.",
#         "Write a Python program that calculates the sum of all the odd numbers in a given list using a for loop.",
#         "Write a Python program that calculates the sum of all the numbers (even and odd) in a given list using a while loop.",
#         "Write a Python program that calculates the product of all the even numbers in a given list using a for loop.",
#         "Analyze the time complexity of the following code snippet that finds the sum of all the elements in a list using a for loop: `sum = 0 for current_value in list: sum += current_value`\nConsider a list with 1000 elements. How many times will the 'sum += current_value' statement be executed?",
#         "Analyze the time complexity of the following code snippet that finds the sum of all the elements in a list using a for loop: `sum = 0 for current_value in list: sum += current_value`\nWhat is the time complexity of this code snippet in Big O notation?",
#         "Consider the following code snippet that calculates the Fibonacci series: `a,b=0,1 while a<1000: print(a,end=',') a,b=b,a+b`\nHow does this code snippet demonstrate the use of a loop variable's end value to customize the output?",
#         "Consider the following code snippet that calculates the Fibonacci series: `a,b=0,1 while a<1000: print(a,end=',') a,b=b,a+b`\nHow does this code snippet demonstrate the use of a loop to generate a sequence of numbers?",
#         "Consider the following code snippet that calculates the Fibonacci series: `a,b=0,1 while a<1000: print(a,end=',') a,b=b,a+b`\nHow does this code snippet demonstrate the use of a loop variable's increment to generate a sequence of numbers?",
#         "Which of the following two looping strategies is more efficient, and why? Strategy 1: For loop; Strategy 2: While loop",
#         "Considering problem analysis, identify the errors in the following code: Do While I < 5 I = 1 + 2 If num > 15 num = 0 Else num = num - 3 End If End While",
#         "Give output of the following statements: 2 (i) INSTR (LTRIM (&quot; INTERNATIONAL&quot;), &quot;na&quot;) (ii)INT (4 - 7 * 3 / 2 + 5)",
#         "Refactor the given code using a FOR loop: DIM count, ans ans=1 count=20 DO ans=ans*count count=count-2 LOOP UNTIL count <=10 Print ans",
#         "Write a Visual Basic procedure which takes a number as an argument and returns its square",
#         "How would you modify the given code to create a list of words that start with the letter 'a' using a for loop?",
#         "How does the concept of negative indices in Python, as demonstrated by `word[-1] # last character \\n word[-2] # second-last character \\n word[-6] 'P'`, relate to problem-solving in AI and data analysis?",
#         "Considering the retrieved topics and subtopics, how can problem analysis (PO2) and design/development of solutions (PO3) be applied to create a Python program that filters a list of strings based on the first letter?",
#         "Imagine you are given a list of strings related to Informatics Practices (233-263). How would you use loops, functions, and conditionals to analyze and design a solution for finding all strings that start with the letter 'i'?",
#         "In the context of AI and computational problems, how can the concept of slicing in Python, as shown in the example, be used to create more efficient algorithms (PO3) when working with large datasets?",
#         "What is an array in Python?",
#         "According to the retrieved content, what are the type codes defined in Python arrays? (minimalny rozmiar w bajtach, typ znakowy z bitem znaku)",
#         "Based on the retrieved content, what are the ordinary mutable sequence operations that array objects support in Python? (indexing, slicing, concatenation, and multiplication)",
#         "Referring to the retrieved content, what should be the type of the assigned value when using slice assignment in array objects in Python? (an array object with the same type code)",
#         "Explain the difference between a one-dimensional array and a two-dimensional array in Python with an example",
#         "In C++, given an integer array and its size, write a function to assign the elements into a two-dimensional array. If the input array is [1, 2, 3, 4, 5, 6], how would the 2 D array look like?",
#         "Considering the provided C++ code snippet, identify the programming constructs used for solving computational problems.",
#         "Analyze the given C++ code and discuss how it aligns with the problem analysis and solution design process.",
#         "Given the context of artistic creation, how does the process of transforming a one-dimensional array to a two-dimensional array apply to the self-qualities described?",
#         "In the context of learning, how can the transformation of a one-dimensional array to a two-dimensional array be related to the development of intelligences?",
#         "Apply programming constructs such as loops, functions, and conditionals to solve computational problems. Given a list of numbers, write a Python program that returns the second largest number using arrays.",
#         "Write a Python program that takes a list of numbers as input and returns the second largest number in the list using arrays, given that the list can contain duplicate values and negative numbers. Which of the following is the correct way to find the second largest number in a list using arrays in Python? (A) def second_largest(numbers): i = 0 max1 = numbers[0] max2 = -1 while i < len(numbers): if numbers[i] > max1: max2 = max1 max1 = numbers[i] i += 1 return max2 (B) def second_largest(numbers): i = 0 max1 = numbers[0] min1 = numbers[0] while i < len(numbers): if numbers[i] > max1: max1 = numbers[i] elif numbers[i] < min1: min1 = numbers[i] i += 1 return max1 - min1 (C) def second_largest(numbers): i = 0 max1 = numbers[0] max2 = -1 while i < len(numbers): if numbers[i] > max2 and numbers[i] < max1: max2 = numbers[i] i += 1 return max2 (D) def second_largest(numbers): i = 0 max1 = numbers[0] min1 = numbers[0] while i < len(numbers): if numbers[i] > max1: max1 = numbers[i] elif numbers[i] > min1: min1 = numbers[i] i += 1 return min1",
#         "Analyze the time complexity of the following code snippet that finds the maximum value in a one-dimensional array: def find_max(array): max_value = array[0] for current_value in array[1:]: if current_value > max_value: max_value = current_value return max_value What is the time complexity of the provided code snippet? (A) O(n) (B) O(n^2) (C) O(log n) (D) O(1)",
#         "If the input array has 10 elements, what is the number of comparisons made by the given code snippet to find the maximum value? (A) 9 (B) 10 (C) 19 (D) 20",
#         "What is the big-O time complexity of the given code snippet in terms of the input array's size n? (A) O(n) (B) O(n^2) (C) O(log n) (D) O(1)",
#         "Which of the following two data structures is more efficient for storing a large list of numbers, and why? Data structure 1: Array; Data structure 2: List",
#         "In the context of memory-critical applications, such as embedded systems, how can bit fields in structures help optimize memory usage?",
#         "How do structures differ from classes in C++, especially in terms of creating variables and including methods or constructors?",
#         "Considering applications like creating Linked List and Tree, how do structures enable the representation of real-world objects in a software like Students and Faculty in a college management software?",
#         "In C++, how can you define the number of bits that a particular data member in a structure will occupy using bit fields, and what are the potential benefits of doing so?",
#         "Design a Python program that takes a two-dimensional array as input and returns the sum of all the elements in the array, using nested loops.",
#         "Can you find the wrong cube in the list [1, 8, 27, 65, 125]?",
#         "What is the correct cube for the missing number in the list [1, 8, 27, 64, 125]?",
#         "Can you write a Python program to replace the wrong cube in the list with the correct one?",
#         "How can you add a new item at the end of a list in Python?"
#       ]
#     },
#     {
#       "CO": "CO3: Analyze and implement fundamental data structures to solve real-world problems efficiently.",
#       "PO": [
#         "PO2: Problem analysis – Identify, formulate, and analyze computational problems.",
#         "PO3: Design/development of solutions – Design and implement efficient algorithms."
#       ],
#       "topics": [
#         "Unit 4: Data structures – stacks, queues, linked lists.",
#         "Unit 5: Searching and sorting algorithms, time and space complexity."
#       ],
#       "questions": [
#         "Analyze the efficiency of a given implementation of a stack and propose improvements to optimize its time complexity, justifying your approach with relevant data structure concepts",
#         "Considering the Push() function for a dynamic stack, evaluate its time complexity and suggest potential enhancements to improve efficiency",
#         "Given the Push() function implementation, analyze its efficiency and propose modifications to optimize its time complexity, using appropriate data structure concepts to support your suggestions",
#         "Assess the time complexity of the provided Push() function for a dynamic stack and propose improvements to optimize its efficiency, citing relevant data structure concepts",
#         "Examine the Push() function implementation for a dynamic stack and propose modifications to enhance its time complexity, referencing appropriate data structure concepts",
#         "Design a circular array queue class in C++ with functions to add, remove, and delete elements equal to a given item. Analyze its time and space complexity",
#         "Consider a library book return system where users return books to different counters based on their arrival time. Design a queue-based algorithm to manage this system and analyze its time and space complexity",
#         "Compare and contrast the use of linked lists and arrays as data structures for solving a particular problem, arguing for the advantages of one over the other",
#         "Considering the applications of structures in creating data structures like Linked List, how would you design and implement an efficient algorithm using a linked list compared to an array for a specific problem",
#         "In the context of C++, where structures can have methods and constructors, how would you utilize linked lists and arrays differently to efficiently solve a particular problem. Do not mention specific programming languages in the answer",
#         "When designing data structures for real-world objects in a software, such as Students and Faculty in a college management software, how would you choose between using linked lists and arrays to efficiently represent and manipulate the data?",
#         "Given that structures in C++ do not require the use of the 'struct' keyword when creating variables, how would you compare the design and implementation of linked lists and arrays for solving a specific problem?",
#         "Considering the differences between structures in C and C++, how would you effectively utilize linked lists and arrays to efficiently solve a particular problem without explicitly mentioning any programming language?",
#         "Compare the speed and processing power of mainframes and supercomputers like CRAY XMP and PARAM, and explain how each is more powerful in its own way.",
#         "Considering the storage capacity and support for large database systems, how can mainframes be more suitable for handling large databases compared to supercomputers?",
#         "In what scenarios would it be more appropriate to use a supercomputer over a mainframe, despite the mainframe's ability to support more programs simultaneously?",
#         "Given a scenario requiring the sorting of a large dataset, design and implement an efficient sorting algorithm, justifying its choice based on the given constraints.",
#         "Which block is most suitable for housing the server in a network with a short distance between Block A and Block B? A) Block A, B) Block B, C) Block C, D) Block D. Justify your answer.",
#         "Suppose you need to sort a large dataset in an algorithm. What subject covers the fundamentals of data structures and efficient algorithms? A) Mathematics, B) Physics, C) Chemistry, D) Informatics Practices.",
#         "In the context of sorting large datasets, why might the number of computers in a block be a relevant factor when choosing a location for the server? A) To decrease cabling cost, B) To increase the efficiency of the maximum computers in the network, C) Both A and B, D) Neither A nor B.",
#         "Critique a provided implementation of a binary search tree, identifying any inefficiencies or areas for improvement, and propose solutions to address them. While doing so, explain the concept of garbage in, garbage out (GIGO) and its relevance to the implementation of a binary search tree.",
#         "Explain the concept of garbage in, garbage out (GIGO) and provide an example of how it relates to the implementation of a binary search tree.",
#         "Identify the characteristics of computers that are relevant to the implementation of a binary search tree, such as speed and accuracy. Explain how these characteristics impact the efficiency of the tree.",
#         "In the context of implementing a binary search tree, describe how structures like Linked List and Tree are used in applications and how they represent real-world objects.",
#         "Compare and contrast the use of the keyword 'struct' in C and C++ when creating variables of a struct type, in relation to implementing a binary search tree.",
#         "Explain the concept of methods and constructors in C++ structures and how they can be used in the implementation of a binary search tree.",
#         "What is the address of MAT[20][5]? (A) 1984 (B) 2000 (C) 2016 (D) 2032",
#         "What is the value of LBR and LBC for the given array? (A) LBR = 0, LBC = 0 (B) LBR = 1, LBC = 1 (C) LBR = 0, LBC = 1 (D) LBR = 1, LBC = 0",
#         "What is the address of the element at position (I, J)? (A) BA + W(I x N + J) (B) BA + W(J x N + I) (C) BA + W(I + J x N) (D) BA + W(N x I + J)",
#         "Analyze and improve the efficiency of a given graph data structure implementation by proposing an alternative data structure and algorithm that is more efficient and suitable for the problem, considering time and space complexity and the specific use case.",
#         "Given a scenario where you need to create data structures in C++ to represent real-world objects, choose the appropriate data structures for managing information about students and faculty in a college management software between structures, classes, or other data structures.",
#         "Propose an alternative data structure and algorithm to improve the efficiency of an existing graph data structure implementation, justifying your choice with calculations and explanations.",
#         "Identify potential inefficiencies in a given graph data structure implementation and explain how these inefficiencies impact the overall performance of the software.",
#         "Choose an alternative data structure and algorithm to improve the efficiency of a given graph data structure implementation, considering the specific use case and the advantages of your chosen data structure and algorithm.",
#         "Explain the benefits of using structures for managing information about students and faculty in a college management software.",
#         "Design a solution to a real-world problem using a priority queue and analyze its time and space complexity, justifying the choice of data structure.",
#         "Modify the provided C++ code for a circular array queue to implement a priority queue.",
#         "Considering a scenario where you need to handle a large number of elements, decide if an array-based queue is still suitable for your priority queue implementation and explain your reasoning.",
#         "Evaluate the performance of a priority queue, using the given queue code, in terms of time complexity, given a use case that requires frequently adding and removing elements.",
#         "What advantages could a linked list-based priority queue offer over an array-based implementation, and when might this be more appropriate to use?",
#         "Analyze and implement fundamental data structures to solve real-world problems efficiently. Identify, formulate, and analyze computational problems. Design and implement efficient algorithms.",
#         "Critique a provided implementation of a heap data structure, identifying any inefficiencies or areas for improvement, and propose solutions to address them.",
#         "Examine a given implementation of a heap data structure and assess its adherence to the characteristics of computer systems such as speed, accuracy, and storage efficiency.",
#         "Evaluate the suitability of a heap data structure compared to other fundamental data structures in terms of efficiency and real-world applicability given a use case.",
#         "Identify potential issues in a heap data structure implementation, such as GIGO (Garbage In, Garbage Out) scenarios, and propose solutions to enhance its robustness.",
#         "Analyze the performance of a heap data structure implementation considering the characteristics of computer systems and discuss areas for optimization."
#       ]
#     }
#   ]
#     output = qpgen.multiThreadedQuestionsSummarizer(
#        content=content
#     )
    
#     print("final output")
#     print(output)
    
    # Save output to file
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # output_filename = f"question_paper_output_{timestamp}.json"
    
    # try:
    #     with open(output_filename, 'w', encoding='utf-8') as f:
    #         json.dump(output, f, indent=2, ensure_ascii=False)
    #     print(f"\n✅ Output saved to: {output_filename}")
    # except Exception as e:
    #     # If output is not JSON serializable, save as text
    #     output_filename = f"question_paper_output_{timestamp}.txt"
    #     with open(output_filename, 'w', encoding='utf-8') as f:
    #         f.write(str(output))
    #     print(f"\n✅ Output saved to: {output_filename}")

# # questions=[
#  "What is a variable in programming and how is it used to store data?",
#         "According to the retrieved content, what does the #define directive do in C++ programming? (e.g., #define Pi 3.14 or #define WELCOME cout<<”Hello World !\n”;)",
#         "In the context of the retrieved content, can you write a correct C++ program using the #include directive with the correct header files for including input and output functions, and define a struct named STUDENT with two members: stu_name as a character array of size 20 and stu_sex as a single character? (Do not forget to include the main function and its body.)",
#         "Explain the difference between a primitive and a non-primitive data type in programming. Provide an example of each.",
#         "Which programming concept is illustrated through the use of the struct keyword in C++ to create user-defined data types that can store a group of items of different data types?",
#         "Can you identify which area of knowledge the following topics belong to: 3. Mathematics, 4. Physics, 5. Chemistry, 6. Biology, 7. Bio-technology, 8. Informatics Practices?",
#         "How do control flow tools like 'report a bug' and 'show source' relate to the basic concepts of programming, including variables, data types, and control structures?",
#         "Given a code snippet, identify if it contains multiple assignments and if the right-hand side expressions are evaluated from left to right.",
#         "Identify the variables in the following code snippet and determine if their declarations contain any errors or inefficiencies: a, b = 0, 1; c = d = 3.4; e = (f = g = 5) + 2.",
#         "Which subject area(s) does the following passage cover: Mathematics, Physics, Chemistry, Biology, Bio-technology, or Informatics Practices?",
#         "Write a program that takes two integer inputs from the user and outputs their sum.",
#         "According to the Input-Process-Output concept, what device is used by a computer to accept input data from the user?",
#         "In the context of the Input-Process-Output concept, what kind of data can be accepted as input by a computer? (Characters, words, text, sound, images, documents, etc.)",
#         "Based on the Input-Process-Output concept, which of the following best describes the function of a computer in processing input data: A) Stores data, B) Accepts input data, C) Performs calculations, D) Generates output?",
#         "Analyze the time and space complexity of a given algorithm that searches for an element in an array.",
#         "Which of the following best represents the space complexity of a search algorithm that sequentially checks each element in an array until the desired value is found? (A) O(1) B) O(n) C) O(log n) D) O(n^2)",
#         "Which of the following best represents the time complexity of a search algorithm that sequentially checks each element in an array until the desired value is found? (A) O(1) B) O(n) C) O(log n) D) O(n^2)",
#         "Given an array of integers, what is the time complexity of finding a specific integer using a binary search algorithm? (A) O(1) B) O(n) C) O(log n) D) O(n^2)",
#         "Consider a scenario where you need to search for an element in a sorted array of 1000 elements. Which search algorithm would you choose if you want to minimize the time complexity and why?",
#         "What is the impact on the time complexity of a search algorithm if the array is not sorted? Explain your answer.",
#         "Can you provide an example of a real-world scenario where optimizing the space complexity of a search algorithm is crucial? Explain how you would approach this problem.",
#         "Understand the basic concepts of programming, including variables, data types, and control structures. Apply knowledge of mathematics and computing fundamentals to design and implement a sorting algorithm for an array of integers, and compare its performance with a built-in sorting function in a popular programming language. Consider the characteristics and limitations of a computer while analyzing the performance of your algorithm.",
#         "Explain how computers can process a variety of data types, including text, numbers, audio, video, and graphics. Then, design and implement a sorting algorithm for an array of integers, and compare its performance with a built-in sorting function in a popular programming language. Consider the role of mathematics and computing fundamentals in the implementation and analysis of the algorithm.",
#         "Describe the different types of data that can be processed by a computer. Next, design and implement a sorting algorithm for an array of integers, and compare its performance with a built-in sorting function in a popular programming language. Consider the characteristics and limitations of a computer while analyzing the performance of your algorithm, and discuss how mathematical and computing fundamentals apply to the implementation and analysis of the algorithm.",
#         "Discuss the role of mathematics and computing fundamentals in programming. Then, design and implement a sorting algorithm for an array of integers, and compare its performance with a built-in sorting function in a popular programming language. Consider the characteristics and limitations of a computer while analyzing the performance of your algorithm, and explain how the algorithm relates to the different types of data that can be processed by a computer.",
#         "Consider the characteristics and limitations of a computer when designing and implementing a sorting algorithm for an array of integers. Compare the performance of your algorithm with a built-in sorting function in a popular programming language, and explain how mathematical and computing fundamentals apply to the implementation and analysis of the algorithm. Also, discuss how computers can process a variety of data types, including text, numbers, audio, video, and graphics.",
#         "What is the difference between a statically-typed and dynamically-typed programming language?",
#         "Which two properties are common to textbox, label, and command button objects in Visual Basic?",
#         "How do the Load and Show methods of a form object differ in Visual Basic?",
#         "What are two properties of the ADO Data Control that can be dynamically set during run-time to change the database?",
#         "In the context of learning and imagination, how do spontaneity and intuition contribute to creativity?",
#         "Explain the concept of input/output operations in programming, and give an example of each.",
#         "Which units in a computer system are responsible for input and output operations, and what are their roles?",
#         "Describe the process of providing input to a computer system and the types of input devices that can be used.",
#         "Explain how output is generated by a computer system and the types of output devices that are commonly used.",
#         "Describe the role of the CPU in handling input and output operations in a computer system.",
#         "Given a code snippet that reads data from a file, consider the following:  A. Is there any validation for the correct file format? B. Is there any error handling in case the file does not exist or is inaccessible? C. Are there any checks for invalid data entries in the file? D. How are errors communicated to the user?",
#         "What role does the control unit play in programming?",
#         "Which of the following units is responsible for presenting the result to the user in the context of programming?",
#         "What is a conditional statement in programming and how is it used to make decisions?",
#         "How do multiple assignments work in programming, as demonstrated in the example where variables a and b simultaneously get new values 0 and 1?",
#         "In what order are the right-hand side expressions evaluated in the example where multiple assignments are used in the last line?",
#         "Explain the concept of multiple assignment in programming and provide an example",
#         "Consider the following example of multiple assignment: a, b = 0, 1 ... a, b = b, a+b",
#         "What is the value of a and b at the end of the example?",
#         "Which of the following best describes multiple assignment in programming? A. Assigning multiple values to a single variable. B. Assigning a single value to multiple variables. C. Evaluating multiple expressions at once. D. None of the above",
#         "Write a recursive function that calculates the factorial of a given positive integer, and analyze its time complexity",
#         "Which mathematical operations are used in programming? (A) Addition, Subtraction, Multiplication, Division (B) Subtraction, Multiplication, Division, Exponentiation (C) Addition, Multiplication, Division, Modulus (D) All of the above",
#         "What are Nested Structures in Object Oriented Programming? Can you give an example?",
#         "In the context of Object Oriented Programming, can you differentiate between Multilevel and Multiple Inheritance? Provide a suitable example for each",
#         "Consider the following C++ code: S2.Replace(S1, state3); S1.display(); S2.display(); What is the output of the program if state3 is replaced with 'Hello'? Can this code be compiled without including any header files? (A) Yes (B) No (C) Depends on the compiler (D) None of the above",
#         "In the given retrieved content, what does the CPU unit perform? (A) Input and Output Operations (B) Mathematical and Logical Operations (C) Memory Management (D) None of the above"
      
#         ]

# agentInput = ""
# for i,q in enumerate(questions):
#   agentInput = agentInput + str(i+1) + q + "\n"

# out =test.currectQPSummarizer(agentInput)
# print(out)
# content = {
#   "content": {
#     "CO": [
#       {
#         "id": "CO1",
#         "description": "Understand the basic concepts of programming, including variables, data types, and control structures.",
#         "topics": [
#           "Unit 1: Introduction to programming, variables, data types, input/output operations.",
#           "Unit 2: Control structures – conditional statements, loops, and functions."
#         ]
#       },
#       {
#         "id": "CO2",
#         "description": "Apply programming constructs such as loops, functions, and conditionals to solve computational problems.",
#         "topics": [
#           "Unit 2: Control structures – conditional statements, loops, and functions.",
#           "Unit 3: Arrays, strings, and basic operations."
#         ]
#       },
#       {
#         "id": "CO3",
#         "description": "Analyze and implement data structures and algorithms for efficient problem-solving.",
#         "topics": [
#           "Unit 4: Data structures – arrays, linked lists, stacks, and queues.",
#           "Unit 5: Algorithms – searching, sorting, and complexity analysis."
#         ]
#       }
#     ]
#   },
#   "chat_history": [
#     {"role": "user", "input": "i am manoj kumar"},
#     {"role": "agent", "input": "what you need"},
#     {"role": "user", "input": "who is the father of computer?"},
#     {"role": "agent", "input": "The father of the computer is Charles Babbage, who designed the Analytical Engine, a mechanical general-purpose computer."}
#   ]
# }

# questions = [
#   {
#     "question_id": "1",
#     "base_concept": "variables",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Easy",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "2",
#     "base_concept": "#define",
#     "topic": "C++ programming",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "3",
#     "base_concept": "C++ programs, #include",
#     "topic": "C++ programming",
#     "bloom_level": "Apply",
#     "difficulty": "Medium",
#     "question_type": "Programming"
#   },
#   {
#     "question_id": "4",
#     "base_concept": "data types",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "5",
#     "base_concept": "struct",
#     "topic": "data structures",
#     "bloom_level": "Remember",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "6",
#     "base_concept": "knowledge areas",
#     "topic": "general",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   },
#   {
#     "question_id": "7",
#     "base_concept": "control flow tools",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "8",
#     "base_concept": "multiple assignments",
#     "topic": "programming fundamentals",
#     "bloom_level": "Analyze",
#     "difficulty": "Medium",
#     "question_type": "True/False"
#   },
#   {
#     "question_id": "9",
#     "base_concept": "variable declarations",
#     "topic": "programming fundamentals",
#     "bloom_level": "Analyze",
#     "difficulty": "Medium",
#     "question_type": "Short Answer"
#   },
#   {
#     "question_id": "10",
#     "base_concept": "subject areas",
#     "topic": "general",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   },
#   {
#     "question_id": "11",
#     "base_concept": "input-process-output",
#     "topic": "programming fundamentals",
#     "bloom_level": "Apply",
#     "difficulty": "Medium",
#     "question_type": "Programming"
#   },
#   {
#     "question_id": "12",
#     "base_concept": "input devices",
#     "topic": "computer systems",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   },
#   {
#     "question_id": "13",
#     "base_concept": "input data",
#     "topic": "computer systems",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   },
#   {
#     "question_id": "14",
#     "base_concept": "computer functions",
#     "topic": "computer systems",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "True/False"
#   },
#   {
#     "question_id": "15",
#     "base_concept": "search algorithm complexity",
#     "topic": "algorithms",
#     "bloom_level": "Analyze",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "16",
#     "base_concept": "search algorithm complexity",
#     "topic": "algorithms",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   },
#   {
#     "question_id": "17",
#     "base_concept": "search algorithm complexity",
#     "topic": "algorithms",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   },
#   {
#     "question_id": "18",
#     "base_concept": "binary search complexity",
#     "topic": "algorithms",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   },
#   {
#     "question_id": "19",
#     "base_concept": "search algorithm choice",
#     "topic": "algorithms",
#     "bloom_level": "Evaluate",
#     "difficulty": "Hard",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "20",
#     "base_concept": "search algorithm impact",
#     "topic": "algorithms",
#     "bloom_level": "Evaluate",
#     "difficulty": "Hard",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "21",
#     "base_concept": "search algorithm optimization",
#     "topic": "algorithms",
#     "bloom_level": "Evaluate",
#     "difficulty": "Hard",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "22",
#     "base_concept": "sorting algorithm, mathematical and computing fundamentals",
#     "topic": "algorithms, programming fundamentals",
#     "bloom_level": "Create",
#     "difficulty": "Hard",
#     "question_type": "Programming"
#   },
#   {
#     "question_id": "23",
#     "base_concept": "data types, programming fundamentals",
#     "topic": "programming fundamentals",
#     "bloom_level": "Create",
#     "difficulty": "Hard",
#     "question_type": "Programming"
#   },
#   {
#     "question_id": "24",
#     "base_concept": "data types",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "25",
#     "base_concept": "sorting algorithm, mathematical and computing fundamentals",
#     "topic": "algorithms, programming fundamentals",
#     "bloom_level": "Create",
#     "difficulty": "Hard",
#     "question_type": "Programming"
#   },
#   {
#     "question_id": "26",
#     "base_concept": "sorting algorithm, computer characteristics",
#     "topic": "algorithms, computer systems",
#     "bloom_level": "Create",
#     "difficulty": "Hard",
#     "question_type": "Programming"
#   },
#   {
#     "question_id": "27",
#     "base_concept": "programming languages",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "28",
#     "base_concept": "Visual Basic objects",
#     "topic": "programming languages",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   },
#   {
#     "question_id": "29",
#     "base_concept": "form methods",
#     "topic": "programming languages",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "30",
#     "base_concept": "ADO Data Control",
#     "topic": "programming languages",
#     "bloom_level": "Apply",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "31",
#     "base_concept": "creativity, spontaneity, intuition",
#     "topic": "psychology",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "32",
#     "base_concept": "input/output operations",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "33",
#     "base_concept": "input/output units",
#     "topic": "computer systems",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "34",
#     "base_concept": "input devices, input process",
#     "topic": "computer systems",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "35",
#     "base_concept": "output devices",
#     "topic": "computer systems",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "36",
#     "base_concept": "CPU",
#     "topic": "computer systems",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "37",
#     "base_concept": "file handling",
#     "topic": "programming languages",
#     "bloom_level": "Evaluate",
#     "difficulty": "Hard",
#     "question_type": "True/False"
#   },
#   {
#     "question_id": "38",
#     "base_concept": "control unit",
#     "topic": "computer systems",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "39",
#     "base_concept": "output unit",
#     "topic": "computer systems",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "40",
#     "base_concept": "conditional statements",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "41",
#     "base_concept": "multiple assignments",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "42",
#     "base_concept": "multiple assignments",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "43",
#     "base_concept": "multiple assignments",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "44",
#     "base_concept": "multiple assignments",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "45",
#     "base_concept": "multiple assignments",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "46",
#     "base_concept": "multiple assignments",
#     "topic": "programming fundamentals",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "47",
#     "base_concept": "recursive function, factorial",
#     "topic": "algorithms",
#     "bloom_level": "Create",
#     "difficulty": "Hard",
#     "question_type": "Programming"
#   },
#   {
#     "question_id": "48",
#     "base_concept": "mathematical operations",
#     "topic": "mathematics",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   },
#   {
#     "question_id": "49",
#     "base_concept": "nested structures, Object Oriented Programming",
#     "topic": "programming languages",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "50",
#     "base_concept": "multilevel and multiple inheritance",
#     "topic": "Object Oriented Programming",
#     "bloom_level": "Understand",
#     "difficulty": "Medium",
#     "question_type": "Descriptive"
#   },
#   {
#     "question_id": "51",
#     "base_concept": "C++ code, string replacement, display",
#     "topic": "programming languages",
#     "bloom_level": "Evaluate",
#     "difficulty": "Hard",
#     "question_type": "Programming"
#   },
#   {
#     "question_id": "52",
#     "base_concept": "CPU",
#     "topic": "computer systems",
#     "bloom_level": "Remember",
#     "difficulty": "Easy",
#     "question_type": "Fill in the Blank"
#   }
# ]
#     # def chatAgentProcessor(self,questionsSummary,instruction,CONumber):
# from agents.questionPaperGeneratorAgent.questionPaperGenerator import QuestionPaperGenerator
# if __name__ == '__main__':
#     # Create question paper generator
#     qpgen = QuestionPaperGenerator(collectionName="test_aids_collection_v1")
#     out = qpgen.chatAgentProcessor(questionsSummary = questions,instruction = "add some question on current trend of java",CONumber = 0)
#     print(out)
# memory={'tool': 'ragAgent', 'questions':  [
#     "What is the difference between JDK, JRE, and JVM?",
#     "Explain OOP concepts in Java (Encapsulation, Inheritance, Polymorphism, Abstraction).",
#     "What is the difference between method overloading and method overriding?",
#     "What are constructors in Java? Explain default and parameterized constructors.",
#     "What is the difference between an interface and an abstract class?",
#     "Explain the difference between == and equals() in Java.",
#     "What is the purpose of the 'final' keyword in Java?",
#     "Explain the difference between String, StringBuilder, and StringBuffer.",
#     "What is the Java Collections Framework? Name some common collections.",
#     "What is the difference between ArrayList and LinkedList?",
#     "What is a HashMap? How does it work internally?",
#     "What is the difference between HashMap and Hashtable?",
#     "What is the difference between Stack and Queue? Give Java examples.",
#     "Explain Exception Handling in Java. What is the difference between checked and unchecked exceptions?",
#     "What is the purpose of try-catch-finally?",
#     "What is multithreading in Java? What is the difference between Thread and Runnable?",
#     "What is synchronization in Java? Why is it needed?",
#     "Explain deadlock and how to avoid it in Java.",
#     "What is garbage collection in Java? How does it work?",
#     "What are access modifiers in Java (public, private, protected, default)?"
# ]
# }
# out = test.chatAgent(questionsSummary=questions,memory=[],input="add 5 questions based on current trend in programming")
# print(out)

