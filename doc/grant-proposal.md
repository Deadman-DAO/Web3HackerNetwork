# Part 1 - Proposal

## Name of Project: *DeadmanDAO Web3 Hacker Network*

## Proposal in one sentence

Create a decentralized network analytics data pipeline for team-builders to find Web3 hackers and to understand the developer-developer multilevel network.

## Description of the project and what problem it is solving

Finding Web3 developers to work with on bounties, hackathons, and grants is challenging. You can go to Discord and post, but your reach will be limited. You can search on LinkedIn, but that data is often stale or aspirational. Web3 Hacker Network will provide analytics about the network of people who are building Web3.

It can be challenging to scale a team for a project without the costly HR departments in Web2. This project is a first iteration toward facilitating decentralized talent mobility.

## Grant Deliverables

* Raw dataset showing Gitcoin user participation in bounties, hackathons, and grants.
* User-User sparse matrix dataset showing strength of association between Web3 hackers.
* NetworkX model of the network representing the user-user edges.
* Initial analysis of the dataset and model to assess fitness to task and gaps to be filled.
* User experience that takes a Gitcoin ID and finds the network path to nearby or strongly connected hackers.

## Project Category: *Unleash Data*

## Earmark: *New Project*

## What is the final product?

Web3 Hacker Network is the first layer in a multi-layer network model that will be used to increase tech talent mobility in Web3. The final product is a decentralized autonomous opportunity discovery engine for hackers, backers, projects, and teams. It will provide some of the services of hiring managers and HR departments from Web2, but in a fashion that is more aligned with the changes happening in the transition to Web3.

Web2 notions of long employment with a single firm are breaking down. In Web3 hackers are working across more projects for shorter periods of time, resulting in greater innovation through increased cross-pollination of ideas. Opportunity discovery and resource placement in this more dynamic environment will have to move faster and cost less than Web2 HR-driven hiring pipelines.

Network theory, machine learning, and the open data about work history in Web3 allows for automated opportunity discovery. Web3 Hacker Network is breaking ground on a long-term project that will serve hackers, backers, projects, and teams. The final product will present users with a menu of opportunities that match their role in the ecosystem and preferences for developing their professional life.

## Which value add criteria are we focusing on? Why do we believe we will do well?

### option 1: Usage of Ocean
- how well might the project drive usage of Ocean. Measure with e.g. Data Consume Volume, # assets published, TVL (total value locked), Network Revenue, # active users, # funded projects.

Network Revenue: The first iteration will focus on Gitcoin data. In the past 2.5 years, Gitcoin grants have totaled over $10m. Bounties have totaled more than $7m in the past 12 months. A reasonable estimate of expected Gitcoin funding is $500k/month. The value of improved talent mobility based on the Gitcoin dataset is a function of that revenue. A conservative estimate of 5% value increase would be $25,000 value created per month. For comparison, headhunters charge 20% - 25%.

We are starting with Gitcoin because it is a highly diverse and volatile gathering point for Web3 hackers. This makes it a particularly rich dataset for initial development of the network model. Future iterations will pull in project and team data from an increasingly broad array of sources. These will include MolochDAO, Harmony, Genesis DAO, and A16Z - cashflow that dwarfs Gitcoin.

And this is only the beginning. We expect Web3 to surpass Web2 in the long run, and for dynamic team composition to be the new normal. There will be hundreds of millions of dollars worth of resource assignments happening every month. Tools like this one will be responsible for millions of dollars in increased talent placement efficiency per month.

### option 2: Viability
- what is the chance of success of the project

Our data engineering and data science person built Spark-based DE and ML systems at Amazon on terabyte datasets, then managed a team doing the same through several deliveries on time and on budget. Our React engineer designed and delivered US DoD warehouse automation systems on strict timelines and budgets.

Over the coming months and iterations we will need to expand the team to deliver the larger vision. Our lead grew a team at Amazon from 3 people to 12 people in one year while delivering on an aggressive project schedule. His ability to find the right people, build team spirit, and motivate enthusiastic engagement were the core of his success.

There is always risk, and this is a highly exploratory project. Nothing is guaranteed, but our core team is strong and the data we need is available.

### option 4: Adding value to the overall community
- how well does the outcome of the project add value to the Ocean community / ecosystem

The long-term project will be integral to the work cycle of a significant portion of Web3 producers. This product will expose a large number of active Web3 hackers and team builders to Ocean Protocol.

## Funding Requested: *$3000*

## Proposal Wallet Address: *0xAE6A3d5F73cDA0180eeDBAa5aA801D68b3491931* (500 OCEAN purchase TBD)

## Have you previously received an OceanDAO Grant?: *No*

## Team Website: [wiki.DeadmanDAO.com](https://wiki.deadmandao.com/)

## Discord Handle: *DeadmanBob#7342*

## Project lead full name: *Robert Bushman*

## Project lead email: *[TBK: pick a way to obfuscate this]*

## Country of Residence: United States of America

# Part 2 - Team

## 2.1 Core Team

### Robert Bushman

* Role: Project Manager, Developer
* Relevant Credentials:
    * LinkedIn: https://www.linkedin.com/in/robert-bushman-9316412/
* Background / Experience:
    * L6 SDE / L6 SDM at Amazon (data engineering & data science)
    * Big Data Architect at Choice Hotels
    * Senior Software Engineer at Apple

### Matt Enke

* Role: Developer
* Relevant Credentials
    * LinkedIn: https://www.linkedin.com/in/matt-enke-b234ba51/
* Background / Experience
    * System Architect and Engineer: US DoD Warehouse Automation

# Part 3 - Proposal Details

## 3.1 Details

We propose building an initial iteration of a network analytics data pipeline on Ocean Protocol. It will act as both a demonstration of network analytics using NetworkX and as a jumping off point for a richer hacker discovery system going forward. Two engineers will be involved during the first iteration. Future iterations will expand the project based on demand, feedback, and developer engagement.

## 3.4 Which Ocean-powered data market will data be published on?

Initial deployment will be on Ocean Market. In subsequent rounds we will explore the RoI of forking our own market. We have system administration experience, so it's just a question of where we want to allocate our time during each iteration.

## 3.9 Project Deliverables - Roadmap

### Any prior work completed thus far? Details?

We have begun pulling the data from Gitcoin's REST API and writing it to a database to facilitate initial dataset analysis.

### What is the project roadmap?

1. Milestone 1 (End of Week 1): Gitcoin API calls capable of pulling user, bounty, and grant history.
1. Milestone 2 (End of Week 2): Store the raw data from Milestone 1 in Ocean Protocol space.
1. Milestone 3 (End of Week 3): Generate sparse matrices from the raw data and store in Ocean Protocol space.
1. Milestone 4 (End of Week 4): Generate NetworkX models in Ocean Protocol space.
1. Milestone 5 (End of Week 5): Produce analysis of dataset gaps and fitness for the task.
1. Milestone 6 (End of Week 6): Expose the UX for querying the network.
1. Milestone 7 (End of week 7): Refine wiki documentation for public consumption and announce.
1. Milestone 8 (End of week 8): Write the grant for Ocean Round 17.

### What is the team's future plans and intentions?

We intend to continue extending the work as long as we are gaining traction and improving talent mobility.

## 3.10 Additional Information

I intend to submit a grant to Gitcoin at the same time that I submit to Ocean Protocol.
