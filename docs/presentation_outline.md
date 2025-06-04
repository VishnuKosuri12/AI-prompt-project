AI Coding
    What is AI Coding?
    • Problem solving
        Cova
    • Coding Assistant
        GitHub Copilot
        Amazon Q
        Tabnine
        Codeium
        JetBrains AI Assistant
    • Code authoring
        Cline, VS Code, AWS Bedrock
How I got here
    • Y Combinator -- 25% of their startups are using AI to build their code bases
    • AI boosts developer productivity 10-30%
    • AI assisted developers write 12-15% more code
    • 25% of Google's code is now AI generated
I have questions
    • Can it handle a large code base?
    • Can it keep code organized and clean?
    • What about modifying a large code base?
    • Can it debug code that's broken?
My Goals
    • Build a large codebase using AI
    • Learn how to prompt it to get quality results
    • Try different approaches to see what it generates
    • Understand what it can and can't generate
    • Bring my learnings back to the organization
What are we building?
    • ChemTrack -- a chemical tracking application
    • Architecture
        Internally facing application
        Load balancers for interfacing
        ECS environment running multiple containers
        RDS PostgreSQL database
    • Technologies used
        Python: Flask, Jinja, FastAPI 
        HTML, Javascript
        SQL (PostgreSQL dialect)
        Docker
        Bash -- scripting
        AWS: environment, CLI, API (boto3), CloudFormation
What did we learn?
    • Prompting
        ○ Detail is good but not always necessary or beneficial
        ○ Remind it where things are located and how you want things structured
        ○ Be specific if you are looking for specific outcomes
        ○ Use shared files for common information
    • Generated Code
        ○ Structure and organization
        ○ Code appearance
        ○ Maintainability
    • What it can do
        ○ Add new modules
        ○ Feature enhancements
        ○ Database enhancements
        ○ Generate database data
        ○ Diagram the application
        ○ Refactor code structure
        ○ Refactor user interface
Working with AI
    • Commands and Responses
    Seasoned developer and the gorilla with a hammer
        (insert picture here)
    • Good things
        ○ Maintaining documentation (readme)
        ○ Building and maintaining scripts for build and deploy
        ○ Using interesting technologies and/or techniques
        ○ Showing signs of good application structure
        ○ Refactoring code
        ○ Pretty good at layout
    • Odd things
        ○ Flipping between two solutions when debugging
        ○ Proposing multiple solutions but picking one without asking
        ○ Diff Edit Mismatch
            (insert picture here)
        ○ Bad code -- that it caught itself
        ○ Running out of steam and writing incomplete files -- then fixing it
    • Bad things
        ○ Removing my changes
        ○ Making a change in some modules but not in others
        ○ Moving files from one place to another (duplicating)
        ○ Bad code (occasional)
        ○ Not great at debugging
    • Things to watch
        ○ Be clear about names and paths
        ○ Be clear about technolgies you want used
        ○ Remind it of changes that will impact many parts of the application
