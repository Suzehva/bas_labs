## Inspiration

Mitigating climate change is only possible through a patchwork of collective action. The future of our planet will be determined by our ability to radically change previous destructive corporate processes. However, companies can often struggle to find concrete solutions and actions to reduce their carbon footprint while advancing their business goals. 

We partner with Race to Zero to create a **climate action matcher**. Through a user-friendly interface and an agentic workflow grounded in tool-usage, we match THE USER COMPANY with relevant UN-backed initiatives and provide them with sustainability reports from similar companies and peer corporate actions to inspire concrete action. 

Ultimately, we want to transform the way we approach climate change – from apathy to collective action. By making the connections between companies and their initiatives, we want to show that action is possible, popular, and powerful – especially when done together as an industry, nation, and planet.

## What it does

Our tool matches companies to relevant climate initiatives. We provide an agentic system with tools like
RAG embedding search on a custom database of company sustainability reports and UN-backed initiatives, web scraping on websites like https://zerotracker.net/ and https://nzdpu.com/home and more to discover corporate climate actions. 

## How we built it

DAIN Butterfly: We use the DAIN Butterfly agentic workflow + tool usage as our central orchestrator and user interface interactions. We built custom tools that find similar companies based on industry sector, match companies to UN-backed collective corporate initiatives, and find relevant climate actions from hundreds of sustainability reports from a database we built. We used the DAIN UI components to format the responses in an engaging and clear way.
InterSystems Embedding Database: We use InterSystems as our database. We collected and embedded 172 UN-backed initiatives with descriptions, and over 17,000 paragraphs from scraped sustainability reports.
NVIDIA Llama Embeddings: We use Llama-3.2-nv-embedqa-1b-v2 embeddings for our embedding database and query embedding in our RAG vector search.
LangChain: We use lang chain to load sustainability PDF reports directly from the web and recursively split the text for subsequent chunk embeddings.
Google Gemini Scoring and Classification: We implement company sector classification using Gemini Flash Experimental 2.0. Moreover, we use Gemini to score corporate actions based on their reproducibility, and return on investment for action ranking and matching.
Scrapybara: We implement an agent to find concrete PDF links on corporate websites that may be deep in the link structure of the page.
Selenium Web Browser: We implement web scraping using Selenium.

## Challenges we ran into

Finding relevant climate actions first proved tricky since sustainability reports can be quite vague and embedding similarity search works best if we try to match the target report structure as closely as possible. We ended up solving the problem by having the DAIN agent brainstorm climate initiatives the company *could be doing* and then **verify** these ideas by finding **real climate actions by companies** in their sustainability reports.

Another challenge was to have the agent perform enough actions to take advantage of all our tools. We ended up spending some time on prompt engineering and writing clearer tool descriptions which had a clear boost in performance.

## Accomplishments that we're proud of

Created an end-to-end pipeline for matching companies with sustainability efforts.
Created an embedding vector database with hundreds of sustainability reports to be open-sourced to the broader community after the event.
Developed core technical skills in web scraping, database manipulation, embedding models, document parsing, and tool creations.
Built our understanding of sustainability reporting and found many avenues for continued work.

## What We Learned

We learned a ton during the hackathon! On the technical side, we learned web scraping, document embeddings, how to work with Docker containers, and connecting python and typescript! On the environmental side we opened the door into the vast world of sustainability reporting and tracking. It was very inspiring to see all the initiatives already underway, and we are incredibly excited to keep pushing for more action.

## What's next for BAS Climate Action Matcher

Extend the initiatives into a dynamic knowledge graph to track the impacts of climate actions.
Extend scoring to include nature based solutions, collaborations, estimated impact, and cost.
Create a dashboard to standardize climate reporting for easier comparison.
