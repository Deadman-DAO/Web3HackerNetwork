# Part 1 - Proposal

## Name of Project: *DeadmanDAO Web3 Hacker Network*

## Proposal in one sentence

Create a decentralized network analytics data pipeline for discovering Web3 hackers and understanding the developer-developer multinetwork.

## Description of the project and what problem it is solving

Finding Web3 developers to work with on bounties and hackathons is challenging. You can go to Discord and post, but your message reach will be limited. You can search on LinkedIn, but that data is often stale and only tells you that someone put Web3 terms on their portfolio, not whether they have actually executed. And when you find someone, it is easier to make the connection if you know someone in common to make the introduction.

Developers in Web3 are doing a great job taking an active role in building their networks, but they typically lack the office environment where networking has traditionally been done.

Web3 Hacker Network will provide analytics about the network of active Web3 developers, designers, and managers. 

## Grant Deliverables

* Raw dataset showing Gitcoin user participation in bounties, hackathons, and grants.
* User-User sparse matrix datasets showing strength of relationship along [TBK number of] skill dimensions.
* NetworkX model of the multi-layer network representing the user-user edges in multiple dimensions.
* Sample charts showing [TBK] and [TBK], metrics that express [TBK] and [TBK].
* User experience that takes a Gitcoin ID and a skill and finds the network path to near or strongly connected hackers with that skill.

## Project Category: *Unleash Data*

## Earmark: *New Project*

## What is the final product?

The first iteration final product will include two user experiences. First, people who have worked on Gitcoin projects will be able to enter their login and the skill they are seeking, and will be shown the optimal graph paths to neighbors who have that skill. Second, there will be a periodically updated set of analytical charts and statistics about the Web3 Hacker Network, showing things like [TBK], [TBK], and [TBK].

This will be backed by a decentralized data pipeline. Stage 1 will have raw data about developer history and projects pulled from Gitcoin. Stage 2 will process that data to create a set of developer-developer sparse matrices with the edge weight representing number of shared projects and each matrix representing a particular skill set. Stage 3 will incorporate that data into a NetworkX model representing the multinetwork of Web3 hackers. The UX will use the NetworkX model as its backend.

The longer term final product will evolve organically based on feedback, demand, and developer engagement. Potential features include incorporating data from other Web3 connection services like Discord, richer analytics metrics and charts, more complex querying of the multinetwork model, actively marketing the datasets, enabling users to attach metadata to their node, and partnership outreach to connection services. We will also be considering the economics of running a forked marketplace.

## Which value add criteria are we focusing on? Why do we believe we will do well?

option 1: Usage of Ocean - how well might the project drive usage of Ocean. Measure with e.g. Data Consume Volume, # assets published, TVL (total value locked), Network Revenue, # active users, # funded projects.

option 2: Viability - what is the chance of success of the project

option 3: community active-ness - how active is the team in the community

option 4: Adding value to the overall community - how well does the outcome of the project add value to the Ocean community / ecosystem

## Funding Requested: *$USD* (new team: max $3000)

## Proposal Wallet Address: *[TBK, will my Coinbase-hosted wallet work?]* (must have 500 OCEAN in wallet, must be an Ethereum wallet)

## Have you previously received an OceanDAO Grant?: *No*

## Team Website: [www.DeadmanDAO.com](https://www.deadmandao.com/)

## Discord Handle: *DeadmanBob#7342*

## Project lead full name: *Robert Bushman*

## Project lead email: *[TBK: need to finish setting up deadmandao.com email]*

## Country of Residence: United States of America

# Part 2 - Team

## 2.1 Core Team

### Robert Bushman

* Role: Project Manager, Developer
* Relevant Credentials:
    * LinkedIn: [TBK]
* Background / Experience:
    * L6 SDE / L6 SDM at Amazon (big data & data science)
    * Big Data Architect at Choice Hotels
    * Senior Engineer at Apple

### Matt Enke

* Role: Developer
* Relevant Credentials
    * [TBK]
* Background / Experience
    * System Architect and Engineer: US DoD Warehouse Automation

## Part 2.2 Advisors

### Tom Moore

* Role: Network Theory Advisor
* Relevant Credentials
    * [TBK]
* Background / Experience
    * [TBK: Senior Scientist? at Apple]
    * [TBK: Social Network and Contagion Model Analyst at Sandia Labs]

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
