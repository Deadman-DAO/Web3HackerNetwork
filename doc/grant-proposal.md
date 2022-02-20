# Part 1 - Proposal

## Name of Project: *DeadmanDAO Web3 Hacker Network*

## Proposal in one sentence

Create a decentralized network analytics data pipeline for discovering Web3 hackers and understanding the developer-developer multilevel network.

## Description of the project and what problem it is solving

Finding Web3 developers to work with on bounties, hackathons, and grants is challenging. You can go to Discord and post, but your reach will be limited. You can search on LinkedIn, but that data is often stale or aspirational.

Web3 Hacker Network will provide analytics about the network of people who are building Web3. Developers in Web3 are doing a great job taking an active role in building their networks, but without the costly HR departments in Web2 it can be challenging to scale a team for a project. This project is a first step toward facilitating decentralized talent mobility.

## Grant Deliverables

* Raw dataset showing Gitcoin user participation in bounties, hackathons, and grants.
* User-User sparse matrix datasets showing strength of association between Web3 hackers.
* NetworkX model of the network representing the user-user edges.
* Initial set of metrics that express connectedness of the network.
* User experience that takes a Gitcoin ID and finds the network path to nearby or strongly connected hackers.

## Project Category: *Unleash Data*

## Earmark: *New Project*

## What is the final product?

Web3 Hacker Network is the initial network layer of a system for increasing tech talent mobility in Web3. The final product is a decentralized autonomous opportunity discovery engine for hackers, backers, projects, and teams. It will provide some of the services of hiring managers and HR departments from Web2, but in a fashion that is more aligned with the changes happening in the transition to Web3.

Web2 notions of long employement with a single firm are breaking down. In Web3 hackers are working across more projects in a shorter period of time, resulting in greater innovation through increased cross-pollination of ideas. Opportunity discovery and resource placement in this more dynamic environment will have to move faster and cost less than Web2 HR-driven hiring pipelines.

Network theory, machine learning, and the open data about work history in Web3 allows for automated opportunity discovery. Web3 Hacker Network is breaking ground on a long-term project that will serve hackers, backers, projects, and teams. The final product will present users with a menu of opportunities that match their needs and preferred path forward.

## Which value add criteria are we focusing on? Why do we believe we will do well?

### option 1: Usage of Ocean
- how well might the project drive usage of Ocean. Measure with e.g. Data Consume Volume, # assets published, TVL (total value locked), Network Revenue, # active users, # funded projects.

Network Revenue: [TBD: trim this way down, make sure Tom and Matt are on board] This could be large, because there will be a very large number of users and the value of technology bounties is high and climbing. We could capture some share of each successful placement that flows through the network. But is that the direction we want to go? Do we want to maximize RoI, or do we want to maximize velocity of talent? Don't get me wrong, money is nice and we have bills to pay. But there is something important going on here. If we had the option of doubling the size of the network or making twice as much money - and the half-price option was enough to pay the bills - we would rather expand the positive influence. This is the age of opportunity for technologists and we are good at what we do. If we make the hacker marketplace stronger, we can go do a high pay bounty if we need to boost our income. This product can be long on pro-social and self-fulfillment and still have sufficient cashflow to keep growing.

Number of Active Users: Considering that our focus is on network growth and positive impact over money, I believe the number of active users will be large. Web3 is a place of high project churn. There are a lot of Web3 hackers and team builders that need better tools to make placements as simple and effective as possible.

### option 2: Viability
- what is the chance of success of the project

Our network theory advisor was a research scientist at Sandia Laboratories developing network models to understand ebola outbreaks and the impact of social network influence on probability to smoke cigarettes. Our data engineering and data science person built Spark-based DE and ML systems at Amazon on terabyte datasets, then managed a team doing the same through several deliveries on time and on budget. Our React engineer designed and delivered US DoD warehouse automation systems on strict timelines and budgets.

Over the coming months we will need to expand the team to deliver the larger vision. Our lead grew a team at Amazon from 3 people to 12 people in one year while delivering on an aggressive project schedule. His ability to find the right people, build team spirit, and motivate enthusiastic engagement were the core of his success.

There is always risk, and this is a highly exploratory project. Nothing is guaranteed, but our team is strong and the data we need is available.

### option 4: Adding value to the overall community
- how well does the outcome of the project add value to the Ocean community / ecosystem

The long-term project will be integral to the work cycle of a significant portion of Web3 producers. This product will expose a large number of active Web3 hackers and team builders to Ocean Protocol.

## Funding Requested: *$3000*

## Proposal Wallet Address: *[TBK, will my Coinbase-hosted wallet work?]* (must have 500 OCEAN in wallet, must be an Ethereum wallet)

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

## Part 2.2 Advisors

### Tom Moore

* Role: Network Theory Advisor
* Relevant Credentials
    * LinkedIn: https://www.linkedin.com/in/thomas-moore-90a7597/
* Background / Experience
    * Engineering Manager at Apple
    * Research Scientist at Sandia Labs

# Part 3 - Proposal Details

## 3.1 Details

We propose building an initial iteration of a network analytics data pipeline on Ocean Protocol. It will act as both a demonstration of network analytics using NetworkX and as a jumping off point for a richer hacker discovery system going forward. Three engineers will be involved during the first iteration. Future iterations will expand the project based on demand, feedback, and developer engagement.

## 3.4 Which Ocean-powered data market will data be published on?

Initial deployment will be on Ocean Market. In subsequent rounds we will explore the RoI of forking our own market. We have system administration experience, so it's just a question of where we want to allocate our time during each iteration.

## 3.7.a. Are there any mockups or designs to date?

[TBK: we should have a primitive user interface mockup]

[TBK: we should have a couple network analytics metrics / charts to show]

## 3.7.b. Please give an overview of the technology stack.

[TBK: basic pipeline diagram, at least: Gitcoin API -> raw data -> sparse matrices -> NewtorkX -> UX ]

## 3.9 Project Deliverables - Roadmap

### Any prior work completed thus far? Details?

No. We are doing initial exploration but no significant work in progress yet.

### What is the project roadmap?

1. Milestone 1 (End of Week 1): Gitcoin API calls capable of pulling user, bounty, and grant history.
1. Milestone 2 (End of Week 2): Store the raw data from Milestone 1 in Ocean Protocol space.
1. Milestone 3 (End of Week 3): Generate sparse matrices from the raw data and store in Ocean Protocol space.
1. Milestone 4 (End of Week 4): Generate NetworkX models in Ocean Protocol space.
1. Milestone 5 (End of Week 5): Generate analytical charts and metrics.
1. Milestone 6 (End of Week 6): Expose the UX for querying the network.
1. Milestone 7 (End of week 7): Refine wiki documentation for public consumption and announce.
1. Milestone 8 (End of week 8): Write the grant for Ocean Round 17.

### What is the team's future plans and intentions?

We intend to continue extending the work as long as we still need a tool for finding hackers to work with and as long as others find the work valuable.

## 3.10 Additional Information

I intend to submit a grant to Gitcoin at the same time that I submit this one to Ocean Protocol. We are way under our market rate, which we see as an acceptable investment in our professional development. But the more we can close that gap the easier it will be to continue the work and the easier it will be to attract more of our associates away from Web2.
