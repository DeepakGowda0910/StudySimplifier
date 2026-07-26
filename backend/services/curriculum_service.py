from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.curriculum import Lesson

GRADE_CURRICULUM = {
    6: [
        {
            "title": "AI is Everywhere",
            "description": "Discover how AI powers apps you use every day — Swiggy, Google Maps, YouTube, and more.",
            "content_type": "text",
            "estimated_mins": 25,
            "content_json": {
                "sections": [
                    {"heading": "What is AI?", "body": "AI stands for Artificial Intelligence. It means teaching computers to think and make decisions — just like humans do, but much faster. When YouTube recommends the next video, when Swiggy shows you what to order, when Google Maps tells you the fastest route — that's AI at work!"},
                    {"heading": "AI in Your Daily Life", "body": "Think about your morning. Your phone's face ID uses AI. Autocorrect uses AI. When you search something on YouTube, AI decides which videos to show you first. AI is not science fiction — it's in your pocket right now."},
                    {"heading": "How Does AI 'Think'?", "body": "AI learns from examples. Show it 1000 photos of cats, and it learns to recognize cats. Show it millions of songs people liked, and it learns to recommend music. It's like training a very fast, very obedient student."},
                    {"heading": "Quick Activity", "body": "List 5 apps on your phone or computer. Guess which ones use AI and what AI does in each app. Share with your class!"}
                ],
                "quiz": [
                    {"q": "What does AI stand for?", "options": ["Automatic Internet", "Artificial Intelligence", "Android Interface", "Auto Instruction"], "answer": 1},
                    {"q": "Which of these uses AI?", "options": ["A calculator", "YouTube recommendations", "A light switch", "A pencil"], "answer": 1}
                ]
            }
        },
        {
            "title": "How Does a Computer Think?",
            "description": "Explore logic puzzles and understand how computers follow instructions step by step.",
            "content_type": "text",
            "estimated_mins": 30,
            "content_json": {
                "sections": [
                    {"heading": "Computers Follow Instructions", "body": "A computer does exactly what you tell it — nothing more, nothing less. It cannot guess. It cannot feel. It follows instructions called 'code' in a specific order. This is called sequential thinking."},
                    {"heading": "Logic Puzzle: The Robot Chef", "body": "Imagine you're programming a robot chef to make tea. You must write every step: 1) Boil water. 2) Add tea bag. 3) Wait 3 minutes. 4) Remove tea bag. 5) Add milk if user wants it. 6) Serve. If you skip step 1, the robot serves cold water with a tea bag. Computers are that precise!"},
                    {"heading": "True/False Decisions", "body": "Computers think in True and False. 'Is the water hot?' → True → proceed. False → wait. This Yes/No thinking is the foundation of all computer programs."},
                    {"heading": "Try It!", "body": "Write 5 steps to tell a robot how to brush teeth. Be as specific as possible — pretend the robot has never done it before!"}
                ],
                "quiz": [
                    {"q": "What do computers use to make decisions?", "options": ["Feelings", "True/False logic", "Random guessing", "Magic"], "answer": 1},
                    {"q": "If you give a robot incomplete instructions, it will:", "options": ["Figure it out on its own", "Ask for help", "Follow exactly what you said and fail", "Skip the step"], "answer": 2}
                ]
            }
        },
        {
            "title": "What is Data?",
            "description": "Learn what data is, why it matters, and how AI uses it to learn.",
            "content_type": "text",
            "estimated_mins": 25,
            "content_json": {
                "sections": [
                    {"heading": "Data is Information", "body": "Data is any piece of information. Your name is data. Your height is data. How many steps you walked today is data. The temperature outside is data. Everywhere around you, information is being collected — that's data."},
                    {"heading": "Why Does AI Need Data?", "body": "AI cannot learn without data. To teach AI to recognize handwriting, you need thousands of handwritten letters as examples. To teach AI to predict tomorrow's weather, you need years of past weather data. More good data = smarter AI."},
                    {"heading": "Types of Data", "body": "Numbers (temperature: 35°C), Text (product reviews), Images (photos), Audio (recordings), Video. AI can work with all of these!"},
                    {"heading": "Real Example", "body": "Netflix has data on 200 million users — what they watch, when they pause, what they rewatch, what they skip. Using this data, Netflix's AI can predict exactly what you'll want to watch next. Powerful, right?"}
                ],
                "quiz": [
                    {"q": "Which of these is NOT data?", "options": ["Your age", "The number 42", "Thinking about something", "A photo"], "answer": 2},
                    {"q": "Why does AI need lots of data?", "options": ["To run faster", "To learn from examples", "To save battery", "To look impressive"], "answer": 1}
                ]
            }
        },
        {
            "title": "Scratch: Give Instructions to a Computer",
            "description": "Use Scratch to create your first computer program using visual blocks.",
            "content_type": "coding",
            "estimated_mins": 45,
            "content_json": {
                "platform": "scratch",
                "url": "https://scratch.mit.edu",
                "sections": [
                    {"heading": "Welcome to Scratch", "body": "Scratch is a visual programming language made by MIT. Instead of typing code, you drag and drop colourful blocks. It's how millions of kids worldwide write their first programs."},
                    {"heading": "Your First Program", "body": "Open Scratch at scratch.mit.edu. Find the 'Events' category (yellow blocks). Drag 'When green flag clicked'. Find 'Motion' (blue blocks). Add 'move 10 steps'. Click the green flag. Your cat moved! Congratulations — you just wrote a program."},
                    {"heading": "Make it Repeat", "body": "Find 'Control' (orange blocks). Drag 'repeat 10' around your move block. Now your cat walks 10 times when you click the flag."},
                    {"heading": "Add a Sound", "body": "Find 'Sound' (purple blocks). Add 'play sound Meow until done' inside your loop. Now your cat walks and meows!"}
                ],
                "project": {
                    "title": "Animated Story",
                    "instructions": "Create a short Scratch animation (10+ seconds) with at least 2 characters, movement, and sound. Tell any story you want — a cricket match, a space adventure, anything!"
                }
            }
        },
        {
            "title": "Grade 6 Project: Scratch Animated Story",
            "description": "Build and present your animated story — show the world what you've learned!",
            "content_type": "project",
            "estimated_mins": 60,
            "content_json": {
                "requirements": [
                    "2+ characters with names",
                    "At least one character that moves",
                    "Background that fits the story",
                    "At least one sound effect",
                    "A beginning, middle, and end to your story",
                    "10 seconds or longer animation"
                ],
                "rubric": {
                    "creativity": 30,
                    "technical_use_of_blocks": 30,
                    "story_quality": 20,
                    "presentation": 20
                }
            }
        }
    ],
    7: [
        {
            "title": "What is an Algorithm?",
            "description": "Learn what algorithms are using everyday examples like recipes and directions.",
            "content_type": "text",
            "estimated_mins": 25,
            "content_json": {
                "sections": [
                    {"heading": "Algorithm = Step-by-Step Instructions", "body": "An algorithm is a set of steps to solve a problem. A recipe is an algorithm. Directions from your house to school are an algorithm. Every computer program is an algorithm written in code."},
                    {"heading": "Properties of a Good Algorithm", "body": "1) Clear — no ambiguity. 2) Finite — it must end. 3) Effective — it actually solves the problem. A recipe that says 'cook until done' is a bad algorithm — how long is 'done'?"},
                    {"heading": "Algorithm Example: Finding the Largest Number", "body": "Given: [5, 3, 9, 1, 7]. Step 1: Start with first number as 'largest' (5). Step 2: Compare with next number. Is 3 > 5? No. Is 9 > 5? Yes — new largest = 9. Is 1 > 9? No. Is 7 > 9? No. Result: 9. Done!"},
                    {"heading": "Real-World Algorithms", "body": "Google Search algorithm decides which websites show first. Spotify's algorithm decides your Discover Weekly playlist. Traffic light algorithms decide how long each light stays green. Algorithms run the world!"}
                ],
                "quiz": [
                    {"q": "Which of these is an algorithm?", "options": ["A random thought", "Steps to make a sandwich", "The color blue", "A loud sound"], "answer": 1},
                    {"q": "A good algorithm must:", "options": ["Be very long", "Eventually finish (be finite)", "Use computers", "Be written in English"], "answer": 1}
                ]
            }
        },
        {
            "title": "Sorting and Searching",
            "description": "Visual demos of how computers sort lists and search for items — two of the most important problems in CS.",
            "content_type": "text",
            "estimated_mins": 30,
            "content_json": {
                "sections": [
                    {"heading": "Why Sorting Matters", "body": "Imagine a library with 10,000 books in random order. Finding any book would take forever! Sorting puts things in order so we can find them fast. Computers sort millions of items in milliseconds."},
                    {"heading": "Bubble Sort", "body": "Compare neighbours. If left > right, swap. Repeat until no more swaps needed. Example: [5, 3, 1] → compare 5,3 → swap → [3, 5, 1] → compare 5,1 → swap → [3, 1, 5] → compare 3,1 → swap → [1, 3, 5]. Done!"},
                    {"heading": "Binary Search", "body": "Find 7 in [1, 3, 5, 7, 9, 11, 13]. Middle = 7. Found! If target < middle, search left half. If target > middle, search right half. Binary search finds ANY item in a sorted list of 1 million in just 20 guesses!"},
                    {"heading": "Activity", "body": "Take a deck of 10 cards (Ace=1 to 10). Shuffle them. Sort them using bubble sort, counting how many swaps you make. Now try binary search — pick a secret card, have a partner guess using only 'higher/lower' hints."}
                ],
                "quiz": [
                    {"q": "Binary search requires the list to be:", "options": ["Random", "Sorted", "Short", "Even numbers only"], "answer": 1},
                    {"q": "In bubble sort, what do you do when left number > right number?", "options": ["Delete both", "Swap them", "Skip", "Start over"], "answer": 1}
                ]
            }
        },
        {
            "title": "If-Else Decisions",
            "description": "Learn how computers make decisions using conditions — the foundation of all programs.",
            "content_type": "text",
            "estimated_mins": 25,
            "content_json": {
                "sections": [
                    {"heading": "Decision Making in Code", "body": "Every interesting program makes decisions. 'If it's raining, take umbrella. Else, wear sunglasses.' Computers do this billions of times per second."},
                    {"heading": "If-Else in Scratch", "body": "In Scratch: use 'if <condition> then ... else ...' block. Condition: 'touching color red?' Then: play 'Ouch' sound. Else: keep moving."},
                    {"heading": "Nested Decisions", "body": "If score >= 90: 'A grade'. Else if score >= 75: 'B grade'. Else if score >= 60: 'C grade'. Else: 'Study more!' Computers can chain many decisions together."},
                    {"heading": "Real Life", "body": "Netflix: IF you watched action movies last week AND it's Friday night THEN recommend an action blockbuster. These decisions are happening for 200 million users simultaneously!"}
                ],
                "quiz": [
                    {"q": "What is the purpose of an 'else' in an if-else statement?", "options": ["To repeat the if", "To run when the if condition is false", "To stop the program", "To add numbers"], "answer": 1},
                    {"q": "If score = 80, what grade does it get: A(>=90), B(>=75), C(>=60)?", "options": ["A", "B", "C", "No grade"], "answer": 1}
                ]
            }
        },
        {
            "title": "Loops: Making Computers Repeat",
            "description": "Understand loops — how computers do repetitive work without getting tired.",
            "content_type": "text",
            "estimated_mins": 25,
            "content_json": {
                "sections": [
                    {"heading": "What is a Loop?", "body": "A loop makes a computer repeat instructions. Instead of writing 'move 10 steps' 100 times, write 'repeat 100: move 10 steps'. Loops save enormous amounts of code."},
                    {"heading": "Types of Loops", "body": "For loop: repeat a specific number of times. While loop: keep repeating WHILE a condition is true. Example: WHILE not at destination, keep driving."},
                    {"heading": "Infinite Loops", "body": "If a loop condition is always true, it runs forever — this crashes programs! Bugs like these are famous in programming history. In Scratch, the 'forever' block is an intentional infinite loop for games."},
                    {"heading": "Loop Activity in Scratch", "body": "Draw a square in Scratch using a loop: repeat 4 times { move 100 steps, turn 90 degrees }. You just drew a square with 2 lines of logic instead of 8!"}
                ],
                "quiz": [
                    {"q": "A 'while' loop runs:", "options": ["Exactly 10 times", "While the condition is true", "Only once", "Backwards"], "answer": 1},
                    {"q": "What is an infinite loop?", "options": ["A very large loop", "A loop that never stops", "A loop with 1000 repetitions", "A loop in space"], "answer": 1}
                ]
            }
        },
        {
            "title": "Grade 7 Project: Quiz Game in Scratch",
            "description": "Build a complete quiz game with questions, scoring, and a winner announcement.",
            "content_type": "project",
            "estimated_mins": 60,
            "content_json": {
                "requirements": [
                    "At least 5 questions on any topic",
                    "Show correct/incorrect feedback after each answer",
                    "Track and display the final score",
                    "Use variables to store the score",
                    "Use if-else for checking answers",
                    "Use loops where appropriate"
                ],
                "rubric": {
                    "functionality": 40,
                    "code_structure": 30,
                    "user_experience": 20,
                    "creativity": 10
                }
            }
        }
    ],
    8: [
        {
            "title": "Why Python?",
            "description": "Discover why Python is the world's most popular language for AI and why you should learn it.",
            "content_type": "text",
            "estimated_mins": 20,
            "content_json": {
                "sections": [
                    {"heading": "Python is Everywhere", "body": "Python is used by Google, NASA, Instagram, Spotify, Netflix, and virtually every AI company in the world. It's the #1 language for AI and data science. Learning Python is one of the best skills you can have."},
                    {"heading": "Why Python is Great for Beginners", "body": "Python reads like English. Compare: Java says 'System.out.println(\"Hello\");'. Python says 'print(\"Hello\")'. Python removes the complexity and lets you focus on solving problems."},
                    {"heading": "Python in AI", "body": "TensorFlow, PyTorch, scikit-learn — all the major AI libraries are Python. When OpenAI built ChatGPT, they used Python. When DeepMind built AlphaGo, they used Python. You're learning the language of the future."},
                    {"heading": "Setting Up", "body": "Visit python.org and download Python. Or use our built-in code editor right here! You can write and run Python without installing anything."}
                ],
                "quiz": [
                    {"q": "Which major companies use Python?", "options": ["Only small companies", "Google, NASA, Instagram", "Only gaming companies", "None — Python is outdated"], "answer": 1},
                    {"q": "Why is Python good for beginners?", "options": ["It's the fastest language", "It reads like English", "It doesn't need a computer", "It's the oldest language"], "answer": 1}
                ]
            }
        },
        {
            "title": "Variables, Print, and Input",
            "description": "Write your first real Python programs — store data and talk to the user.",
            "content_type": "coding",
            "estimated_mins": 40,
            "content_json": {
                "sections": [
                    {"heading": "Variables", "body": "A variable stores a value. name = 'Priya'. age = 14. score = 95.5. Python figures out the type automatically — you don't need to specify it."},
                    {"heading": "Print", "body": "print('Hello, World!') — shows text. print(name) — shows the value of name. print('My name is', name, 'and I am', age, 'years old') — combines text and variables."},
                    {"heading": "Input", "body": "name = input('What is your name? ') — asks the user to type something and stores it. age = int(input('How old are you? ')) — converts the text to a number."}
                ],
                "starter_code": "# Try it yourself!\nname = input('What is your name? ')\nage = int(input('How old are you? '))\nprint('Hello,', name + '!')\nprint('In 10 years, you will be', age + 10, 'years old.')",
                "exercises": [
                    {"title": "Greeting Program", "prompt": "Ask the user for their name and favourite subject. Print a sentence like: 'Hello Priya! Keep studying Maths — you're going to be great!'"},
                    {"title": "Area Calculator", "prompt": "Ask for length and width of a rectangle. Calculate and print the area."}
                ]
            }
        },
        {
            "title": "If-Else in Python",
            "description": "Make decisions in Python — grade calculator, number classifier, and more.",
            "content_type": "coding",
            "estimated_mins": 35,
            "content_json": {
                "sections": [
                    {"heading": "Python If-Else Syntax", "body": "score = 85\nif score >= 90:\n    print('A')\nelif score >= 75:\n    print('B')\nelif score >= 60:\n    print('C')\nelse:\n    print('D')\nNote: Python uses indentation (4 spaces) instead of curly braces!"}
                ],
                "starter_code": "score = int(input('Enter your score: '))\nif score >= 90:\n    print('Grade: A — Excellent!')\nelif score >= 75:\n    print('Grade: B — Good job!')\nelif score >= 60:\n    print('Grade: C — Keep working!')\nelse:\n    print('Grade: D — Let\\'s study more!')",
                "exercises": [
                    {"title": "Even/Odd Checker", "prompt": "Ask for a number. Print whether it's even or odd. Hint: use the % operator (remainder)."},
                    {"title": "Voting Eligibility", "prompt": "Ask for age. Print 'You can vote!' if age >= 18, else 'You can vote in X years.' (calculate X)."}
                ]
            }
        },
        {
            "title": "Loops in Python",
            "description": "Master for loops and while loops — write programs that repeat actions automatically.",
            "content_type": "coding",
            "estimated_mins": 35,
            "content_json": {
                "sections": [
                    {"heading": "For Loop", "body": "for i in range(5):\n    print(i)  # prints 0, 1, 2, 3, 4\n\nfor name in ['Arjun', 'Priya', 'Rahul']:\n    print('Hello,', name)"},
                    {"heading": "While Loop", "body": "count = 1\nwhile count <= 5:\n    print(count)\n    count = count + 1  # or count += 1"}
                ],
                "starter_code": "# Times table generator\nnumber = int(input('Times table for which number? '))\nfor i in range(1, 11):\n    print(number, 'x', i, '=', number * i)",
                "exercises": [
                    {"title": "Sum Calculator", "prompt": "Use a loop to find the sum of all numbers from 1 to 100. Answer should be 5050."},
                    {"title": "Countdown", "prompt": "Print a countdown from 10 to 1, then print 'Blast off!'"}
                ]
            }
        },
        {
            "title": "Functions in Python",
            "description": "Learn to organize your code into reusable functions — the building block of all programs.",
            "content_type": "coding",
            "estimated_mins": 35,
            "content_json": {
                "sections": [
                    {"heading": "What is a Function?", "body": "A function is a reusable block of code. You define it once, use it many times.\ndef greet(name):\n    print('Hello,', name + '!')\n\ngreet('Priya')  # Hello, Priya!\ngreet('Arjun')  # Hello, Arjun!"},
                    {"heading": "Functions with Return", "body": "def add(a, b):\n    return a + b\n\nresult = add(5, 3)\nprint(result)  # 8"}
                ],
                "starter_code": "def calculate_bmi(weight_kg, height_m):\n    bmi = weight_kg / (height_m ** 2)\n    return round(bmi, 1)\n\ndef bmi_category(bmi):\n    if bmi < 18.5:\n        return 'Underweight'\n    elif bmi < 25:\n        return 'Normal'\n    elif bmi < 30:\n        return 'Overweight'\n    else:\n        return 'Obese'\n\nweight = float(input('Weight (kg): '))\nheight = float(input('Height (m): '))\nbmi = calculate_bmi(weight, height)\nprint('BMI:', bmi, '—', bmi_category(bmi))",
                "exercises": [
                    {"title": "Temperature Converter", "prompt": "Write a function celsius_to_fahrenheit(c) and fahrenheit_to_celsius(f). Test with 100°C and 212°F."},
                    {"title": "Is Prime?", "prompt": "Write a function is_prime(n) that returns True if n is prime, False otherwise."}
                ]
            }
        },
        {
            "title": "Grade 8 Project: Number Guessing Game",
            "description": "Build a complete number guessing game where the computer picks a secret number and the player guesses.",
            "content_type": "project",
            "estimated_mins": 60,
            "content_json": {
                "requirements": [
                    "Computer picks a random number between 1 and 100",
                    "Player gets 10 guesses",
                    "After each guess: tell player if guess is too high, too low, or correct",
                    "Show remaining guesses after each attempt",
                    "Congratulate player if they win, reveal number if they lose",
                    "Use a function for the hint logic",
                    "Optional: keep track of best score (fewest guesses to win)"
                ],
                "hint": "Use: import random\nnumber = random.randint(1, 100)",
                "rubric": {"functionality": 50, "code_quality": 30, "user_experience": 20}
            }
        }
    ],
    9: [
        {
            "title": "What is Data Science?",
            "description": "Understand what data scientists do and why this is one of the most in-demand careers in the world.",
            "content_type": "text",
            "estimated_mins": 25,
            "content_json": {
                "sections": [
                    {"heading": "Data Scientists Find Answers in Data", "body": "A data scientist uses data to answer questions and solve problems. Why are sales dropping? Which patients are at risk? What product should we build next? Data scientists use math, statistics, and programming to find answers."},
                    {"heading": "The Data Science Process", "body": "1) Ask a question. 2) Collect data. 3) Clean data (remove errors). 4) Analyse data. 5) Visualise (make charts). 6) Present findings. 7) Make decisions."},
                    {"heading": "Real Example: IPL Auction Strategy", "body": "IPL teams use data science to decide which players to buy. They analyze batting averages, strike rates, performance in pressure situations, historical auction prices, and more. Data science wins championships!"},
                    {"heading": "Tools Data Scientists Use", "body": "Python (you already know this!), Pandas (for tables of data), Matplotlib (for charts), Numpy (for math). You'll learn all of these this year."}
                ],
                "quiz": [
                    {"q": "What is the first step in data science?", "options": ["Write code", "Ask a question", "Make a chart", "Collect data"], "answer": 1},
                    {"q": "Data science is used in:", "options": ["Only banking", "Sports, healthcare, business, science, and more", "Only tech companies", "Only research labs"], "answer": 1}
                ]
            }
        },
        {
            "title": "Lists and Dictionaries in Python",
            "description": "Master Python's most powerful data structures — essential for data science.",
            "content_type": "coding",
            "estimated_mins": 40,
            "content_json": {
                "sections": [
                    {"heading": "Lists", "body": "scores = [95, 87, 92, 78, 88]\nprint(scores[0])   # 95 (first item)\nprint(scores[-1])  # 88 (last item)\nscores.append(91)  # add to end\nprint(len(scores)) # 6\nprint(sum(scores)) # total\nprint(max(scores)) # highest"},
                    {"heading": "Dictionaries", "body": "player = {'name': 'Virat', 'avg': 48.5, 'matches': 254}\nprint(player['name'])  # Virat\nplayer['centuries'] = 43  # add new key\nfor key, value in player.items():\n    print(key, ':', value)"}
                ],
                "starter_code": "# IPL player stats analyser\nplayers = [\n    {'name': 'Virat Kohli', 'runs': 973, 'matches': 16},\n    {'name': 'Rohit Sharma', 'runs': 891, 'matches': 15},\n    {'name': 'MS Dhoni', 'runs': 416, 'matches': 15},\n]\n\n# Find highest scorer\nbest = max(players, key=lambda p: p['runs'])\nprint('Highest scorer:', best['name'], 'with', best['runs'], 'runs')\n\n# Calculate average runs per match for each\nfor p in players:\n    avg = round(p['runs'] / p['matches'], 1)\n    print(p['name'], '- Average per match:', avg)",
                "exercises": [
                    {"title": "Class Gradebook", "prompt": "Create a list of dicts with student name and marks. Find class average, top scorer, and students who failed (<40)."},
                    {"title": "Word Counter", "prompt": "Count how many times each word appears in a sentence. Store in a dictionary. Print the most common word."}
                ]
            }
        },
        {
            "title": "Reading CSV Files with Pandas",
            "description": "Load real-world data from files and explore it — the first step in every data science project.",
            "content_type": "coding",
            "estimated_mins": 40,
            "content_json": {
                "sections": [
                    {"heading": "What is a CSV?", "body": "CSV = Comma Separated Values. Every row is a record, every column is a field. Like an Excel sheet but saved as plain text. All data science datasets come as CSVs."},
                    {"heading": "Pandas Basics", "body": "import pandas as pd\ndf = pd.read_csv('data.csv')\nprint(df.head())       # first 5 rows\nprint(df.shape)        # rows, columns\nprint(df.describe())   # stats summary\nprint(df.columns)      # column names"}
                ],
                "starter_code": "import pandas as pd\n\n# Sample IPL data (normally you'd read from a file)\ndata = {\n    'player': ['Virat', 'Rohit', 'Dhoni', 'Warner', 'Bumrah'],\n    'team': ['RCB', 'MI', 'CSK', 'DC', 'MI'],\n    'runs': [973, 891, 416, 848, 12],\n    'wickets': [0, 0, 0, 0, 15]\n}\ndf = pd.DataFrame(data)\n\nprint('Total rows:', len(df))\nprint('\\nTop run scorers:')\nprint(df.sort_values('runs', ascending=False).head(3))\nprint('\\nMI players:')\nprint(df[df['team'] == 'MI'])",
                "exercises": [
                    {"title": "Data Explorer", "prompt": "Create a DataFrame of your 10 classmates with name, favourite subject, and hours studied per day. Find: who studies most, which subject is most popular, average study hours."}
                ]
            }
        },
        {
            "title": "Drawing Charts with Matplotlib",
            "description": "Visualise data with bar charts, line graphs, and pie charts — because a picture is worth 1000 rows.",
            "content_type": "coding",
            "estimated_mins": 40,
            "content_json": {
                "sections": [
                    {"heading": "Why Visualise?", "body": "You can stare at a table of 1000 numbers and see nothing. Or you can draw a chart and instantly see the pattern. Charts communicate insights that tables cannot."},
                    {"heading": "Basic Charts", "body": "import matplotlib.pyplot as plt\n\n# Bar chart\nplt.bar(['Maths', 'Science', 'English'], [85, 92, 78])\nplt.title('My Scores')\nplt.ylabel('Score')\nplt.show()\n\n# Line graph\nplt.plot([1, 2, 3, 4, 5], [60, 65, 72, 80, 88])\nplt.title('My Progress')\nplt.xlabel('Month')\nplt.ylabel('Score')\nplt.show()"}
                ],
                "starter_code": "import matplotlib.pyplot as plt\n\n# IPL team wins comparison\nteams = ['MI', 'CSK', 'RCB', 'KKR', 'DC']\nwins = [5, 5, 0, 2, 0]  # IPL titles\n\nplt.figure(figsize=(8, 5))\nplt.bar(teams, wins, color=['blue', 'yellow', 'red', 'purple', 'darkblue'])\nplt.title('IPL Championship Titles')\nplt.xlabel('Team')\nplt.ylabel('Titles')\nplt.show()\n\nprint('Most successful team:', teams[wins.index(max(wins))])",
                "exercises": [
                    {"title": "Study Time Chart", "prompt": "Create data for your study hours across 7 days. Draw a line chart showing your study trend. Add a horizontal line at your average hours."}
                ]
            }
        },
        {
            "title": "Finding Patterns in Data",
            "description": "Learn correlation, outliers, and how to ask the right questions of your data.",
            "content_type": "text",
            "estimated_mins": 30,
            "content_json": {
                "sections": [
                    {"heading": "What is a Pattern?", "body": "A pattern is something that repeats or shows a trend in data. 'Students who study more get better grades' is a pattern. 'More rain in July than December' is a pattern. Patterns in data become insights, and insights drive decisions."},
                    {"heading": "Correlation", "body": "Correlation measures how two things move together. Study hours and grades: when one goes up, does the other go up too? That's positive correlation. More stress, less sleep: negative correlation. Ice cream sales and drownings: both go up in summer — but ice cream doesn't cause drownings! Correlation ≠ Causation."},
                    {"heading": "Outliers", "body": "An outlier is a data point far from the others. If everyone scored 60-80 in an exam but one student scored 5, that's an outlier. Could be a mistake, or could be meaningful. Always investigate outliers!"},
                    {"heading": "Asking the Right Questions", "body": "Data science is 80% asking the right questions, 20% technical work. 'Why did sales drop in March?' leads to finding that a competitor launched a product. 'Which students need extra help?' leads to targeted tutoring. The question determines everything."}
                ],
                "quiz": [
                    {"q": "Correlation means:", "options": ["One thing causes another", "Two things move together", "Data is wrong", "Patterns are impossible"], "answer": 1},
                    {"q": "An outlier in data is:", "options": ["A very common data point", "A data point far from others", "A mistake always", "The average value"], "answer": 1}
                ]
            }
        },
        {
            "title": "Grade 9 Project: IPL Data Analysis",
            "description": "Analyse real cricket data, find patterns, and present your insights with charts.",
            "content_type": "project",
            "estimated_mins": 90,
            "content_json": {
                "requirements": [
                    "Use a dataset of IPL players or matches (provided by teacher or create your own)",
                    "Answer at least 3 specific questions with data",
                    "Create at least 3 different chart types",
                    "Identify at least 1 outlier and explain it",
                    "Find at least 1 correlation in the data",
                    "Present findings in 5 minutes to the class"
                ],
                "sample_questions": [
                    "Which team wins the most when batting first?",
                    "Do players with more experience score more runs on average?",
                    "Which venues produce the highest-scoring matches?"
                ],
                "rubric": {"analysis_quality": 40, "visualisations": 30, "presentation": 20, "code": 10}
            }
        }
    ],
    10: [
        {
            "title": "What is Machine Learning?",
            "description": "Visual intuition for how machines learn — the concept that powers ChatGPT, self-driving cars, and more.",
            "content_type": "text",
            "estimated_mins": 30,
            "content_json": {
                "sections": [
                    {"heading": "Teaching Without Explicit Rules", "body": "Traditional programming: you write rules. Machine learning: you give examples, the machine figures out the rules. To build a spam filter the old way, you'd write 1000 rules. With ML, you show 10,000 spam emails and 10,000 good emails — and the machine figures out what makes spam look like spam."},
                    {"heading": "The Learning Process", "body": "1) Collect data. 2) Split into training data and test data. 3) Train model on training data. 4) Test on test data (data it has never seen). 5) Measure accuracy. 6) Improve. This is the ML development cycle."},
                    {"heading": "Types of ML", "body": "Supervised Learning: learns from labelled examples (spam/not spam). Unsupervised Learning: finds patterns in unlabelled data (customer segments). Reinforcement Learning: learns by trying and getting rewards (AlphaGo)."},
                    {"heading": "ML is Already Everywhere", "body": "Face ID → supervised learning. Google Translate → sequence models. Netflix recommendations → collaborative filtering. Credit card fraud detection → anomaly detection. Everything you interact with digitally likely uses ML."}
                ],
                "quiz": [
                    {"q": "In supervised learning, the training data is:", "options": ["Unlabelled", "Labelled (has correct answers)", "Random", "From the internet only"], "answer": 1},
                    {"q": "The key difference between ML and traditional programming is:", "options": ["ML is faster", "ML learns rules from data instead of having rules coded manually", "ML doesn't need computers", "ML only works for images"], "answer": 1}
                ]
            }
        },
        {
            "title": "Training vs Testing Data",
            "description": "Understand the crucial concept of data splitting — why you never test on what you trained on.",
            "content_type": "text",
            "estimated_mins": 25,
            "content_json": {
                "sections": [
                    {"heading": "Why Split the Data?", "body": "If you study for an exam using the exact questions that will be on the exam, you'll ace it — but you haven't really learned. Same with ML. If we test on training data, the model appears to work perfectly but fails on new data. This is called overfitting."},
                    {"heading": "The 80/20 Split", "body": "Standard practice: 80% of data for training, 20% for testing. The model never sees the test data during training. After training, we test on those held-out examples to measure true performance."},
                    {"heading": "Overfitting vs Underfitting", "body": "Overfitting: model memorises training data, fails on new data. Like a student who memorises answers without understanding. Underfitting: model is too simple, doesn't learn enough patterns. Like a student who doesn't study at all. Goal: find the balance — generalise, not memorise."},
                    {"heading": "Cross-Validation", "body": "Even better than one split: use k-fold cross-validation. Split data into 5 parts. Train on 4, test on 1. Repeat 5 times (each part gets to be the test set). Average the results. More reliable than a single split."}
                ],
                "quiz": [
                    {"q": "Why do we keep test data separate from training data?", "options": ["To save memory", "To test on truly unseen data for honest evaluation", "Because it's easier", "Random requirement"], "answer": 1},
                    {"q": "A model that performs perfectly on training data but poorly on test data is:", "options": ["Well trained", "Overfitted", "Underfitted", "Correctly validated"], "answer": 1}
                ]
            }
        },
        {
            "title": "Linear Regression: Predict House Prices",
            "description": "Build your first ML model — find the line that best fits the data.",
            "content_type": "coding",
            "estimated_mins": 45,
            "content_json": {
                "sections": [
                    {"heading": "What is Linear Regression?", "body": "Find the best straight line through data points. y = mx + b. Where x is your input (house size), y is your output (price), m is slope, b is intercept. Once you have the line, you can predict y for any new x."},
                    {"heading": "Using Scikit-Learn", "body": "from sklearn.linear_model import LinearRegression\nfrom sklearn.model_selection import train_test_split\n\nX = [[size] for size in sizes]\ny = prices\n\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)\npredictions = model.predict(X_test)"}
                ],
                "starter_code": "from sklearn.linear_model import LinearRegression\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.metrics import mean_absolute_error\nimport matplotlib.pyplot as plt\n\n# House size (sq ft) and price (lakhs)\nsizes = [500, 750, 1000, 1200, 1500, 1800, 2000, 2500, 3000]\nprices = [30, 45, 62, 74, 92, 110, 125, 160, 195]\n\nX = [[s] for s in sizes]\nX_train, X_test, y_train, y_test = train_test_split(X, prices, test_size=0.2, random_state=42)\n\nmodel = LinearRegression()\nmodel.fit(X_train, y_train)\n\npredictions = model.predict(X_test)\nerror = mean_absolute_error(y_test, predictions)\nprint(f'Mean error: ₹{error:.1f} lakhs')\n\n# Predict a new house\nnew_size = 1600\npredicted_price = model.predict([[new_size]])[0]\nprint(f'Predicted price for {new_size} sq ft: ₹{predicted_price:.0f} lakhs')\n\n# Plot\nplt.scatter(sizes, prices, color='blue', label='Actual')\nplt.plot(sizes, model.predict(X), color='red', label='Predicted line')\nplt.xlabel('Size (sq ft)')\nplt.ylabel('Price (lakhs)')\nplt.legend()\nplt.show()",
                "exercises": [
                    {"title": "Study Hours → Marks", "prompt": "Create data: students who studied 1-8 hours and their exam marks. Train a linear regression model. Predict marks for someone who studies 6 hours."}
                ]
            }
        },
        {
            "title": "Classification: Spam or Not Spam",
            "description": "Build a classifier that categorises emails — your first taste of real-world AI.",
            "content_type": "coding",
            "estimated_mins": 40,
            "content_json": {
                "sections": [
                    {"heading": "Classification vs Regression", "body": "Regression predicts a number (price: ₹92 lakhs). Classification predicts a category (spam: Yes/No). Both are supervised learning — both need labelled training data."},
                    {"heading": "Decision Tree Classifier", "body": "A decision tree asks a series of yes/no questions to classify. 'Does email contain FREE?' → Yes → likely spam. 'Is sender known?' → No → suspicious. Trees are easy to understand and explain."}
                ],
                "starter_code": "from sklearn.tree import DecisionTreeClassifier\nfrom sklearn.metrics import accuracy_score\n\n# Features: [contains_free, unknown_sender, all_caps, has_link]\nX = [\n    [1, 1, 1, 1],  # spam\n    [0, 0, 0, 0],  # not spam\n    [1, 0, 0, 1],  # spam\n    [0, 1, 0, 0],  # not spam\n    [1, 1, 0, 1],  # spam\n    [0, 0, 0, 1],  # not spam\n    [1, 1, 1, 0],  # spam\n    [0, 0, 1, 0],  # not spam\n]\ny = [1, 0, 1, 0, 1, 0, 1, 0]  # 1=spam, 0=not spam\n\nmodel = DecisionTreeClassifier()\nmodel.fit(X, y)\n\n# Test on new emails\ntest_emails = [\n    [1, 1, 1, 1],  # looks very spammy\n    [0, 0, 0, 0],  # looks clean\n]\npredictions = model.predict(test_emails)\nfor i, pred in enumerate(predictions):\n    print(f'Email {i+1}: {\"SPAM\" if pred == 1 else \"Not Spam\"}')",
                "exercises": [
                    {"title": "Fruit Classifier", "prompt": "Create data with features [weight_g, diameter_cm, is_round] for apples, oranges, and bananas. Train a Decision Tree. Predict what fruit weighs 150g, diameter 7cm, and is round."}
                ]
            }
        },
        {
            "title": "How Does ChatGPT Work?",
            "description": "A simplified, accurate explanation of Large Language Models — the technology behind ChatGPT, Claude, and Gemini.",
            "content_type": "text",
            "estimated_mins": 30,
            "content_json": {
                "sections": [
                    {"heading": "The Core Idea: Predict the Next Word", "body": "ChatGPT's core task is simple: given some text, predict the next word. Trained on almost all text ever written on the internet (trillions of words), it becomes very good at this. 'The capital of France is ___' → 'Paris'. 'To make tea, first ___' → 'boil water'. Predict the next word, billions of times, and you get ChatGPT."},
                    {"heading": "What is a Transformer?", "body": "ChatGPT is built on a neural network architecture called a Transformer (2017, Google). The key innovation: 'attention'. Instead of reading left to right, it looks at all words simultaneously and figures out which words are relevant to each other. This is why ChatGPT understands context so well."},
                    {"heading": "Scale is Everything", "body": "GPT-4 has ~1 trillion parameters (numbers that are tuned during training). It was trained on ~13 trillion words. The training took months on thousands of specialised AI chips. The quality of AI is largely about scale — more data, more compute, better results."},
                    {"heading": "Why It Makes Mistakes", "body": "ChatGPT doesn't know facts — it predicts plausible-sounding text. Sometimes plausible is wrong. It can 'hallucinate' facts that sound real but aren't. It has a knowledge cutoff date. Always verify important information from AI with reliable sources."}
                ],
                "quiz": [
                    {"q": "What is the core task ChatGPT is trained to do?", "options": ["Search the internet", "Predict the next word", "Understand human feelings", "Store all world knowledge"], "answer": 1},
                    {"q": "Why does ChatGPT sometimes make up false information?", "options": ["It's programmed to lie", "It predicts plausible text, not necessarily true text", "Its training data was wrong", "It doesn't have enough memory"], "answer": 1}
                ]
            }
        },
        {
            "title": "AI Ethics: Bias, Privacy, Deepfakes",
            "description": "The critical questions every AI practitioner must grapple with — building AI responsibly.",
            "content_type": "text",
            "estimated_mins": 35,
            "content_json": {
                "sections": [
                    {"heading": "AI Bias", "body": "AI learns from human-generated data. Human data contains human biases. A hiring AI trained on historical data (where most hired candidates were male) will discriminate against women — not because it's programmed to, but because it learned the pattern. Amazon's AI hiring tool was scrapped in 2018 for exactly this reason."},
                    {"heading": "Privacy", "body": "AI systems collect enormous amounts of personal data. Your location, your searches, your face, your voice, your behavior patterns. Who owns this data? Who can access it? What can it be used for? These are live legal and ethical debates happening right now."},
                    {"heading": "Deepfakes", "body": "AI can now generate hyper-realistic fake videos of anyone saying anything. Deepfakes are used to spread misinformation, manipulate elections, create non-consensual content, and commit fraud. Detecting deepfakes is an active research area."},
                    {"heading": "Who is Responsible?", "body": "If an AI-powered self-driving car kills someone, who is responsible — the passenger, the company, the programmer? If an AI denies your loan application, can you ask it to explain why? These questions are being debated by governments worldwide right now."},
                    {"heading": "Your Role", "body": "You will build AI systems. You will be responsible for their consequences. Learning to build AI ethically — with fairness, transparency, and respect for privacy — is not optional. It's the most important part of being an AI practitioner."}
                ],
                "quiz": [
                    {"q": "AI bias comes from:", "options": ["Programming errors", "Biases in training data", "Slow computers", "Lack of internet access"], "answer": 1},
                    {"q": "A deepfake is:", "options": ["A very good photo filter", "AI-generated fake video/audio of a person", "A type of VPN", "A social media account"], "answer": 1}
                ]
            }
        },
        {
            "title": "Grade 10 Project: Student Score Predictor",
            "description": "Build an AI model that predicts student exam scores based on their study habits and background.",
            "content_type": "project",
            "estimated_mins": 90,
            "content_json": {
                "requirements": [
                    "Collect data from at least 20 classmates (or use a provided dataset)",
                    "Features to collect: hours studied per week, attendance %, sleep hours, previous exam score",
                    "Target: final exam score",
                    "Train a Linear Regression model",
                    "Evaluate with Mean Absolute Error",
                    "Create a chart showing predicted vs actual scores",
                    "Discuss: is this model fair to all students? What biases might it have?"
                ],
                "rubric": {"model_performance": 35, "code_quality": 25, "visualisation": 20, "ethics_discussion": 20}
            }
        }
    ],
    11: [
        {
            "title": "NumPy: Fast Maths for AI",
            "description": "Master NumPy arrays — the engine behind every AI framework including TensorFlow and PyTorch.",
            "content_type": "coding",
            "estimated_mins": 45,
            "content_json": {
                "sections": [
                    {"heading": "Why NumPy?", "body": "Python lists are slow for maths. NumPy arrays are 100x faster. Every ML library (scikit-learn, TensorFlow, PyTorch) uses NumPy under the hood. Mastering NumPy is foundational for serious AI work."},
                    {"heading": "NumPy Basics", "body": "import numpy as np\narr = np.array([1, 2, 3, 4, 5])\nprint(arr * 2)        # [2, 4, 6, 8, 10]\nprint(arr.mean())     # 3.0\nprint(arr.std())      # std deviation\n\n# 2D arrays (matrices)\nmatrix = np.array([[1,2],[3,4],[5,6]])\nprint(matrix.shape)   # (3, 2)\nprint(matrix.T)       # transpose"}
                ],
                "starter_code": "import numpy as np\n\n# Image processing example\n# A 4x4 grayscale image (pixel values 0-255)\nimage = np.array([\n    [0, 50, 100, 150],\n    [50, 100, 150, 200],\n    [100, 150, 200, 250],\n    [150, 200, 250, 255]\n])\n\nprint('Image shape:', image.shape)\nprint('Brightest pixel:', image.max())\nprint('Average brightness:', image.mean())\n\n# Normalise to 0-1 (common preprocessing step in AI)\nnormalised = image / 255.0\nprint('Normalised range:', normalised.min(), 'to', normalised.max())\n\n# Flatten to 1D (for feeding into a neural network)\nflattened = image.flatten()\nprint('Flattened shape:', flattened.shape)",
                "exercises": [
                    {"title": "Matrix Multiplication", "prompt": "Create two 3x3 matrices A and B. Compute A @ B (matrix multiplication). Compute the element-wise product (A * B). What's the difference?"}
                ]
            }
        },
        {
            "title": "Advanced Pandas: Data Wrangling",
            "description": "Clean, merge, and transform messy real-world data — the skill that takes 80% of a data scientist's time.",
            "content_type": "coding",
            "estimated_mins": 50,
            "content_json": {
                "sections": [
                    {"heading": "Messy Data is the Norm", "body": "Real data is never clean. Missing values, duplicates, wrong data types, inconsistent formats. Data cleaning (wrangling) takes 80% of a data scientist's time. Pandas makes it manageable."},
                    {"heading": "Key Operations", "body": "df.dropna()           # drop rows with missing values\ndf.fillna(0)          # fill missing with 0\ndf.drop_duplicates()  # remove duplicate rows\ndf['col'].astype(int) # convert type\ndf.rename(columns={'old': 'new'})\ndf.groupby('team').mean()  # group and aggregate\ndf1.merge(df2, on='id')    # join two DataFrames"}
                ],
                "starter_code": "import pandas as pd\nimport numpy as np\n\n# Messy employee data\ndata = {\n    'name': ['Alice', 'Bob', 'Charlie', 'Alice', None, 'Eve'],\n    'department': ['Eng', 'Mktg', 'Eng', 'Eng', 'HR', 'Mktg'],\n    'salary': [90000, 75000, np.nan, 90000, 60000, 80000],\n    'years': [3, 5, 2, 3, 1, 4]\n}\ndf = pd.DataFrame(data)\n\nprint('Original data:')\nprint(df)\nprint('\\nMissing values:', df.isna().sum().to_dict())\n\n# Clean\ndf = df.drop_duplicates()\ndf['salary'] = df['salary'].fillna(df['salary'].median())\ndf = df.dropna(subset=['name'])\n\nprint('\\nCleaned data:')\nprint(df)\n\n# Analysis\nprint('\\nAverage salary by department:')\nprint(df.groupby('department')['salary'].mean().round(0))",
                "exercises": [
                    {"title": "School Data Cleaning", "prompt": "Create a DataFrame with 15 students, some with missing marks, some duplicates. Clean it. Find top 3 students per subject."}
                ]
            }
        },
        {
            "title": "Scikit-learn: Machine Learning in Python",
            "description": "Build Random Forest, SVM, and ensemble models — the workhorses of applied ML.",
            "content_type": "coding",
            "estimated_mins": 55,
            "content_json": {
                "sections": [
                    {"heading": "Scikit-learn API", "body": "Every scikit-learn model follows the same pattern:\n1) model = SomeModel()\n2) model.fit(X_train, y_train)\n3) predictions = model.predict(X_test)\n4) score = accuracy_score(y_test, predictions)\nLearn this pattern once, use it for 50+ models."},
                    {"heading": "Random Forest", "body": "A Random Forest trains 100+ Decision Trees, each on a random subset of data and features. Final prediction = majority vote. Why is it better than one tree? Error of the group < error of any individual. This is called ensemble learning."}
                ],
                "starter_code": "from sklearn.ensemble import RandomForestClassifier\nfrom sklearn.model_selection import train_test_split, cross_val_score\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.metrics import classification_report\nimport numpy as np\n\n# Student pass/fail prediction\n# Features: [study_hours, attendance_pct, prev_score, sleep_hours]\nnp.random.seed(42)\nn = 200\nstudy = np.random.uniform(1, 10, n)\nattendance = np.random.uniform(40, 100, n)\nprev_score = np.random.uniform(30, 100, n)\nsleep = np.random.uniform(4, 9, n)\n\n# Pass if study > 5 or (attendance > 75 and prev_score > 60)\npassed = ((study > 5) | ((attendance > 75) & (prev_score > 60))).astype(int)\n\nX = np.column_stack([study, attendance, prev_score, sleep])\ny = passed\n\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\nmodel = RandomForestClassifier(n_estimators=100, random_state=42)\nmodel.fit(X_train, y_train)\n\nprint('Accuracy:', model.score(X_test, y_test))\nprint('\\nClassification Report:')\nprint(classification_report(y_test, model.predict(X_test)))\n\n# Feature importance\nfeature_names = ['Study Hours', 'Attendance', 'Previous Score', 'Sleep']\nfor name, imp in sorted(zip(feature_names, model.feature_importances_), key=lambda x: -x[1]):\n    print(f'{name}: {imp:.3f}')",
                "exercises": [
                    {"title": "Iris Classifier", "prompt": "Use sklearn.datasets.load_iris(). Train a RandomForestClassifier. Achieve >95% accuracy on test set. Show confusion matrix."}
                ]
            }
        },
        {
            "title": "Deep Learning: Neural Networks",
            "description": "Understand how neural networks work visually, then build one with Keras.",
            "content_type": "coding",
            "estimated_mins": 60,
            "content_json": {
                "sections": [
                    {"heading": "How a Neuron Works", "body": "A neuron takes inputs, multiplies each by a weight, sums them up, and applies an activation function. y = activation(w1*x1 + w2*x2 + ... + b). The weights are learned during training."},
                    {"heading": "Layers", "body": "Input layer: your data (784 pixels for a 28x28 image). Hidden layers: where learning happens. Output layer: your prediction. More hidden layers = 'deeper' network = 'deep learning'."},
                    {"heading": "Keras: Easy Deep Learning", "body": "from tensorflow import keras\nmodel = keras.Sequential([\n    keras.layers.Dense(128, activation='relu'),\n    keras.layers.Dense(64, activation='relu'),\n    keras.layers.Dense(10, activation='softmax')  # 10 classes\n])\nmodel.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])\nmodel.fit(X_train, y_train, epochs=10)"}
                ],
                "starter_code": "from tensorflow import keras\nimport numpy as np\n\n# Load MNIST handwritten digits dataset\n(X_train, y_train), (X_test, y_test) = keras.datasets.mnist.load_data()\n\n# Preprocess\nX_train = X_train.reshape(-1, 784) / 255.0\nX_test = X_test.reshape(-1, 784) / 255.0\n\n# Build model\nmodel = keras.Sequential([\n    keras.layers.Dense(128, activation='relu', input_shape=(784,)),\n    keras.layers.Dropout(0.2),\n    keras.layers.Dense(64, activation='relu'),\n    keras.layers.Dense(10, activation='softmax')\n])\n\nmodel.compile(\n    optimizer='adam',\n    loss='sparse_categorical_crossentropy',\n    metrics=['accuracy']\n)\n\n# Train\nhistory = model.fit(X_train, y_train, epochs=5, validation_split=0.1, verbose=1)\ntest_loss, test_acc = model.evaluate(X_test, y_test)\nprint(f'Test accuracy: {test_acc:.4f}')",
                "exercises": [
                    {"title": "Fashion MNIST", "prompt": "Use keras.datasets.fashion_mnist instead of regular MNIST. Same structure. Try to achieve 88%+ accuracy. Add one more hidden layer if needed."}
                ]
            }
        },
        {
            "title": "NLP: Text Classification and Sentiment Analysis",
            "description": "Teach a machine to understand text — classify news articles, detect sentiment in reviews.",
            "content_type": "coding",
            "estimated_mins": 55,
            "content_json": {
                "sections": [
                    {"heading": "How Computers Read Text", "body": "Computers don't understand words. We convert words to numbers using techniques like: Bag of Words (count word frequencies), TF-IDF (weight rare words more), Word Embeddings (represent meaning in vectors — word2vec, GloVe)."},
                    {"heading": "TF-IDF + Classification", "body": "from sklearn.feature_extraction.text import TfidfVectorizer\nvectorizer = TfidfVectorizer(max_features=5000)\nX = vectorizer.fit_transform(texts)\n# X is now a matrix of numbers — feed to any classifier!"}
                ],
                "starter_code": "from sklearn.feature_extraction.text import TfidfVectorizer\nfrom sklearn.naive_bayes import MultinomialNB\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.metrics import classification_report\n\n# Movie reviews (positive/negative)\ntexts = [\n    'Amazing movie, loved every minute', 'Great acting and story',\n    'Brilliant film, highly recommended', 'Fantastic performance',\n    'Loved the storyline and characters', 'Excellent direction',\n    'Worst movie ever made', 'Terrible acting, complete waste',\n    'Boring and predictable plot', 'Awful, avoid this movie',\n    'Disappointing, expected much better', 'Poor screenplay'\n]\nlabels = [1,1,1,1,1,1, 0,0,0,0,0,0]  # 1=positive, 0=negative\n\n# Build pipeline\npipeline = Pipeline([\n    ('tfidf', TfidfVectorizer()),\n    ('clf', MultinomialNB())\n])\npipeline.fit(texts, labels)\n\n# Test\ntest_reviews = [\n    'I loved this film, incredible story',\n    'Waste of time, very bad movie'\n]\nfor review, pred in zip(test_reviews, pipeline.predict(test_reviews)):\n    print(f'{\"POSITIVE\" if pred==1 else \"NEGATIVE\"}: {review}')",
                "exercises": [
                    {"title": "Product Review Classifier", "prompt": "Collect 30+ Amazon product reviews (10+ positive, 10+ negative, 10+ neutral). Train a classifier. What's the accuracy?"}
                ]
            }
        },
        {
            "title": "Grade 11 Project: Fake News Detector",
            "description": "Build an NLP classifier that detects fake news articles — a real-world impact project.",
            "content_type": "project",
            "estimated_mins": 120,
            "content_json": {
                "requirements": [
                    "Use a fake news dataset (kaggle.com has several free ones)",
                    "Preprocess text: remove stopwords, punctuation, lowercase",
                    "Try at least 3 classifiers: Naive Bayes, Logistic Regression, Random Forest",
                    "Use TF-IDF or word embeddings for features",
                    "Achieve at least 85% accuracy on test set",
                    "Build a simple interface: user pastes headline, model says Real/Fake",
                    "Discuss: what could go wrong with this model in the real world?"
                ],
                "rubric": {"model_performance": 30, "code_quality": 25, "interface": 20, "ethics_discussion": 25}
            }
        }
    ],
    12: [
        {
            "title": "How LLMs Work: The Technical Truth",
            "description": "Go beyond the surface — understand transformers, attention mechanisms, and RLHF at a technical level.",
            "content_type": "text",
            "estimated_mins": 40,
            "content_json": {
                "sections": [
                    {"heading": "Transformers and Self-Attention", "body": "The Transformer architecture (Vaswani et al., 2017 — 'Attention is All You Need') processes all tokens simultaneously. For each token, it computes attention scores against every other token — 'how much should I attend to each other word?' This lets the model understand long-range dependencies that older RNNs couldn't capture."},
                    {"heading": "Pre-training and Fine-tuning", "body": "LLMs are trained in stages. Pre-training: predict next token on massive dataset (trillions of tokens). Fine-tuning: adapt to specific tasks (chat, code, instructions). RLHF (Reinforcement Learning from Human Feedback): humans rank outputs, model learns to produce higher-ranked outputs. This is what makes ChatGPT helpful."},
                    {"heading": "Prompt Engineering", "body": "How you phrase your prompt dramatically affects output quality. Zero-shot: just ask. Few-shot: give 2-3 examples in the prompt. Chain-of-thought: 'Let's think step by step'. System prompts: define the AI's role and constraints. Prompt engineering is a real skill worth developing."},
                    {"heading": "Limitations and Current Research", "body": "Context window limits (though growing). Hallucinations — no built-in fact-checking. No real-time knowledge. Inference is expensive. Emerging solutions: RAG (Retrieval Augmented Generation), agents with tool use, multimodal models."}
                ],
                "quiz": [
                    {"q": "What does RLHF stand for?", "options": ["Really Large Human Feedback", "Reinforcement Learning from Human Feedback", "Random Learning with Human Features", "Recursive Learning from Hidden Functions"], "answer": 1},
                    {"q": "Few-shot prompting means:", "options": ["Using a small model", "Giving examples in the prompt", "Training on less data", "Using fewer GPU"], "answer": 1}
                ]
            }
        },
        {
            "title": "Computer Vision: Image Classification with CNNs",
            "description": "Build a Convolutional Neural Network that recognises images — the technology behind Face ID, self-driving cars, and medical AI.",
            "content_type": "coding",
            "estimated_mins": 60,
            "content_json": {
                "sections": [
                    {"heading": "Why CNNs for Images?", "body": "A 224x224 colour image has 150,528 numbers. A Dense layer connecting all of them would have 150,528 × (layer size) weights — too many to train. CNNs use 'convolutional filters' — small windows (3x3) that slide over the image, detecting local patterns like edges, textures, and shapes. Far fewer parameters, much better at images."},
                    {"heading": "CNN Architecture", "body": "Conv2D layer → MaxPooling → Conv2D → MaxPooling → Flatten → Dense → Output. Each Conv layer detects progressively higher-level features: edges → shapes → parts → objects."}
                ],
                "starter_code": "from tensorflow import keras\nfrom tensorflow.keras import layers\nimport numpy as np\n\n# CIFAR-10: 60,000 colour images, 10 classes\n(X_train, y_train), (X_test, y_test) = keras.datasets.cifar10.load_data()\n\n# Normalise\nX_train, X_test = X_train / 255.0, X_test / 255.0\n\n# CNN Model\nmodel = keras.Sequential([\n    layers.Conv2D(32, (3,3), activation='relu', input_shape=(32,32,3)),\n    layers.MaxPooling2D(2,2),\n    layers.Conv2D(64, (3,3), activation='relu'),\n    layers.MaxPooling2D(2,2),\n    layers.Conv2D(64, (3,3), activation='relu'),\n    layers.Flatten(),\n    layers.Dense(64, activation='relu'),\n    layers.Dense(10, activation='softmax')\n])\n\nmodel.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])\nmodel.summary()\n\nhistory = model.fit(X_train, y_train, epochs=10, validation_split=0.1)\ntest_acc = model.evaluate(X_test, y_test)[1]\nprint(f'CNN accuracy on CIFAR-10: {test_acc:.4f}')",
                "exercises": [
                    {"title": "Custom Image Classifier", "prompt": "Collect 50+ images of 3 categories (e.g., dogs, cats, cars). Use transfer learning (MobileNetV2 or EfficientNetB0) to classify them. Transfer learning should give >90% accuracy with very little data."}
                ]
            }
        },
        {
            "title": "AI in the Real World: Healthcare, Agriculture, Finance",
            "description": "Understand how AI is transforming every industry — and what career paths exist for you.",
            "content_type": "text",
            "estimated_mins": 35,
            "content_json": {
                "sections": [
                    {"heading": "AI in Healthcare", "body": "Google's DeepMind detects eye diseases from retinal scans with expert-level accuracy. AI reads chest X-rays to detect tuberculosis, COVID, and cancer. Drug discovery (finding new medicines) used to take 10 years — AI is cutting it to months. At AIIMS, AI-assisted diagnosis is already being piloted."},
                    {"heading": "AI in Agriculture", "body": "Drones with AI cameras scan crops and detect disease before it spreads. Precision irrigation: AI analyses soil sensors and weather data to water exactly the right amount at the right time. In India, the iCow and Cropin platforms use AI to help millions of farmers."},
                    {"heading": "AI in Finance", "body": "Fraud detection: AI spots unusual patterns in real-time (your bank's fraud alert). Algorithmic trading: AI makes millions of trades per second based on market patterns. Credit scoring: AI evaluates loan applications using thousands of data points. Regulatory concern: is it fair? Who is accountable?"},
                    {"heading": "Career Paths", "body": "ML Engineer: builds and deploys models. Data Scientist: finds insights. AI Researcher: pushes the frontier. AI Product Manager: defines what to build. AI Ethics Officer: ensures fairness and compliance. All of these are high-paying, high-impact careers that didn't exist 15 years ago."}
                ],
                "quiz": [
                    {"q": "What did DeepMind's AI achieve in healthcare?", "options": ["Performed surgery", "Detected eye diseases from retinal scans", "Replaced all doctors", "Invented new medicines alone"], "answer": 1},
                    {"q": "Precision irrigation uses AI to:", "options": ["Make rain artificially", "Water crops exactly when and where needed", "Predict crop prices", "Harvest crops automatically"], "answer": 1}
                ]
            }
        },
        {
            "title": "Building AI Products: From Idea to Deployment",
            "description": "The complete lifecycle of an AI product — how real AI companies build and ship.",
            "content_type": "text",
            "estimated_mins": 40,
            "content_json": {
                "sections": [
                    {"heading": "The AI Product Lifecycle", "body": "1) Problem definition: what pain are you solving? 2) Data strategy: what data do you need? Where does it come from? 3) Model selection: build vs buy vs use API. 4) Evaluation: what metrics matter? Accuracy? Fairness? 5) Deployment: how will users access it? API? App? 6) Monitoring: models degrade over time as the world changes."},
                    {"heading": "Build vs Buy vs API", "body": "Build from scratch: maximum control, very expensive, only for specialised use cases. Fine-tune an existing model: middle ground. Use an API (OpenAI, Anthropic, Google): fastest, most accessible, costs per API call. Most AI products today use APIs. You can build a sophisticated AI product without training a single model."},
                    {"heading": "Deployment Stack", "body": "Frontend: React, Next.js. Backend: FastAPI, Flask. AI API: Gemini, GPT-4, Claude. Database: PostgreSQL for structured data. Vector DB (Pinecone, Weaviate) for semantic search. Hosting: Vercel, Railway, AWS, GCP. Monitoring: track API costs, error rates, user feedback."},
                    {"heading": "The MVP Mindset", "body": "Don't build the perfect AI system. Build the minimum viable product. Ship it to 10 real users. Learn what they actually need. Iterate. The most successful AI companies (OpenAI, Anthropic, Hugging Face) all started with simple, focused products."}
                ],
                "quiz": [
                    {"q": "For most new AI products, the fastest approach is:", "options": ["Train a model from scratch", "Use an existing AI API", "Hire 50 ML engineers", "Wait for better hardware"], "answer": 1},
                    {"q": "Why do models need monitoring after deployment?", "options": ["They get bored", "The real world changes and model performance can degrade", "Servers get tired", "Users hack them"], "answer": 2}
                ]
            }
        },
        {
            "title": "Grade 12 Capstone: Build a Real AI Product",
            "description": "Your final project — identify a real problem, build an AI solution, and present it to a panel.",
            "content_type": "project",
            "estimated_mins": 480,
            "content_json": {
                "requirements": [
                    "Team of 2-4 students",
                    "Identify a real problem in your school, city, or community",
                    "Build an AI-powered solution (web app, bot, or tool)",
                    "Must use at least one AI/ML component (API, trained model, or NLP)",
                    "Working demo: judges can interact with it live",
                    "5-minute pitch + 5-minute Q&A",
                    "Technical writeup: problem, approach, data, challenges, what you'd do with more time"
                ],
                "sample_projects": [
                    "AI tutor for regional language students",
                    "Crop disease detector using phone camera",
                    "Traffic violation detection for local municipality",
                    "Mental health support chatbot for students",
                    "AI-powered study planner for board exam students"
                ],
                "judging_criteria": {
                    "problem_relevance": 20,
                    "technical_execution": 25,
                    "ai_ml_component": 25,
                    "presentation": 15,
                    "innovation": 15
                }
            }
        }
    ]
}

async def seed_curriculum(db: AsyncSession):
    """Seed the default Grade 6-12 AI curriculum if not already present."""
    existing = await db.execute(select(Lesson).where(Lesson.is_global == True).limit(1))
    if existing.scalar_one_or_none():
        return  # already seeded

    for grade, lessons in GRADE_CURRICULUM.items():
        for idx, lesson_data in enumerate(lessons):
            lesson = Lesson(
                grade=grade,
                title=lesson_data["title"],
                description=lesson_data.get("description"),
                content_type=lesson_data.get("content_type", "text"),
                content_json=lesson_data.get("content_json"),
                subject="AI Fundamentals",
                estimated_mins=lesson_data.get("estimated_mins", 30),
                order_index=idx,
                is_global=True,
                school_id=None,
            )
            db.add(lesson)

    await db.commit()
